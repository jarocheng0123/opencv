# 通用摄像头配置工具

**基于Python的通用摄像头参数自动配置工具**

## 项目简介
本工具用于自动配置摄像头的参数（如对比度、饱和度、白平衡等），支持Windows和Ubuntu系统。具备以下功能：
- 自动检测并关闭冲突进程
- 多摄像头参数同步配置
- 实时视频流显示
- 硬件信息报告生成
- 自动依赖安装

## 安装指南

### 系统要求
- **Windows 10/11** 或 **Ubuntu 20.04+**
- Python 3.8+
- 支持DirectShow的摄像头设备

### 依赖安装
#### Windows
```bash
pip install opencv-python pycameralist psutil wmi
```

#### Ubuntu
```bash
sudo apt install python3-wmi
pip3 install opencv-python pycameralist psutil
```

**首次运行自动安装**：
```bash
python main.py  # Windows
python3 main.py  # Ubuntu
```

## 使用说明

### 配置参数
修改代码中的配置区域：
```python
# 用户配置区
TARGET_CAMERA_NAME = "Your Camera Name"  # 摄像头名称关键字，可修改为实际摄像头名称
AMCAP_EXE_NAME = "amcap+v3.0.9.exe"  # 需关闭的冲突进程
CAMERA_INIT_DELAY = 1  # 摄像头初始化等待时间（秒）
SHOW_CAMERA_WINDOW = True  # 是否显示实时画面
MAIN_DELAY = 5  # 程序运行时长（秒）
```

### 运行命令
```bash
python main.py  # Windows
python3 main.py  # Ubuntu
```

## 打包为exe（Windows）

### 安装PyInstaller
```bash
pip install pyinstaller
```

### 打包命令
在命令行中，进入包含`main.py`文件的目录，然后运行以下命令：
```bash
pyinstaller --onefile --noconsole main.py
```
- `--onefile`：将所有依赖打包成一个单独的可执行文件。
- `--noconsole`：打包后的程序运行时不显示命令行窗口。

### 查找打包后的文件
打包完成后，在项目目录下会生成一个`dist`文件夹，其中包含打包好的`main.exe`文件。

## 功能特性

### 1. 硬件信息报告
```
===================================================== 设备初始化报告 =====================================================
序号 | 设备名称                  | VID   | PID  | 序列号          | 制造商             
--------------------------------------------------
   1 | Your Camera Name         | 0483  | 5750 | 1234567890ABCDEF | Camera Manufacturer  
   2 | Another Camera Name      | 0483  | 5751 | 0987654321FEDCBA | Another Manufacturer         
```

### 2. 参数配置示例
```python
class CameraConfig:
    PARAM_INFO = {
        "Contrast": {"chinese_name": "对比度", "value": 39, "range": (0, 100)},
        "Hue": {"chinese_name": "色调调节", "value": 0, "range": (-180, 180)},
        # ...更多参数
    }
```

## 注意事项
1. **权限要求**：
   - Windows需以管理员身份运行
   - Ubuntu需添加摄像头权限：`sudo usermod -aG video $USER`

2. **常见问题**：
   - 若出现`无法打开摄像头`，请检查：
     - 摄像头是否被其他程序占用
     - 驱动是否正确安装
     - 是否有权限访问设备

3. **参数限制**：
   - 部分参数（如降噪强度）可能因硬件限制无法调节
   - 自动模式与手动模式参数可能存在冲突

## 贡献指南
1. 提交PR前请确保：
   - 代码符合PEP8规范
   - 添加必要的注释
   - 通过Windows和Ubuntu测试

