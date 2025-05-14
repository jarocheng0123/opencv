# 通用摄像头配置工具

**基于Python的通用摄像头参数自动配置工具**
 - 最新版本
```bash
2025/5/14
ViTai4.py
ViTai测试2.py
```

## 项目简介
本工具用于自动配置摄像头的参数具备以下功能：

- 自动检测系统中存在相同 VID/PID 组合的摄像头
- 自动检测并关闭冲突进程
- 多摄像头参数同步配置（支持多设备同时设置）
- 实时视频流显示（带设备信息叠加）
- 硬件信息报告生成（含 VID/PID 检测）
- 支持查找指定 VID/PID 的相机
- 重复 VID/PID 设备检测与警告
## 安装指南

### 系统要求
- Windows 10/11
- Python 3.9+

### 脚本测试环境

- 用户名 
```bash
Windows 10
```
- 电脑信息
```bash
主机名:           DESKTOP-0MI7116
OS 名称:          Microsoft Windows 10 专业工作站版
OS 版本:          10.0.19045 暂缺 Build 19045
OS 制造商:        Microsoft Corporation
OS 配置:          独立工作站
OS 构件类型:      Multiprocessor Free
注册的所有人:      Windows 10
```

- 文件名 
```bash
ViTai.py
```

- 图标名
```bash
ViTailogo.ico
```

- Python包
```bash
python-3.9.13-amd64
```

- Python安装路径 
```bash
C:\Program Files\Python39
```

- Python脚本路径 
```bash
C:\Users\Windows 10\Desktop\ViTai4.py
```

- 查找指定相机
```python
SPECIFIED_PIDS_VIDS = [("F225", "0001")]
```

### 依赖安装
#### Python安装路径
```bash
 C:\Program Files\Python39\python.exe
```

#### Windows PowerShell (管理员)(A) 使用 pip 安装依赖
```bash
& "C:\Program Files\Python39\python.exe" -m pip install --upgrade pip --verbose pywin32 wmi opencv-python psutil PyCameraList pyinstaller -i https://mirrors.aliyun.com/pypi/simple
```


## 使用说明

### 配置参数
修改代码中的配置区域：
```python
# 摄像头名称
TARGET_CAMERA_NAME = "ViTai"
# SN码固定前缀
NAME_GF225 = "GF225"
# 指定PID，VID 组合
SPECIFIED_PIDS_VIDS = [("F225", "0001")]
# 需要关闭的进程
AMCAP_EXE_NAME = "amcap+v3.0.9.exe"
# 摄像头初始化时间
CAMERA_INIT_DELAY = 1
# 显示摄像头画面
SHOW_CAMERA_WINDOW = True
# 显示摄像头属性窗口
SHOW_PROPERTY_WINDOW = False
# 程序退出延时
MAIN_DELAY = 10
# 需要关闭的属性窗口关键字
KEYWORDS = ["ViTai 属性"]
# 读取参数等待时间
PARAM_READ_DELAY = 1
#窗口自动关闭控制
AUTO_CLOSE_WINDOW = False
```

### 配置参数详细说明
- `TARGET_CAMERA_NAME`：指定要配置的摄像头名称，用于筛选目标设备。
- `NAME_GF225`：SN 码的固定前缀，在生成 SN 码时使用。
- `SPECIFIED_PIDS_VIDS`：指定要查找的 PID 和 VID 组合，以列表形式存储，每个元素为一个元组 `(PID, VID)`。
- `AMCAP_EXE_NAME`：需要关闭的进程名称，用于避免进程冲突。
- `CAMERA_INIT_DELAY`：摄像头初始化的延迟时间（秒），确保摄像头正常启动。
- `SHOW_CAMERA_WINDOW`：是否显示摄像头画面，取值为 `True` 或 `False`。
- `SHOW_PROPERTY_WINDOW`：是否显示摄像头属性窗口，取值为 `True` 或 `False`。
- `MAIN_DELAY`：程序退出的延迟时间（秒）。
- `KEYWORDS`：需要关闭的属性窗口关键字列表，用于自动关闭相关窗口。
- `PARAM_READ_DELAY`：读取参数的等待时间（秒）。
- `AUTO_CLOSE_WINDOW`：窗口自动关闭控制，`True` 表示程序结束后自动关闭窗口，`False` 表示保持窗口等待用户关闭。

### 预设参数配置方案说明  
| 方案名称          | 主要参数调整                                                                 | 适用场景                |
|-------------------|------------------------------------------------------------------------------|-------------------------|
| `PARAM_INFO_DEFAULT` | 默认参数，自动白平衡开启，亮度-39，伽玛300，白平衡色温6500（硬件推荐值）     | 通用场景                |
| `PARAM_INFO_A`     | 自动白平衡**关闭**，亮度-64（最低），白平衡色温6000（暖色调）                | 白色9×9软体检测         |
| `PARAM_INFO_B`     | 自动白平衡**关闭**，亮度0（中间值），其他参数保持默认                        | 灰色9×9软体检测         |
| `PARAM_INFO_C`     | 自动白平衡**关闭**，亮度0，伽玛100（低对比度）                              | 纯灰色软体（低反光场景）|
| `PARAM_INFO_D`     | 自动白平衡**关闭**，亮度-64（最低），伽玛100（低对比度）                    | 纯白色软体（高反光场景）|

## 打包为exe（Windows）

**Windows PowerShell 使用 PyInstaller 打包**：
```bash
cd "C:\Users\Windows 10\Desktop"
```
```bash
& "C:\Program Files\Python39\python.exe" -m PyInstaller --onefile --distpath "C:\Users\Windows 10\Desktop" --hidden-import=colorama --icon=ViTailogo.ico ViTai4.py
```

## 功能特性
### 1. 硬件信息报告
```
========================================== 设备初始化报告 ==========================================
序号   | 设备名称                        | VID      | PID    | 序列号         | 制造商
----------------------------------------------------------------------------------------------------
0      | Integrated IR Camera           | 174F     | 1820   | N/A            | N/A
0      | Integrated Camera              | 174F     | 1820   | N/A            | N/A
----------------------------------------------------------------------------------------------------
1      | ViTai                          | FFFF     | 9001   | GF2259001A9B3  | N/A
2      | ViTai                          | AD08     | 1032   | GF2251032BA78  | N/A

==================================== 检测到重复VID/PID设备组合 =====================================
 ❗ VID: 174F, PID: 1820

===================================== 找到指定 PID/VID 的设备 ======================================
 ⚠️ 设备名称: ViTai, VID: F225, PID: 0001

```

### 2. 参数配置示例
 - 配置方案使用方法
1. 在用户配置区找到`CONFIG_NAME`参数：  
   ```python  
   # 选择要使用的参数配置方案名称  
   CONFIG_NAME = "PARAM_INFO_DEFAULT"  
   ```  
2. 将`CONFIG_NAME`设置为上述方案名称（如`"PARAM_INFO_A"`）即可生效。  
3. 支持自定义方案：如需新增配置，可在`CameraConfig`类中添加新的参数组（如`PARAM_INFO_E`），并更新`PARAM_CONFIG_MAP`映射关系。

- 参数配置需要根据实际情况选择
```python
class CameraConfig:
    PARAM_INFO_DEFAULT = {
        # 默认值#########################################################################################################
        "Brightness": {"chinese_name": "亮度调节", "value": -39, "range": (-64, 64),"cv_constant": cv2.CAP_PROP_BRIGHTNESS},
        "Contrast": {"chinese_name": "对比度", "value": 39, "range": (0, 100), "cv_constant": cv2.CAP_PROP_CONTRAST},
        "Hue": {"chinese_name": "色调调节", "value": 0, "range": (-180, 180), "cv_constant": cv2.CAP_PROP_HUE},
        "Saturation": {"chinese_name": "饱和度", "value": 72, "range": (0, 100),"cv_constant": cv2.CAP_PROP_SATURATION},
        "Sharpness": {"chinese_name": "清晰度", "value": 75, "range": (0, 100), "cv_constant": cv2.CAP_PROP_SHARPNESS},
        "Gamma": {"chinese_name": "伽玛校正", "value": 300, "range": (100, 500), "cv_constant": cv2.CAP_PROP_GAMMA},
        "WhiteBalance": {"chinese_name": "白平衡色温", "value": 6500, "range": (2800, 6500), "cv_constant": cv2.CAP_PROP_WHITE_BALANCE_BLUE_U},
        "Gain": {"chinese_name": "增益", "value": 64, "range": (1, 128), "cv_constant": cv2.CAP_PROP_GAIN},
        "Focus": {"chinese_name": "焦点", "value": 68, "range": (0, 1023), "auto_support": True,"cv_constant": cv2.CAP_PROP_FOCUS},
        "Exposure": {"chinese_name": "曝光值", "value": -9, "range": (-14, 0), "cv_constant": cv2.CAP_PROP_EXPOSURE},
        # 自动模式########################################################################################################
        "AutoWhiteBalance": {"chinese_name": "自动白平衡模式", "value": 1, "range": (0, 1),"cv_constant": cv2.CAP_PROP_AUTO_WB},
        "AutoFocus": {"chinese_name": "自动对焦", "value": 1, "range": (0, 1), "cv_constant": cv2.CAP_PROP_AUTOFOCUS},
        "AutoExposure": {"chinese_name": "自动曝光模式", "value": 0, "range": (0, 1),"cv_constant": cv2.CAP_PROP_AUTO_EXPOSURE},
        # 设置固定值######################################################################################################

        # 不支持参数######################################################################################################
        # "NoiseReduction": {"chinese_name": "降噪强度", "value": 50, "range": (0, 100), "cv_constant": None},
        # "Zoom": {"chinese_name": "数字变焦", "value": 0, "range": (0, 100), "cv_constant": cv2.CAP_PROP_ZOOM},
        # "FrameRate": {"chinese_name": "帧率", "value": 30, "range": (1, 60), "cv_constant": cv2.CAP_PROP_FPS},
        # "ResolutionWidth": {"chinese_name": "分辨率宽度", "value": 1920, "range": (640, 3840), "cv_constant": cv2.CAP_PROP_FRAME_WIDTH},
        # "ResolutionHeight": {"chinese_name": "分辨率高度", "value": 1080, "range": (480, 2160), "cv_constant": cv2.CAP_PROP_FRAME_HEIGHT},
        # "ColorMode": {"chinese_name": "色彩模式", "value": 0, "range": (0, 2), "cv_constant": None}
    }
```
- 部分硬件不支持声明（需要与厂商确认）
```python 
    print("降噪强度:   可能摄像头硬件没有内置降噪功能或驱动不支持调节降噪强度")
    print("数字变焦:   可能需要光学变焦镜头并通过物理控制，或摄像头本身不支持数字变焦")
    print("帧率:       可能摄像头硬件不支持指定的帧率范围或驱动未提供设置接口")
    print("分辨率宽度: 可能摄像头硬件不支持指定的分辨率宽度或驱动未提供设置接口")
    print("分辨率高度: 可能摄像头硬件不支持指定的分辨率高度或驱动未提供设置接口")
    print("色彩模式:   可能摄像头硬件不支持多种色彩模式或驱动未提供设置接口")
```    

## 常见问题解答

**Q: 为什么摄像头无法打开？**
- 检查是否有其他程序占用
- 确认驱动程序正确安装
- 以管理员身份运行程序

**Q: 参数设置无效怎么办？**
- 尝试重启摄像头设备
- 检查硬件兼容性
- 查看设备属性面板确认支持的参数范围

**Q: 视频流显示卡顿？**
- 降低分辨率设置
- 减少参数调整频率
- 检查系统资源占用情况

**Q: 参数设置后画面异常（过亮/过暗）怎么办？**  
- A: 尝试切换不同的预设方案（如`PARAM_INFO_DEFAULT`或`PARAM_INFO_A`）

### 安全声明
1. 本程序需要访问摄像头设备，请确保已获得相应权限
2. 自动关闭进程功能可能会影响其他应用程序，请谨慎使用
3. 参数调整可能导致图像异常，建议先备份原始配置

## 版本更新日志
### v 2025.05.14
- **新增：SN 码解析**
  - 功能：在生成设备初始化报告时，对目标设备的 SN 码进行解析和生成。
  - 使用方法：在 `generate_system_report` 函数中，会自动根据 `NAME_GF225` 和设备的 PID 生成 SN 码。

### v 2025.04.23
- **新增：多参数配置方案支持**
  - 功能：支持多种预设参数配置方案，如 `PARAM_INFO_DEFAULT`, `PARAM_INFO_A`, `PARAM_INFO_B` 等，可根据不同场景选择合适的方案。
  - 使用方法：在代码中修改相应的配置方案名称即可切换参数配置。

- **优化：参数配置模块化**
  - 改进点：将不同方案的参数独立维护，提高了代码的可扩展性。
  - 影响：方便后续添加新的参数配置方案，减少代码的耦合度。  

### v 2025.03.31
- 新增：摄像头属性窗口显示控制开关
- 优化：资源释放验证与异常处理机制

### v 2025.03.21
- 新增重复ID检测功能
- 优化硬件信息报告格式
- 增强参数校验逻辑
- 修复多摄像头同步配置问题

### v 2025.03.08
- 第一版相机调控脚本