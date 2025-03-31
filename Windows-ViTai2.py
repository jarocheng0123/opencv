# -*- coding: utf-8 -*-

# ███████████████████████████████████████████████  Windows安装依赖和打包   ███████████████████████████████████████████████
# Windows PowerShell (管理员)(A) 使用 pip 安装依赖
# & "C:\Program Files\Python39\python.exe" -m pip install --upgrade pip --verbose pywin32 wmi opencv-python psutil PyCameraList pyinstaller -i https://mirrors.aliyun.com/pypi/simple

# Windows PowerShell 使用 PyInstaller 打包到桌面
# cd "C:\Users\Windows 10\Desktop"
# & "C:\Program Files\Python39\python.exe" -m PyInstaller --onefile --distpath "C:\Users\Windows 10\Desktop"  --hidden-import=colorama ViTai.py
# ██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████

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
import unicodedata
from threading import Thread, Event
from collections import defaultdict
from PyCameraList.camera_device import list_video_devices

# -------------------- 终端显示 --------------------
# 设置控制台颜色
os.system('color')  

# 在全局作用域定义退出事件
exit_event = Event()

# 定义基本文本颜色常量
BLACK='\033[30m' # 黑色文本
RED='\033[31m' # 红色文本
GREEN='\033[32m' # 绿色文本
YELLOW='\033[33m' # 黄色文本
BLUE='\033[34m' # 蓝色文本
PURPLE='\033[35m' # 紫色文本
CYAN='\033[36m' # 青色文本
WHITE='\033[37m' # 白色文本
RESET = '\033[0m'  # 重置颜色

# 文本居中显示（支持填充字符）
def center_text(text, width=100, fill_char=' '):
    def char_width(c):
        # 获取字符的显示宽度
        return 2 if unicodedata.east_asian_width(c) in ('F', 'W', 'A') else 1
    # 计算文本的实际显示宽度
    text_width = sum(char_width(c) for c in text)
    # 计算需要填充的数量
    padding = max(0, width - text_width)
    left_padding = padding // 2
    right_padding = padding - left_padding
    return fill_char * left_padding + text + fill_char * right_padding

# ██████████████████████████████████████████████████████ 用户配置区 ██████████████████████████████████████████████████████
# -------------------- 程序声明 --------------------
print()# 添加空行
print(f"{CYAN}{center_text(' ViTai相机配置程序 ', 100, '=')}{RESET}")
print()# 添加空行

# -------------------- 用户配置区 --------------------
# 摄像头名称
TARGET_CAMERA_NAME = "ViTai"
# 指定PID，VID 组合
SPECIFIED_PIDS_VIDS = [("F225", "0001")]
# 需要关闭的进程
AMCAP_EXE_NAME = "amcap+v3.0.9.exe"
# 摄像头初始化时间
CAMERA_INIT_DELAY = 1
# 显示摄像头画面
SHOW_CAMERA_WINDOW = True
# 程序退出延时
MAIN_DELAY = 10
# 读取参数等待时间
PARAM_READ_DELAY = 1
#窗口自动关闭控制
AUTO_CLOSE_WINDOW = True  # True: 程序结束后自动关闭窗口 | False: 保持窗口等待用户关闭

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
    print()# 添加空行
    print(f"{YELLOW}{center_text(f' {TARGET_CAMERA_NAME} 相机配置声明 ', 100, '=')}{RESET}")    
    print("降噪强度:   可能摄像头硬件没有内置降噪功能或驱动不支持调节降噪强度")
    print("数字变焦:   可能需要光学变焦镜头并通过物理控制，或摄像头本身不支持数字变焦")
    print("帧率:      可能摄像头硬件不支持指定的帧率范围或驱动未提供设置接口")
    print("分辨率宽度: 可能摄像头硬件不支持指定的分辨率宽度或驱动未提供设置接口")
    print("分辨率高度: 可能摄像头硬件不支持指定的分辨率高度或驱动未提供设置接口")
    print("色彩模式:   可能摄像头硬件不支持多种色彩模式或驱动未提供设置接口")

# ██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████

# -------------------静默依赖安装 --------------------
def silent_install_deps():
    required = [
        ("opencv-python", "cv2"),
        ("pycameralist", "PyCameraList.camera_device"),
        ("psutil", "psutil"),
        ("wmi", "wmi"),
    ]

    python_exe = sys.executable
    installed = True

    for pkg_info in required:
        pkg_name, mod_name = pkg_info
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
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"安装 {pkg_name} 时出错: {e}")

    return installed

# -------------------- 硬件信息模块 --------------------
def _get_reg_value(key, value_name):
    try:
        return winreg.QueryValueEx(key, value_name)[0]
    except:
        return "N/A"

# 生成结构化系统报告
def get_camera_hardware_info():
    c = wmi.WMI()

    # 设备列表
    devices = []
    for item in c.Win32_PnPEntity(ClassGuid="{ca3e7ab9-b4c3-4ae6-8251-579ef933890f}"):
        if not item.DeviceID:
            continue

        # 解析设备ID
        vid_pid = re.findall(r"VID_([0-9A-F]{4})&PID_([0-9A-F]{4})", item.DeviceID, re.I)
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

# 生成系统报告
def generate_system_report(): 
    report = []

    # 硬件信息
    hw_info = []
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

    report.insert(
        0,
        f"{YELLOW}{center_text(' 设备初始化报告 ', 100, '=')}{RESET}",
    )

    if hw_info:
        # 收集目标设备和非目标设备的信息
        target_devices = [] # 目标设备
        non_target_devices = [] # 非目标设备
       
        target_device_index = 1 # 目标设备序号
        vid_pid_counts = {} # 重复设备计数
        duplicate_devices = [] # 重复设备
        specified_devices_found = [] # 指定PID/VID的设备

        for device in hw_info:
            name = device["name"]
            vid = device["vid"]
            pid = device["pid"]
            serial = device["serial"]
            manufacturer = device["manufacturer"]

            key = (vid, pid)
            if key in vid_pid_counts:
                duplicate_devices.append(device) # 计数
            else:
                vid_pid_counts[key] = 1 # 计数

            if TARGET_CAMERA_NAME.lower() in name.lower(): # 目标设备
                target_devices.append(
                    (target_device_index, name, vid, pid, serial, manufacturer)
                )
                target_device_index += 1
                if key in SPECIFIED_PIDS_VIDS: # 指定PID/VID的设备
                    specified_devices_found.append(device)
            else:
                non_target_devices.append((0, name, vid, pid, serial, manufacturer))

        # 生成报告内容
        report.append(
            "{:<4} | {:<26} | {:<8} | {:<6} | {:<11} | {}".format(
                "序号", "设备名称", "VID", "PID", "序列号", "制造商"
            )
        )
        report.append("-" * 100)

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

        # 重复设备警告
        if duplicate_devices:
            unique_duplicates = list({(d['vid'], d['pid']) for d in duplicate_devices})

            device_names_map = defaultdict(list)
            for device in duplicate_devices:
                device_names_map[(device['vid'], device['pid'])].append(device['name'])
            report.append(f"\n{RED}{center_text(' 检测到重复VID/PID设备组合 ', 100, '=')}{RESET}")
            for vid, pid in unique_duplicates:
                report.append(f" ❗ VID: {vid}, PID: {pid}") # 打印VID/PID

        # 指定PID/VID的设备
        if specified_devices_found: 
            report.append(f"\n{RED}{center_text(' 找到指定 PID/VID 的设备 ', 100, '=')}{RESET}")
            for device in specified_devices_found:
                report.append(f" ⚠️ 设备名称: {device['name']}, VID: {device['vid']}, PID: {device['pid']}")
            report.append("\033[0m")
        else:
            report.append(f"\n{RED}{center_text(' 未找到指定 PID/VID 的设备 ', 100, '=')}{RESET}")

    # 返回报告内容
    return "\n".join(report) 

# -------------------- 检测并关闭AMCap进程 --------------------
def kill_amcap():
    print(f"{YELLOW}{center_text('进程管理', 100, '=')}{RESET}")
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
    print()# 添加空行
    print(f"{PURPLE}{center_text(' 最终设备状态 ', 100, '=')}{RESET}")
    for idx, cam in enumerate(target_cameras, 1):
        status = "✅" if not cam.failed_params else "❌"
        failed_param_names = [cam._get_ch_name(param) for param in cam.failed_params]
        failed_param_str = ", ".join(failed_param_names)
        if failed_param_str:
            failed_param_str = f"({failed_param_str})"
        print(f"摄像头{idx}: {status} ViTai-{cam.vid}-{cam.pid}{failed_param_str}")

# -------------------- 摄像头控制类 --------------------
class Camera:
    PARAM_MAP = {param: info["cv_constant"] for param, info in CameraConfig.PARAM_INFO.items()} # 参数映射表

    def __init__(self, index, vid, pid): # 初始化摄像头
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
                print()# 添加空行
                print(f"{PURPLE}{center_text(' 摄像头初始化 ', 100, '=')}{RESET}")    
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

        for param_name, cv_constant in self.PARAM_MAP.items(): # 遍历所有参数
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
                        f"\033[32m🔁   {self._get_ch_name(param_name):<6} : {clamped_value} (设置成功)\033[0m"
                    )
                    results["成功"].append(param_name)
                else:
                    print(
                        f"\033[31m🐞   {self._get_ch_name(param_name):<6} : 该参数不被当前设备支持，错误代码: {self.cap.get(cv_constant)}\033[0m"
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

    # 获取参数的中文名称
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

    # 获取摄像头硬件信息
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

    # 没有找到目标设备
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
            print()# 添加空行
            print(f"{RESET}{center_text(' 启动视频流线程 ', 100, '-')}{RESET}")
            thread.start()
            threads.append(thread)
    print("\033[93m参数设置完成后窗口将保持{}秒\033[0m".format(MAIN_DELAY))
    print("\033[36m[" + "■" * 20 + "]\033[0m")
    for i in range(MAIN_DELAY, 0, -1):
        print(f"\r🚧 程序剩余运行时间: {i} 秒", end="")
        time.sleep(1)
    print()

    # 设置退出事件
    exit_event.set()
    
    # 等待所有线程结束
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

        print()# 添加空行
        print(f"{RESET}{center_text(' 释放摄像头资源 ', 100, '=')}{RESET}")
        for cam in target_cameras:
            cam.cleanup()

        print()# 添加空行
        print(f"{RESET}{center_text(' 程序运行结束 ', 100, '=')}{RESET}")

        # 打包exe窗口关闭控制
        if not AUTO_CLOSE_WINDOW:
            input("\n按任意键关闭窗口...")

########################################################################################################################
if __name__ == "__main__":

    # 安装依赖
    if not silent_install_deps():
        print("首次运行依赖安装完成，请重启程序！")

        # 退出程序
        sys.exit(0)
        
    main()
    