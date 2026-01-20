import zlib


def encrypt_text(text, use_compression=True):
    """
    将文本加密为"结婚"编码（支持压缩以提高信息熵）
    规则：结=1, 婚=0

    参数:
        text: 要加密的文本字符串
        use_compression: 是否使用压缩（默认True，可大幅减少长度）

    返回:
        加密后的字符串（由"结"和"婚"组成）
    """
    if not isinstance(text, str):
        raise TypeError("输入必须是字符串类型")

    # 将文本转换为UTF-8字节序列
    bytes_data = text.encode('utf-8')

    # 如果启用压缩，先压缩数据
    if use_compression:
        bytes_data = zlib.compress(bytes_data)

    # 将每个字节转换为8位二进制
    binary_str = ''.join(format(byte, '08b') for byte in bytes_data)

    # 将二进制转换为"结婚"编码
    encrypted = binary_str.replace('1', '结').replace('0', '婚')

    # 添加标记位表示是否压缩（第一个字符）
    marker = '结' if use_compression else '婚'

    return marker + encrypted


def decrypt_text(encrypted):
    """
    将"结婚"编码解密为原文本（自动识别是否压缩）
    规则：结=1, 婚=0

    参数:
        encrypted: 加密后的字符串（由"结"和"婚"组成）

    返回:
        解密后的原始文本
    """
    if not isinstance(encrypted, str) or len(encrypted) < 1:
        raise ValueError("加密文本必须是非空字符串")

    # 读取标记位判断是否压缩
    is_compressed = (encrypted[0] == '结')
    encrypted_data = encrypted[1:]

    # 将"结婚"编码转换为二进制
    binary_str = encrypted_data.replace('结', '1').replace('婚', '0')

    # 将二进制转换回字节
    bytes_data = []
    for i in range(0, len(binary_str), 8):
        byte = binary_str[i:i+8]
        if len(byte) == 8:
            bytes_data.append(int(byte, 2))

    bytes_result = bytes(bytes_data)

    # 如果是压缩的，先解压
    if is_compressed:
        try:
            bytes_result = zlib.decompress(bytes_result)
        except zlib.error:
            raise ValueError("解压缩失败，请检查加密数据是否完整")

    # 将字节序列解码为UTF-8文本
    try:
        return bytes_result.decode('utf-8')
    except UnicodeDecodeError:
        raise ValueError("解码失败，请检查加密数据是否完整")


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("压缩模式 vs 非压缩模式对比")
    print("=" * 60)
    
    test_text = "你好世界，这是一个测试文本。Hello World! 人工智能AI技术发展迅速。"
    
    # 非压缩模式
    encrypted_raw = encrypt_text(test_text, use_compression=False)
    decrypted_raw = decrypt_text(encrypted_raw)
    
    # 压缩模式
    encrypted_compressed = encrypt_text(test_text, use_compression=True)
    decrypted_compressed = decrypt_text(encrypted_compressed)
    
    print(f"\n原文: {test_text}")
    print(f"原文长度: {len(test_text)} 字符\n")
    
    print(f"【非压缩模式】")
    print(f"加密长度: {len(encrypted_raw)} 字符")
    print(f"压缩率: {len(encrypted_raw) / len(test_text):.2f}x")
    print(f"解密正确: {'✓' if test_text == decrypted_raw else '✗'}\n")
    
    print(f"【压缩模式】")
    print(f"{encrypted_compressed}")
    print(f"加密长度: {len(encrypted_compressed)} 字符")
    print(f"压缩率: {len(encrypted_compressed) / len(test_text):.2f}x")
    print(f"解密正确: {'✓' if test_text == decrypted_compressed else '✗'}")
    print(f"相比非压缩节省: {(1 - len(encrypted_compressed) / len(encrypted_raw)) * 100:.1f}%\n")
    
    # 更多测试
    print("=" * 60)
    print("更多测试用例（压缩模式）")
    print("=" * 60)
    
    test_cases = [
        "Hello",
        "你好世界",
        "Python编程",
        "123456",
        "AI人工智能",
        "重复重复重复重复重复重复重复重复",
        "The quick brown fox jumps over the lazy dog. " * 3
    ]
    
    for test in test_cases:
        enc = encrypt_text(test, use_compression=True)
        dec = decrypt_text(enc)
        ratio = len(enc) / len(test)
        print(f"{test[:30]:30} | 原{len(test):3} -> 密{len(enc):4} | 比率{ratio:.2f}x | {('✓' if test == dec else '✗')}")