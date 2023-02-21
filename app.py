from flask import Flask, request, render_template,send_from_directory,make_response
from werkzeug.utils import secure_filename
import paramiko

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('/dist/index.html')

@app.route('/js/<path:filename>')
def js_static(filename):
    return send_from_directory('templates/dist/js', filename)

@app.route('/<path:filename>')
def favicon_static(filename):
    return send_from_directory('templates/dist/', filename)

@app.route('/fonts/<path:filename>')
def fonts_static(filename):
    return send_from_directory('templates/dist/fonts', filename)

@app.route('/css/<path:filename>')
def css_static(filename):
    return send_from_directory('templates/dist/css', filename)

@app.route('/check',methods=['GET'])
def check():
    ip = request.args.get('ip')
    username = request.args.get('username')
    password = request.args.get('password')

    # 远程连接服务器功能
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username=username, password=password)
        result = "连接服务器成功！"
    except:
        result = "你输入的服务ip或者密码有误，无法连接到服务器"
        ssh.close()
    return result

@app.route('/upload',methods=['POST'])
def upload():
    if request.method == 'POST':
        ip = request.form.get('ip')
        username = request.form.get('username')
        password = request.form.get('password')
        file = request.files.get('file')
        if file:
            # 本地存储好再上传
            filename = secure_filename(file.filename)
            file.save(filename)

            # 远程连接服务器功能
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password)

            # 上传文件到服务器功能
            try:
                with ssh.open_sftp() as sftp:
                    sftp.put(filename, '/tmp/' + filename)
                    # 校验是否上传成功
                    stdin, stdout, stderr = ssh.exec_command('ls /tmp/' + file.filename)
                    file_exists = (file.filename in stdout.read().decode('utf-8'))
                    if file_exists:
                        result = '上传'+file.filename+'成功！'
            except Exception as e:
                result = '上传'+file.filename+'失败！' + str(e)

            sftp.close()
            ssh.close()

    return result

@app.route('/pod', methods=['GET'])
def get_pod():
    ip = request.args.get('ip')
    username = request.args.get('username')
    password = request.args.get('password')
    namespaces = request.args.get('namespaces')


    # 远程连接服务器功能
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username=username, password=password)
    except:
        return '你输入的服务ip或者密码有误无法连接到服务器'

    # 执行命令
    try:
        stdin, stdout, stderr = ssh.exec_command('kubectl get pod -n' + namespaces)
        result = stdout.read().decode('utf-8')
        if result.strip() == '':
            result = '该命名空间下没有pod，请输入正确命名空间'
    except:
        result = '命名空间有误，或者不存在'

    response = make_response(result)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response


@app.route('/map',methods=['POST'])
def map():
    if request.method == 'POST':
        ip = request.form.get('ip')
        username = request.form.get('username')
        password = request.form.get('password')
        container_name = request.form.get('container_name')
        container_path = request.form.get('container_path')
        namespaces = request.form.get('namespaces')
        file = request.files.get('file')

        # 远程连接服务器功能
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(ip, username=username, password=password)
        except:
            return '你输入的服务ip或者密码有误无法连接到服务器'

        # 复制文件到 Docker 容器
        # stdin, stdout, stderr = ssh.exec_command('docker cp /tmp/' + file.filename + ' container_name:' + container_name + ':' + container_path)
        # result = stdout.read() + stderr.read()
        #     if not result:
        #         result = '复制文件成功'
        #     else:
        #         return result


        #复制文件到 K8S 容器
        try:
            if not container_path.startswith('/'):
                return '容器路径必须以 / 开头'
            stdin, stdout, stderr = ssh.exec_command('kubectl cp /tmp/' + file.filename + ' ' + container_name + ':' + container_path + ' -n ' + namespaces)
            result = stdout.read().decode() + stderr.read().decode()
            if not result:
                result = '复制文件成功'
            else:
                return result
        except:
            result = '命名空间有误'

        if not container_path.startswith('/'):
            result = '容器路径必须以 / 开头'

    return result

if __name__ == '__main__':
    # app.run(debug=True)
    app.run()