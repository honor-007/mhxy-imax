import subprocess


def motherboardUUID():
    # 执行命令并获取输出
    result = subprocess.run(['wmic', 'csproduct', 'get', 'UUID'], capture_output=True, text=True)

    # 输出包含了很多额外的信息，我们需要从中提取UUID
    # 注意：这个简单的例子假设UUID是输出的第一行（在实际情况中可能不是这样）
    # 更健壮的方法可能需要解析整个输出
    lines = result.stdout.splitlines()
    if lines:
        uuid_value = lines[2]  # 假设UUID在第二行（第一行通常是标题）
        print(f"UUID: {uuid_value}")
        return uuid_value
    else:
        print("没有找到UUID信息")
        return None


def BIOSSerialNumber():
    # 执行命令并获取输出
    result = subprocess.run(['wmic', 'bios', 'get', 'serialnumber'], capture_output=True, text=True)

    # 输出包含了很多额外的信息，我们需要从中提取UUID
    # 注意：这个简单的例子假设UUID是输出的第一行（在实际情况中可能不是这样）
    # 更健壮的方法可能需要解析整个输出
    lines = result.stdout.splitlines()
    if lines:
        uuid_value = lines[2]  # 假设UUID在第二行（第一行通常是标题）
        print(f"BIOS SerialNumber: {uuid_value}")
        return uuid_value
    else:
        print("没有找到BIOS SerialNumber信息")
        return None

def test():
    print("11")

if __name__ == "__main__":
    BIOSSerialNumber()
