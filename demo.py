import subprocess

def check_ping(ip_address):
    # 使用ping命令检查IP是否可达
    command = ['ping', '-n', '1', ip_address]  # 在Linux/MacOS上使用'-c'参数，在Windows上使用'-n'参数
    try:
        # 执行ping命令
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 如果ping成功，则返回True
        return True
    except subprocess.CalledProcessError:
        # 如果ping失败，则返回False
        return False

# 示例用法
ip_address = '192.168.2.186'
if check_ping(ip_address):
    print(f"{ip_address} is reachable.")
else:
    print(f"{ip_address} is not reachable.")

