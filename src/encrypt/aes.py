# import base64
# from Crypto.Cipher import AES
# from Crypto.Random import get_random_bytes
# from Crypto.Util.Padding import pad, unpad
#
#
# class AesEncrypt:
#     def __init__(self, key):
#         self.key = key  # 定义并初始化name属性
#
#     def aes_encrypt(self, plaintext):
#         # 生成随机的初始化向量
#         iv_bytes = get_random_bytes(AES.block_size)
#
#         # 创建AES cipher对象，使用CBC模式
#         cipher = AES.new(self.key, AES.MODE_CBC, iv_bytes)
#
#         # 对数据进行padding，然后加密
#         message_bytes_encrypted = cipher.encrypt(pad(plaintext, AES.block_size))
#
#         # 将iv和密文拼接，然后base64编码，以便传输
#         iv = base64.b64encode(iv_bytes).decode('utf-8')
#         encrypted = base64.b64encode(message_bytes_encrypted).decode('utf-8')
#         result = iv + "_" + encrypted
#         return result
#
#     def aes_decrypt(self, encrypted_text):
#         # 分离出IV和密文
#         iv_base64, encrypted_base64 = encrypted_text.split('_')
#
#         # 对IV和密文进行Base64解码
#         iv_bytes = base64.b64decode(iv_base64)
#         encrypted_bytes = base64.b64decode(encrypted_base64)
#
#         # 创建AES cipher对象，使用CBC模式
#         cipher = AES.new(self.key, AES.MODE_CBC, iv_bytes)
#
#         # 对密文进行解密
#         decrypted_bytes = cipher.decrypt(encrypted_bytes)
#
#         # 对解密后的数据进行去填充
#         decrypted_text = unpad(decrypted_bytes, AES.block_size)
#         # print("解密结果:", decrypted_text.decode('utf-8'))
#         return decrypted_text.decode('utf-8')
#
# # 测试代码
# # key = b'Sixteensbyteskey'
# # plaintext = b"hello world"
# # encrypted = aes_encrypt(plaintext, key)
# # print("加密结果:", encrypted)
#
# # aes_util = AesEncrypt(key)
# # encrypted = 'igEoJj1zcfxxMlspQ1okSg==_tK9iqmAoDLWqUwiFMfcdvm7OUjp6Ho2JAn6+P8QM4uQ='
# # aes_util.aes_decrypt(encrypted)
