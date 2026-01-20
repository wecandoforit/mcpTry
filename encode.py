import heapq
from collections import Counter
import pickle
import base64


class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman_tree(text):
    """构建哈夫曼树"""
    if not text:
        return None

    # 统计字符频率
    frequency = Counter(text)

    # 创建优先队列
    heap = [HuffmanNode(char, freq) for char, freq in frequency.items()]
    heapq.heapify(heap)

    # 构建哈夫曼树
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)

        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right

        heapq.heappush(heap, merged)

    return heap[0] if heap else None


def build_codes(root, current_code="", codes=None):
    """从哈夫曼树构建编码表"""
    if codes is None:
        codes = {}

    if root is None:
        return codes

    # 叶子节点
    if root.char is not None:
        codes[root.char] = current_code if current_code else "0"
        return codes

    # 递归构建
    build_codes(root.left, current_code + "0", codes)
    build_codes(root.right, current_code + "1", codes)

    return codes


def encrypt_text(text):
    """
    使用哈夫曼编码将文本加密为"结婚"编码
    规则：结=1, 婚=0

    参数:
        text: 要加密的文本字符串

    返回:
        加密后的字符串（由"结"和"婚"组成）
    """
    if not isinstance(text, str):
        raise TypeError("输入必须是字符串类型")

    if not text:
        return "婚结"  # 使用两个字符表示空字符串，第一位表示非压缩，第二位是占位符

    # 构建哈夫曼树和编码表
    root = build_huffman_tree(text)
    if root is None:
        return "婚结"  # 空文本的情况

    codes = build_codes(root)

    # 使用哈夫曼编码压缩文本
    encoded_bits = ''.join(codes[char] for char in text)

    # 将编码表序列化
    codes_serialized = pickle.dumps(codes)
    codes_base64 = base64.b64encode(codes_serialized).decode('ascii')

    # 将编码表转为二进制
    codes_bits = ''.join(format(ord(c), '08b') for c in codes_base64)

    # 编码表长度（32位）
    codes_length = format(len(codes_bits), '032b')

    # 组合：编码表长度 + 编码表 + 编码后的文本
    full_bits = codes_length + codes_bits + encoded_bits

    # 填充到8的倍数
    padding = (8 - len(full_bits) % 8) % 8
    full_bits += '0' * padding

    # 添加填充长度信息（3位，最多7）
    padding_info = format(padding, '03b')
    full_bits = padding_info + full_bits

    # 转换为"结婚"编码
    encrypted = full_bits.replace('1', '结').replace('0', '婚')

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
    if not isinstance(encrypted, str) or len(encrypted) < 1:
        raise ValueError("加密文本必须是非空字符串")

    if encrypted == "婚结":
        return ""  # 空字符串的特殊表示

    # 转换回二进制
    bits = encrypted.replace('结', '1').replace('婚', '0')

    # 读取填充信息
    if len(bits) < 3:
        raise ValueError("加密数据格式错误")
    padding = int(bits[:3], 2)
    bits = bits[3:]

    # 移除填充
    if padding > 0:
        if len(bits) < padding:
            raise ValueError("加密数据格式错误")
        bits = bits[:-padding]

    # 读取编码表长度
    if len(bits) < 32:
        raise ValueError("加密数据格式错误")
    codes_length = int(bits[:32], 2)
    bits = bits[32:]

    # 提取编码表和编码后的文本
    if len(bits) < codes_length:
        raise ValueError("加密数据格式错误")
    codes_bits = bits[:codes_length]
    encoded_bits = bits[codes_length:]

    # 将编码表转回字符串
    codes_chars = []
    for i in range(0, len(codes_bits), 8):
        byte = codes_bits[i:i+8]
        if len(byte) == 8:
            codes_chars.append(chr(int(byte, 2)))
    codes_base64 = ''.join(codes_chars)

    try:
        # 反序列化编码表
        codes_serialized = base64.b64decode(codes_base64)
        codes = pickle.loads(codes_serialized)
    except Exception:
        raise ValueError("编码表解析失败，请检查加密数据是否完整")

    # 构建反向编码表
    reverse_codes = {v: k for k, v in codes.items()}

    # 解码文本
    decoded_text = []
    current_code = ""
    for bit in encoded_bits:
        current_code += bit
        if current_code in reverse_codes:
            decoded_text.append(reverse_codes[current_code])
            current_code = ""

    return ''.join(decoded_text)

# 使用示例
if __name__ == "__main__":
    print("=" * 70)
    print("哈夫曼编码 + 结婚加密")
    print("=" * 70)
    
    test_cases = [
        '''以前总怪父母那么努力还没让我过好日子，直到自己扛起养家的担子才懂：成年人的世界，光是活着，就已经要拼尽全力。
小时候我就知道家里很穷，穷到什么程度呢？小时候总会有邻居家的叔叔阿姨问：你想不想自己的爸妈呀？说实话，就是一直跟着爷爷奶奶生活，一年也没见过爸妈几次，谈不上想与不想。
日子苦到放学要割猪草、下雨要光脚回家，有时候也会抱怨父母外出打工不陪我、没给我好生活。
直到我自己现在成为了妈妈，才突然读懂原来他们拼尽所有，也只够后给我勉强的生活件。
那时候的我，是典型的留守儿童。从记事起，爸妈就在外地打工，家里只剩我和爷爷奶奶和姐姐妹妹。童年没有玩具也没有零食，只有干不完的农活和数不尽的窘迫。
每天放学后，第一件事不是写作业，而是拿着竹筐去割猪草，直到割满一筐，才急冲冲地回家。周末也是要么帮着喂猪喂鸡，要么跟着奶奶去地里锄草，裤脚永远沾满泥土，鞋子上全是泥点，童年基本上就是玩泥巴度过的。
鞋子的窘迫，更是刻在骨子里的记忆。一年四季就两双拿得出手的鞋：一双单鞋，一双棉鞋。每周五放学，我都要把单鞋洗干净，晾在风最大的地方，盼着鞋子快点干，生怕周一穿不上干鞋。
那时候村里没有水泥路，全是坑坑洼洼的土路，最不喜欢的就是下雨天。一旦下雨，路面又湿又滑，鞋子碰到水就湿透了。为了不让鞋子湿掉，下雨天直接把鞋子脱下来揣在怀里，光着脚往家走，脚底被石子硌得生疼，也顾不上了，比起冻脚，更怕鞋子坏了再也没得穿。
而小时候的愿望就是去照相馆拍照片，看着邻居家小朋友有自己的照片就特别羡慕。直到五年级那年，叔叔让婶婶给他寄一张堂妹的照片，婶婶就把我们姐妹几个，特意带去镇上的照相馆拍了一张合照，那是我童年唯一一张在照相馆拍的照片，照片上的我们穿着洗得发白的衣服，头发梳得整整齐齐，笑得格外灿烂。
总以为等爸妈挣够钱了，就能经常带我拍照，后来才知道，他们连自己的生活费都要省着花，根本没多余的钱满足我。
那时候的我，不懂为什么爸妈一年到头不回家，不懂为什么我们家总是比别人穷，不懂为什么他们不能像别的父母一样陪在我身边。甚至偶尔会偷偷抱怨：为什么别人的爸妈有本事，能给孩子好生活，而我的爸妈却只能让我过苦日子？有时候顺嘴跟爸妈说这些时，他们都会瞬间变脸色，那时候不懂这份情绪背后的心情，直到自己成家生子，才突然恍然大悟。
如今自己成了妈妈，才懂当年父母的难有多沉。每天照顾11个月的宝宝，熬到深夜喂完奶，还要打开电脑写自媒体，每月账单接踵而至，奶粉、尿不湿、家用，几千块钱转眼就花光，明明没闲着，却总怕赚不够钱给宝宝好生活。
以前上班时，早出晚归、节假日无休，扛着业绩压力，拼命工作，8年熬过来不敢有丝毫懈怠，可即便如此，失业后还是瞬间陷入迷茫焦虑。
那天给宝宝买奶粉，看着结账时的账单，突然想起小时候爸妈过年给我买新衣服的场景。他们在外省吃俭用，把攒下来的钱全寄回家，自己舍不得买一件新衣服，却愿意把最好的都给我们姐妹。
现在回想起爸妈在外打工的辛苦，我抱怨没新衣服穿，他们却在工地里、工厂里拼尽全力，只为让我少吃点苦；我盼着他们陪伴，他们却要先赚钱养家，才能谈陪伴的奢侈。
成年人的世界，从来没有两全其美。
小时候总以为，日子苦是因为爸妈不够努力；长大后才懂，穷从来不是因为不努力，而是谋生本来就是一场艰难的战役。
当年靠着爸妈撑起一个家，养活我和姐姐还有爷爷奶奶，已经拼尽了所有力气。
以前总盼着长大，以为长大就能逃离苦日子，就能给家人好生活。如今才懂，成年人的世界，从来就不容易。光是带好宝宝、做好事业、撑起小家，就已经要拼尽全力。那些当年觉得父母不够好的地方，全是他们用汗水和辛苦换来的。
现在的我，不再追求大富大贵，只愿宝宝健康成长，家人平安顺遂。自己能在自媒体路上慢慢努力，既能陪伴宝宝，也能实现自我价值，把当年父母没享过的福，一点点补回来。
或许我们都是普通人，拼尽全力也只是过着平凡的日子。
原来长大后的我们，终究会活成父母当年的样子，一边为生活奔波劳碌，一边拼尽全力给家人最好的生活。
也终于读懂，父母当年的穷，藏着我没见过的拼尽全力；他们当年的爱，比我想象中更沉重、更伟大。'''
    ]
    
    print(f"\n{'原文':<40} | {'原长':>4} | {'密长':>6} | {'比率':>6} | {'状态':^4}")
    print("-" * 70)
    
    for test in test_cases:
        encrypted = encrypt_text(test)
        decrypted = decrypt_text(encrypted)
        ratio = len(encrypted) / len(test) if len(test) > 0 else 0
        status = '✓' if test == decrypted else '✗'
        
        display_text = test[:38] + '..' if len(test) > 40 else test
        print(f"{display_text:<40} | {len(test):4} | {len(encrypted):6} | {ratio:5.2f}x | {status:^4}")
    
    # 详细示例
    print("\n" + "=" * 70)
    print("详细示例：高频字符的优势")
    print("=" * 70)
    
    example = test_cases[0]
    encrypted = encrypt_text(example)
    decrypted = decrypt_text(encrypted)
    
    print(f"\n原文: {example}")
    print(f"原文长度: {len(example)} 字符")
    
    # 显示字符频率
    freq = Counter(example)
    print(f"\n字符频率:")
    for char, count in sorted(freq.items(), key=lambda x: -x[1]):
        print(f"  '{char}': {count} 次")
    
    # 显示编码信息
    root = build_huffman_tree(example)
    codes = build_codes(root)
    print(f"\n哈夫曼编码:")
    for char in sorted(codes.keys()):
        print(f"  '{char}': {codes[char]} ({len(codes[char])} 位)")
    
    print(f"\n加密后长度: {len(encrypted)} 个'结婚'字符")
    print(f"压缩比率: {len(encrypted) / len(example):.2f}x")
    print(f"解密验证: {'✓ 成功' if example == decrypted else '✗ 失败'}")
    
    # 理论分析
    avg_bits = sum(len(codes[c]) * freq[c] for c in freq) / len(example)
    print(f"\n理论平均编码长度: {avg_bits:.2f} 位/字符")
    print(f"相比固定8位编码节省: {(1 - avg_bits/8) * 100:.1f}%")