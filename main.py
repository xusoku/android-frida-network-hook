#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Android Frida Network Hook - Main Entry Point
使用Frida框架在Android上Hook网络请求
"""

import argparse
import sys
import json
import time
from pathlib import Path

try:
    import frida
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError as e:
    print(f"❌ 缺少依赖: {e}")
    print("请运行: pip install -r requirements.txt")
    sys.exit(1)

from utils.logger import Logger
from utils.request_parser import RequestParser
from utils.export import Exporter
from hook_scripts.loader import HookScriptLoader


class FridaNetworkHook:
    """Frida网络Hook主类"""
    
    def __init__(self, package_name, output_file=None, verbose=False):
        self.package_name = package_name
        self.output_file = output_file
        self.verbose = verbose
        self.logger = Logger(verbose=verbose)
        self.requests = []
        self.device = None
        self.process = None
        self.script = None
        self.hook_loader = HookScriptLoader()
        
    def connect_device(self):
        """连接到Android设备"""
        try:
            self.device = frida.get_usb_device(timeout=5)
            self.logger.info(f"✅ 已连接到设备: {self.device.name}")
            return True
        except frida.TimedOutError:
            self.logger.error("❌ 连接超时，请确保:")
            self.logger.error("   1. USB调试已启用")
            self.logger.error("   2. Frida Server在设备上运行")
            self.logger.error("   3. 运行: adb shell /data/local/tmp/frida-server &")
            return False
        except Exception as e:
            self.logger.error(f"❌ 连接失败: {e}")
            return False
    
    def attach_process(self):
        """连接到目标应用进程"""
        try:
            # 获取应用进程ID
            self.process = self.device.get_process(self.package_name)
            self.logger.info(f"✅ 已连接到进程: {self.package_name} (PID: {self.process.pid})")
            return True
        except frida.ProcessNotFoundError:
            self.logger.error(f"❌ 找不到应用: {self.package_name}")
            self.logger.info("📱 当前正在运行的应用:")
            try:
                processes = self.device.enumerate_processes()
                for proc in processes[:10]:
                    self.logger.info(f"   - {proc.name} ({proc.pid})")
                self.logger.info("   ...")
            except:
                pass
            return False
        except Exception as e:
            self.logger.error(f"❌ 连接进程失败: {e}")
            return False
    
    def on_message(self, message, data):
        """处理来自Frida脚本的消息"""
        try:
            if message['type'] == 'send':
                payload = message.get('payload', {})
                
                # 解析网络请求
                if payload.get('type') == 'http_request':
                    request = RequestParser.parse(payload)
                    self.requests.append(request)
                    self._print_request(request)
                    
                    # 实时导出
                    if self.output_file:
                        self._save_to_file(request)
            
            elif message['type'] == 'error':
                self.logger.error(f"Script error: {message.get('description')}")
                
        except Exception as e:
            self.logger.error(f"Message handling error: {e}")
    
    def _print_request(self, request):
        """打印单个请求到控制台"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.GREEN}[{request['timestamp']}] {request['method']} {request['url']}")
        print(f"{Style.RESET_ALL}")
        
        # 请求头
        if request.get('headers'):
            print(f"{Fore.YELLOW}Request Headers:{Style.RESET_ALL}")
            for key, value in request['headers'].items():
                print(f"  {key}: {value[:100]}...")
        
        # 请求体
        if request.get('body'):
            body_preview = request['body'][:200]
            print(f"{Fore.YELLOW}Request Body:{Style.RESET_ALL}")
            print(f"  {body_preview}...")
        
        # 响应状态
        if request.get('response_code'):
            status_color = Fore.GREEN if 200 <= request['response_code'] < 300 else Fore.RED
            print(f"{status_color}Response: {request['response_code']}{Style.RESET_ALL}")
    
    def _save_to_file(self, request):
        """保存请求到文件"""
        try:
            if not self.output_file.parent.exists():
                self.output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 追加到JSON文件
            requests_list = []
            if self.output_file.exists():
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    requests_list = json.load(f)
            
            requests_list.append(request)
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(requests_list, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Save file error: {e}")
    
    def load_hook_script(self, hook_type='all'):
        """加载Hook脚本"""
        try:
            script_content = self.hook_loader.load(hook_type)
            if not script_content:
                self.logger.error(f"❌ 无法加载Hook脚本: {hook_type}")
                return False
            
            self.script = self.device.create_script(script_content)
            self.script.on('message', self.on_message)
            self.script.load()
            
            self.logger.info(f"✅ Hook脚本已加载: {hook_type}")
            return True
        except Exception as e:
            self.logger.error(f"❌ 加载脚本失败: {e}")
            return False
    
    def start_hooking(self, hook_type='all'):
        """开始Hook网络请求"""
        self.logger.info(f"\n🎯 开始监控应用: {self.package_name}")
        self.logger.info(f"📝 Hook类型: {hook_type}")
        
        if self.output_file:
            self.logger.info(f"💾 输出文件: {self.output_file}")
        
        self.logger.info(f"\n⏳ 等待应用发起网络请求...\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("\n\n⏹️  正在停止...\n")
    
    def stop_hooking(self):
        """停止Hook"""
        try:
            if self.script:
                self.script.unload()
            self.logger.info(f"✅ Hook已停止")
            self.logger.info(f"📊 捕获请求数: {len(self.requests)}")
        except Exception as e:
            self.logger.error(f"❌ 停止Hook失败: {e}")
    
    def run(self, hook_type='all'):
        """运行Hook"""
        # 连接设备
        if not self.connect_device():
            return False
        
        # 连接进程
        if not self.attach_process():
            return False
        
        # 加载脚本
        if not self.load_hook_script(hook_type):
            return False
        
        # 开始Hook
        try:
            self.start_hooking(hook_type)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_hooking()
        
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Android Frida Network Hook - 无需Root自动Hook网络请求',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # Hook微信应用的所有请求
  python main.py --package com.tencent.mm
  
  # Hook支付宝并保存到文件
  python main.py --package com.eg.android.AlipayGphone --output requests.json
  
  # 仅Hook OkHttp请求
  python main.py --package com.example.app --hook okhttp
  
  # 详细日志模式
  python main.py --package com.example.app -vv
        """
    )
    
    parser.add_argument(
        '--package', '-p',
        required=True,
        help='目标应用包名 (e.g., com.tencent.mm)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='输出文件路径 (JSON格式)'
    )
    
    parser.add_argument(
        '--hook', '-t',
        choices=['all', 'okhttp', 'http', 'retrofit', 'volley'],
        default='all',
        help='Hook类型 (默认: all)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='count',
        default=0,
        help='详细日志输出'
    )
    
    args = parser.parse_args()
    
    # 创建Hook实例
    hook = FridaNetworkHook(
        package_name=args.package,
        output_file=args.output,
        verbose=args.verbose > 0
    )
    
    # 运行
    success = hook.run(hook_type=args.hook)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()