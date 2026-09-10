#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
导出功能 - 支持JSON和CSV格式
"""

import json
import csv
from pathlib import Path


class Exporter:
    """导出网络请求数据"""
    
    @staticmethod
    def export_json(requests, output_file):
        """
        导出为JSON格式
        
        Args:
            requests: 请求列表
            output_file: 输出文件路径
        """
        try:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(requests, f, ensure_ascii=False, indent=2)
            
            return True, f"已导出 {len(requests)} 条请求到 {output_file}"
        except Exception as e:
            return False, f"导出失败: {e}"