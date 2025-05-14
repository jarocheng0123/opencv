# 相机SN校验程序
import zlib

# 计算CRC16校验码
def hash_crc16(sn: str) -> str:
    return f"{zlib.crc32((sn + '95C8').encode()) & 0xFFFF:04X}"

# 生成设备SN
def generate_sn(name: str = "", pid: str = "") -> str:
    return f"{name}{pid}{hash_crc16(f'{name}{pid}')}"

# 定义设备信息
serial = generate_sn("GF225", "9001")

if __name__ == "__main__":
    print(f"生成的设备SN: {serial}")