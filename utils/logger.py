#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志模块
"""

from datetime import datetime
from colorama import Fore, Style


class Logger:
    """简单的日志类"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
    
    def _get_timestamp(self):
        """获取时间戳"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def info(self, message):
        """打印信息"""
        print(f"{Fore.BLUE}[INFO {self._get_timestamp()}]{Style.RESET_ALL} {message}")
    
    def success(self, message):
        """打印成功信息"""
        print(f"{Fore.GREEN}[✓ {self._get_timestamp()}]{Style.RESET_ALL} {message}")
    
    def warning(self, message):
        """打印警告信息"""
        print(f"{Fore.YELLOW}[⚠ {self._get_timestamp()}]{Style.RESET_ALL} {message}")
    
    def error(self, message):
        """打印错误信息"""
        print(f"{Fore.RED}[✗ {self._get_timestamp()}]{Style.RESET_ALL} {message}")
    
    def debug(self, message):
        """打印调试信息"""
        if self.verbose:
            print(f"{Fore.CYAN}[DEBUG {self._get_timestamp()}]{Style.RESET_ALL} {message}")