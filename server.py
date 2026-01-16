def encrypt_text(text):
    """
    将文本加密为"结婚"编码
    规则：结=1, 婚=0
    
    参数:
        text: 要加密的文本字符串
    
    返回:
        加密后的字符串（由"结"和"婚"组成）
    """
    # 将文本转换为UTF-8字节序列
    bytes_data = text.encode('utf-8')
    
    # 将每个字节转换为8位二进制
    binary_str = ''.join(format(byte, '08b') for byte in bytes_data)
    
    # 将二进制转换为"结婚"编码
    encrypted = binary_str.replace('1', rule[0]).replace('0', rule[1])
    
    return encrypted


def decrypt_text(encrypted):
    """
    将"结婚"编码解密为原文本
    规则：结=1, 婚=0
    
    参数:
        encrypted: 加密后的字符串（由"结"和"婚"组成）
    
    返回:
        解密后的原始文本
    """
    # 将"结婚"编码转换为二进制
    binary_str = encrypted.replace(rule[0], '1').replace(rule[1], '0')
    
    # 将二进制转换回字节
    bytes_data = []
    for i in range(0, len(binary_str), 8):
        byte = binary_str[i:i+8]
        if len(byte) == 8:  # 确保是完整的字节
            bytes_data.append(int(byte, 2))
    
    # 将字节序列解码为UTF-8文本
    return bytes(bytes_data).decode('utf-8')

rule="结婚"

# 使用示例
if __name__ == "__main__":
    # 测试加密
    original_text = "hello world"
    print(f"原文: {original_text}")
    
    # 加密
    encrypted = encrypt_text(original_text)
    print(f"加密后: {encrypted}")
    print(f"加密长度: {len(encrypted)} 字符")
    
    # 解密
    decrypted = decrypt_text(encrypted)
    print(f"解密后: {decrypted}")
    
    # 验证
    print(f"\n验证: {original_text == decrypted}")
    
    # 更多测试
    print("\n" + "="*50)
    test_cases = ["Hello", "Python编程", "123456", "https://blog.csdn.net/2401_84494441/article/details/148765943"]
    for test in test_cases:
        enc = encrypt_text(test)
        dec = decrypt_text(enc)
        print(f"{test} -> 长度{len(enc)} -> {dec} ({'✓' if test == dec else '✗'})")