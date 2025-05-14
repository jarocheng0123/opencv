# 在Ubuntu 运行：需使用 pip3 安装依赖
# 在Windows运行：需使用 pip  安装依赖
# -------------------- 导入依赖 --------------------
import re
import os
import sys
import wmi
import cv2
import time
import winreg
import psutil
import platform
import importlib
import subprocess
from threading import Thread, Event
from PyCameraList.camera_device import list_video_devices

# ██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
# -------------------- 用户配置区 --------------------
# 摄像头名称
TARGET_CAMERA_NAME = "ViTai"
# 需要关闭的进程
AMCAP_EXE_NAME = "amcap+v3.0.9.exe"
# 摄像头初始化时间
CAMERA_INIT_DELAY = 1
# 显示摄像头画面
SHOW_CAMERA_WINDOW = True
# 程序退出延时
MAIN_DELAY = 5
# 读取参数等待时间
PARAM_READ_DELAY = 1

# -------------------- 摄像头参数配置 --------------------
class CameraConfig:
    PARAM_INFO = {
        # 默认值#########################################################################################################
        "Contrast": {"chinese_name": "对比度", "value": 39, "range": (0, 100), "cv_constant": cv2.CAP_PROP_CONTRAST},
        "Hue": {"chinese_name": "色调调节", "value": 0, "range": (-180, 180), "cv_constant": cv2.CAP_PROP_HUE},
        "Saturation": {"chinese_name": "饱和度", "value": 72, "range": (0, 100),"cv_constant": cv2.CAP_PROP_SATURATION},
        "Sharpness": {"chinese_name": "清晰度", "value": 75, "range": (0, 100), "cv_constant": cv2.CAP_PROP_SHARPNESS},
        "Gamma": {"chinese_name": "伽玛校正", "value": 300, "range": (100, 500), "cv_constant": cv2.CAP_PROP_GAMMA},
        "Gain": {"chinese_name": "增益", "value": 64, "range": (1, 128), "cv_constant": cv2.CAP_PROP_GAIN},
        "Focus": {"chinese_name": "焦点", "value": 68, "range": (0, 1023), "auto_support": True,"cv_constant": cv2.CAP_PROP_FOCUS},
        "Exposure": {"chinese_name": "曝光值", "value": -9, "range": (-14, 0), "cv_constant": cv2.CAP_PROP_EXPOSURE},
        # 自动模式########################################################################################################
        "AutoWhiteBalance": {"chinese_name": "自动白平衡模式", "value": 0, "range": (0, 1),"cv_constant": cv2.CAP_PROP_AUTO_WB},
        "AutoFocus": {"chinese_name": "自动对焦", "value": 1, "range": (0, 1), "cv_constant": cv2.CAP_PROP_AUTOFOCUS},
        "AutoExposure": {"chinese_name": "自动曝光模式", "value": 0, "range": (0, 1),"cv_constant": cv2.CAP_PROP_AUTO_EXPOSURE},
        # 设置固定值######################################################################################################
        "Brightness": {"chinese_name": "亮度调节", "value": -64, "range": (-64, 64),"cv_constant": cv2.CAP_PROP_BRIGHTNESS},
        "WhiteBalance": {"chinese_name": "白平衡色温", "value": 6000, "range": (2800, 6500),"cv_constant": cv2.CAP_PROP_WHITE_BALANCE_BLUE_U},
        # 不支持参数######################################################################################################
        # "NoiseReduction": {"chinese_name": "降噪强度", "value": 50, "range": (0, 100), "cv_constant": None},
        # "Zoom": {"chinese_name": "数字变焦", "value": 0, "range": (0, 100), "cv_constant": cv2.CAP_PROP_ZOOM},
        # "FrameRate": {"chinese_name": "帧率", "value": 30, "range": (1, 60), "cv_constant": cv2.CAP_PROP_FPS},
        # "ResolutionWidth": {"chinese_name": "分辨率宽度", "value": 1920, "range": (640, 3840), "cv_constant": cv2.CAP_PROP_FRAME_WIDTH},
        # "ResolutionHeight": {"chinese_name": "分辨率高度", "value": 1080, "range": (480, 2160), "cv_constant": cv2.CAP_PROP_FRAME_HEIGHT},
        # "ColorMode": {"chinese_name": "色彩模式", "value": 0, "range": (0, 2), "cv_constant": None}
    }

    # 查询状态
    READ_PARAMS = {
        info["chinese_name"]: info["cv_constant"]
        for param, info in PARAM_INFO.items()
        if info["chinese_name"] in ["自动白平衡模式", "亮度调节", "白平衡色温"]
    }

# 不支持调节参数说明
def print_unsupported_param_info():
    print("\033[93m")
    print(f"{'=' * 46}初始化完成{'=' * 46}")
    print("降噪强度:   可能摄像头硬件没有内置降噪功能或驱动不支持调节降噪强度")
    print("数字变焦:   可能需要光学变焦镜头并通过物理控制，或摄像头本身不支持数字变焦")
    print("帧率:      可能摄像头硬件不支持指定的帧率范围或驱动未提供设置接口")
    print("分辨率宽度: 可能摄像头硬件不支持指定的分辨率宽度或驱动未提供设置接口")
    print("分辨率高度: 可能摄像头硬件不支持指定的分辨率高度或驱动未提供设置接口")
    print("色彩模式:   可能摄像头硬件不支持多种色彩模式或驱动未提供设置接口")
    print("\033[0m")

# ██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████

# 在全局作用域定义退出事件
exit_event = Event()

# -------------------静默依赖安装 --------------------
def silent_install_deps():
    required = {
        "windows": [
            ("opencv-python", "cv2"),
            ("pycameralist", "PyCameraList.camera_device"),
            ("psutil", "psutil"),
            ("wmi", "wmi"),
        ],
        "linux": [
            ("opencv-python", "cv2"),
            ("pycameralist", "PyCameraList.camera_device"),
            ("psutil", "psutil"),
            ("python3-wmi", "wmi", "apt"),
        ],
    }

    current_platform = platform.system().lower()
    python_exe = sys.executable
    installed = True

    # 处理平台特定依赖
    if current_platform not in required:
        print(f"\033[31m不支持的平台: {current_platform}\033[0m")
        return False

    for pkg_info in required[current_platform]:
        pkg_name = pkg_info[0]
        mod_name = pkg_info[1]

        # 处理apt安装包
        if len(pkg_info) > 2 and pkg_info[2] == "apt":
            if os.system(f"dpkg -l | grep -q {pkg_name}") != 0:
                print(f"正在安装系统包: {pkg_name}")
                os.system(f"sudo apt install -y {pkg_name}")
            continue

        # 检查Python包
        try:
            importlib.import_module(mod_name)
        except ImportError:
            installed = False
            print(f"正在安装 {pkg_name}...")
            cmd = [
                python_exe,
                "-m",
                "pip",
                "install",
                pkg_name,
                "-i",
                "https://pypi.tuna.tsinghua.edu.cn/simple",
                "--quiet",
                "--disable-pip-version-check",
            ]
            subprocess.run(cmd, check=True)

    return installed

# -------------------- 硬件信息模块 --------------------
def _get_reg_value(key, value_name):
    try:
        return winreg.QueryValueEx(key, value_name)[0]
    except:
        return "N/A"

def get_camera_hardware_info():
    c = wmi.WMI()
    devices = []
    for item in c.Win32_PnPEntity(ClassGuid="{ca3e7ab9-b4c3-4ae6-8251-579ef933890f}"):
        if not item.DeviceID:
            continue

        # 解析设备ID
        vid_pid = re.findall(
            r"VID_([0-9A-F]{4})&PID_([0-9A-F]{4})", item.DeviceID, re.I)
        vid, pid = vid_pid[0] if vid_pid else ("N/A", "N/A")
        # 读取注册表信息
        reg_path = item.DeviceID.replace("\\", "#") + "#"
        try:
            with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    f"SYSTEM\\CurrentControlSet\\Enum\\{reg_path}",
            ) as key:
                serial = _get_reg_value(key, "SerialNumber")
                manufacturer = _get_reg_value(key, "Manufacturer")
        except:
            serial = manufacturer = "N/A"
        devices.append(
            {
                "name": item.Name or "未知设备",
                "vid": vid,
                "pid": pid,
                "serial": serial,
                "manufacturer": manufacturer,
            }
        )

    return devices

# -------------------- 系统报告模块 --------------------
# 文本居中显示
def center_text(text, width):
    return text.center(width, " ")

# 生成结构化系统报告
def generate_system_report():
    report = []

    # 硬件信息
    hw_info = []
    if platform.system() == "Windows":
        try:
            hw_info = get_camera_hardware_info()
        except Exception as e:
            report.append(f"[警告] 硬件信息获取失败: {str(e)}")

    # 设备列表
    try:
        devices = list_video_devices()
    except Exception as e:
        devices = []
        report.append(f"[错误] 设备枚举失败: {str(e)}")

    # 构建报告
    border = "=" * 100
    report.insert(
        0,
        f"\033[33m\n{border}\n{center_text(' 设备初始化报告 ', 100)}\n{border}\033[0m",
    )

    if hw_info:
        report.append(
            "{:<5} | {:<27} | {:<8} | {:<6} | {:<12} | {}".format(
                "序号", "设备名称", "VID", "PID", "序列号", "制造商"
            )
        )
        report.append("-" * 100)

        # 分离目标设备和非目标设备
        target_devices = []
        non_target_devices = []
        # 初始化序号计数器
        target_device_index = 1

        for device in hw_info:
            name = device["name"]
            vid = device["vid"]
            pid = device["pid"]
            serial = device["serial"]
            manufacturer = device["manufacturer"]

            if TARGET_CAMERA_NAME.lower() in name.lower():
                # 目标设备的序号从1开始
                target_devices.append(
                    (target_device_index, name, vid, pid, serial, manufacturer)
                )
                target_device_index += 1
            else:
                # 非目标设备的序号为0
                non_target_devices.append((0, name, vid, pid, serial, manufacturer))
                # 打印非目标设备
        for idx, name, vid, pid, serial, manufacturer in non_target_devices:
            report.append(
                f"{idx:<6} | {name[:30]:<30} | {vid:<8} | {pid:<6} | {serial:<14} | {manufacturer}"
            )
            # 如果有目标设备和非目标设备，打印分隔线
        if target_devices and non_target_devices:
            report.append("-" * 100)
            # 打印目标设备
        for idx, name, vid, pid, serial, manufacturer in target_devices:
            report.append(
                f"\033[32m{idx:<6} | {name[:30]:<30} | {vid:<8} | {pid:<6} | {serial:<14} | {manufacturer} \033[0m "
            )

    report.append(f"\n{border}")
    return "\n".join(report)

# -------------------- 检测并关闭AMCap进程 --------------------
def kill_amcap():
    killed = False
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"].lower() == AMCAP_EXE_NAME.lower():
                proc.kill()
                print(f"\033[31m 已终止 {AMCAP_EXE_NAME} 进程\033[0m")
                killed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return killed

# 状态报告
def print_final_device_status(target_cameras):
    print("\n\033[95m{:=^100}\033[0m".format(" 最终设备状态 "))
    for idx, cam in enumerate(target_cameras, 1):
        status = "✅" if not cam.failed_params else "❌"
        failed_param_names = [cam._get_ch_name(param) for param in cam.failed_params]
        failed_param_str = ", ".join(failed_param_names)
        if failed_param_str:
            failed_param_str = f"({failed_param_str})"
        print(f"摄像头{idx}: {status} ViTai-{cam.vid}-{cam.pid}{failed_param_str}")

# -------------------- 摄像头控制类 --------------------
class Camera:
    PARAM_MAP = {param: info["cv_constant"] for param, info in CameraConfig.PARAM_INFO.items()}

    def __init__(self, index, vid, pid):
        self.index = index
        self.vid = vid
        self.pid = pid
        self.cap = None
        self.failed_params = []

    # 初始化摄像头设备
    def init_camera(self):
        try:
            self.cap = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                print("\n 摄像头初始化失败！可能原因：摄像头被其他程序占用")
                return False
            if self.cap.isOpened():
                # 设置视频流的宽度和高度为640x480
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                try:
                    # 打开摄像头属性面板自动恢复默认
                    self.cap.set(cv2.CAP_PROP_SETTINGS, 0)
                except Exception as e:
                    print(f"设置摄像头属性面板默认值时出错: {e}")
                print(f"\033[95m正在为 ViTai-{self.vid}-{self.pid} 初始化需等待{CAMERA_INIT_DELAY}秒\033[0m")
                time.sleep(CAMERA_INIT_DELAY)
                return True
            else:
                print(
                    f"无法打开摄像头 {self.index} (ViTai-{self.vid}-{self.pid}). 错误代码: {self.cap.get(cv2.CAP_PROP_POS_MSEC)}")
                return False
        except cv2.error as cv_e:
            print(f"OpenCV 错误: 摄像头初始化错误 {self.index} (ViTai-{self.vid}-{self.pid}): {cv_e}")
        except Exception as e:
            print(f"摄像头初始化错误 {self.index} (ViTai-{self.vid}-{self.pid}): {e}")
            return False

    # 参数设置
    def apply_parameters(self):
        print(f"正在为 ViTai-{self.vid}-{self.pid} 设置参数")
        results = {"成功": [], "失败": []}

        for param_name, cv_constant in self.PARAM_MAP.items():
            config = CameraConfig.PARAM_INFO[param_name]
            target_value = config["value"]
            min_val, max_val = config["range"]

            # 范围修正
            clamped_value = max(min_val, min(target_value, max_val))
            # 范围警告
            if clamped_value != target_value:
                print(
                    f"\033[33m[警告] {self._get_ch_name(param_name)} "
                    f"超出允许范围({min_val}-{max_val})，已自动修正为：{clamped_value}\033[0m"
                )
            try:
                success = self.cap.set(cv_constant, float(clamped_value))
                if success:
                    print(
                        f"\033[32m {self._get_ch_name(param_name):<6} : {clamped_value} (设置成功)\033[0m"
                    )
                    results["成功"].append(param_name)
                else:
                    print(
                        f"\033[31m {self._get_ch_name(param_name):<6} : 该参数不被当前设备支持，错误代码: {self.cap.get(cv_constant)}\033[0m"
                    )
                    results["失败"].append(param_name)
                    self.failed_params.append(param_name)
            except Exception as e:
                print(
                    f"\033[31m {self._get_ch_name(param_name):<6} : 设置失败（错误详情：{str(e)}）\033[0m"
                )
                results["失败"].append(param_name)
                self.failed_params.append(param_name)

        return results

    def _get_ch_name(self, param):
        return CameraConfig.PARAM_INFO[param]["chinese_name"]

    # 显示视频流
    def show_video_stream(self):
        if SHOW_CAMERA_WINDOW:
            try:
                window_name = f"ViTai-{self.vid}-{self.pid}"
                cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
                cv2.resizeWindow(window_name, 640, 480)

                while not exit_event.is_set():
                    ret, frame = self.cap.read()
                    if ret:
                        # 叠加设备信息，左上角添加设备信息彩色窗口
                        cv2.putText(
                            frame,
                            f"ViTai {self.vid} {self.pid}",
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 255),
                            2,
                        )
                        cv2.imshow(window_name, frame)
                        cv2.waitKey(1)

            except Exception as e:
                print(f"显示视频流时出错 ViTai-{self.vid}-{self.pid}: {e}")
        else:
            print(
                f"跳过视频流显示 ViTai-{self.vid}-{self.pid} due to SHOW_CAMERA_WINDOW = False"
            )

    # 获取指定参数的值
    def get_param_value(self, param_const):
        if self.cap and self.cap.isOpened():
            return self.cap.get(param_const)
        return None

    # 输出摄像头状态
    def get_status_info(self):
        status_str = f"ViTai-{self.vid}-{self.pid}"
        for param_name, param_const in CameraConfig.READ_PARAMS.items():
            value = self.get_param_value(param_const)
            status_str += f" {param_name}: {value if value is not None else 'N/A'}"
        return status_str

    # 释放摄像头资源
    def cleanup(self):
        print(f"\033[36m释放 ViTai-{self.vid}-{self.pid}摄像头资源\033[0m")
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()

# -------------------- 主程序 --------------------
def main():
    # 打印系统报告
    print(generate_system_report())

    # 检测并关闭amcap
    if not kill_amcap():
        print(f"未检测到 {AMCAP_EXE_NAME} 进程")

    # 获取设备列表
    cameras = list_video_devices()
    hw_info = get_camera_hardware_info()

    # 匹配目标设备
    target_cameras = []
    # 记录已经处理过的 VID - PID 组合
    processed_devices = set()

    # 提取所有 ViTai 摄像头的硬件信息
    vitai_hw_info = [
        info for info in hw_info if TARGET_CAMERA_NAME.lower() in info["name"].lower()
    ]

    # 取出一个未处理的 ViTai 硬件信息
    for idx, name in cameras:
        if TARGET_CAMERA_NAME.lower() in name.lower():
            if vitai_hw_info:
                info = vitai_hw_info.pop(0)
                device_id = f"{info['vid']}-{info['pid']}"
                if device_id not in processed_devices:
                    target_cameras.append(Camera(idx, info["vid"], info["pid"]))
                    processed_devices.add(device_id)

    if not target_cameras:
        print(f"\n[错误] 未找到名称包含 '{TARGET_CAMERA_NAME}' 的摄像头！")
        return

    # 不支持调节参数说明
    print_unsupported_param_info()

    # 启动摄像头线程
    threads = []
    for cam in target_cameras:
        if cam.init_camera():
            cam.apply_parameters()
            # 启动视频流线程
            thread = Thread(target=cam.show_video_stream)
            print(f"启动摄像头线程: ViTai-{cam.vid}-{cam.pid}")
            print(f"{'-' * 100}")
            thread.start()
            threads.append(thread)
    print("\n\033[93m参数设置完成后窗口将保持{}秒\033[0m".format(MAIN_DELAY))
    print("\033[36m[" + "■" * 20 + "]\033[0m")
    for i in range(MAIN_DELAY, 0, -1):
        print(f"\r程序剩余运行时间: {i} 秒", end="")
        time.sleep(1)
    print()

    # 设置退出事件
    exit_event.set()

    try:
        for thread in threads:
            thread.join(timeout=MAIN_DELAY)
            if thread.is_alive():
                print(f"线程 {thread.name} 未能在 {MAIN_DELAY} 秒内正常退出。")
    finally:

        # 打印错误报告
        print_final_device_status(target_cameras)

        # 读取相机状态
        print(f"\n等待 {PARAM_READ_DELAY} 秒后读取相机状态...")
        time.sleep(PARAM_READ_DELAY)
        for cam in target_cameras:
            print(f"\033[93m{cam.get_status_info()}\033[0m")

        # 强制释放资源
        cv2.destroyAllWindows()

        print(f"\n{'=' * 44}释放摄像头资源{'=' * 45}")
        for cam in target_cameras:
            cam.cleanup()

        # 程序运行结束
        print(f"\n{'-' * 45}程序运行结束{'-' * 45}")


########################################################################################################################
if __name__ == "__main__":
    if not silent_install_deps():
        print("首次运行依赖安装完成，请重启程序！")
        sys.exit(0)
    main()
    