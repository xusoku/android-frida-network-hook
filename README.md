# Android Frida Network Hook

使用Frida框架在Android 9+上自动Hook其他App的网络请求，无需Root权限。

## 功能特性

- ✅ **无需Root** - 仅需USB调试权限
- ✅ **自动Hook** - 支持OkHttp、HttpURLConnection、Retrofit等主流库
- ✅ **实时捕获** - 实时显示HTTP/HTTPS请求和响应
- ✅ **Android 9+** - 完全适配Android 9及以上版本
- ✅ **多App支持** - 可同时监控多个应用
- ✅ **请求导出** - 支持JSON/CSV格式导出

## 支持的Hook目标

| 库名 | 包名 | 状态 |
|-----|------|------|
| OkHttp | okhttp3 | ✅ 支持 |
| HttpURLConnection | java.net | ✅ 支持 |
| Retrofit | retrofit2 | ✅ 支持 |
| HttpClient | org.apache.http | ✅ 支持 |
| Volley | com.android.volley | ✅ 支持 |

## 快速开始

### 前置要求

- Android 9+ 设备或模拟器
- USB连接电脑（开启USB调试）
- Python 3.7+
- frida 和 frida-tools

### 安装步骤

#### 1. 安装Frida工具

```bash
pip install -r requirements.txt
```

#### 2. 下载Frida Server到设备

```bash
# 获取设备架构
adb shell uname -m

# 下载对应版本 (https://github.com/frida/frida/releases)
# 例如: arm64-v8a -> frida-server-16.1.0-android-arm64.xz

# 解压并推送到设备
xz -d frida-server-16.1.0-android-arm64.xz
adb push frida-server-16.1.0-android-arm64 /data/local/tmp/
adb shell chmod +x /data/local/tmp/frida-server-16.1.0-android-arm64
```

#### 3. 启动Frida Server

```bash
adb shell /data/local/tmp/frida-server-16.1.0-android-arm64 &
```

#### 4. 验证连接

```bash
frida-ps -U
```

### 使用方法

#### 基础用法

```bash
# Hook指定应用的所有网络请求
python main.py --package com.example.app

# 保存到文件
python main.py --package com.example.app --output requests.json

# Hook特定库（OkHttp）
python main.py --package com.example.app --hook okhttp

# 详细日志
python main.py --package com.example.app -vv
```

## 项目结构

```
android-frida-network-hook/
├── main.py                 # 主程序入口
├── hook_scripts/           # Frida Hook脚本
│   ├── hook_okhttp.js      # OkHttp拦截脚本
│   ├── hook_http.js        # HttpURLConnection拦截脚本
│   └── hook_all.js         # 全局Hook脚本
├── utils/                  # 工具函数
│   ├── request_parser.py   # 请求解析器
│   ├── logger.py           # 日志模块
│   └── export.py           # 导出功能
├── docs/                   # 文档
└── requirements.txt        # Python依赖
```

## 常见问题

### Q: 为什么连接失败？
A: 
- 确保USB调试已启用
- 运行 `adb devices` 检查设备连接
- 确保Frida Server在设备上运行中

### Q: HTTPS请求无法解密？
A: 
- 某些App使用证书固定(SSL Pinning)
- 可以扩展Hook脚本进行处理

### Q: Android 9有什么特殊限制？
A:
- 明文HTTP被限制
- 需要配置合适的SELinux策略

## 许可证

MIT License