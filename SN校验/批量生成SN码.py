# 批量生成SN码 2025/5/14
import zlib

# 计算CRC16校验码
def hash_crc16(sn: str) -> str:
    return f"{zlib.crc32((sn + '95C8').encode()) & 0xFFFF:04X}"

# 生成设备SN
def generate_sn(name: str = "", pid: str = "") -> str:
    return f"{name}{pid}{hash_crc16(f'{name}{pid}')}"

# 主函数
def main():
    # 定义基础名称
    base_name = "GF225"

    # 定义需要计算的PID列表
    pids = [
        # "1001", "1002", "0003", "1004", "1005",
        # "1006", "0002", "1008", "1009", "1010", "1011", "1012", "0008", "0009", "0010",
        # "1016", "1017", "1018", "1019", "1020", "0006", "1022", "1023", "1024", "1025","1026", "1027", "1028", "0014", "0015",
        # "1031", "1032", "1033", "1034", "1035","1036",
        # "1037", "1038", "1039", "1040", "1041",
        "9999", "9001", "9002", "9003","9004", "9005", "9006", "9007", "9008", "9009", "9010", "9011", "9012", "9013","9014", "9015"
    ]

    print("-" * 30)
    for pid in pids:
        sn = generate_sn(base_name, pid)
        print(f"{pid}\t\t{sn}")

    print("-" * 30)
    for pid in pids:
        sn = generate_sn(base_name, pid)
        print(f"{sn}")

if __name__ == "__main__":
    main()    