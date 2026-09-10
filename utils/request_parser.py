#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
网络请求解析器
"""

from datetime import datetime
from urllib.parse import urlparse
import json


class RequestParser:
    """解析从Frida脚本接收到的网络请求"""
    
    @staticmethod
    def parse(payload):
        """
        解析原始payload为标准请求对象
        
        Args:
            payload: 来自Frida脚本的数据
        
        Returns:
            dict: 标准化的请求对象
        """
        request = {
            'timestamp': datetime.now().isoformat(),
            'url': payload.get('url', ''),
            'method': payload.get('method', 'GET'),
            'headers': payload.get('headers', {}),
            'body': payload.get('body', ''),
            'response_code': payload.get('response_code'),
            'response_headers': payload.get('response_headers', {}),
            'response_body': payload.get('response_body', ''),
            'library': payload.get('library', 'unknown'),
            'duration_ms': payload.get('duration_ms', 0),
        }
        
        # 解析URL
        parsed_url = urlparse(request['url'])
        request['host'] = parsed_url.hostname or ''
        request['path'] = parsed_url.path or '/'
        request['scheme'] = parsed_url.scheme or 'http'
        
        # 尝试解析JSON body
        if request['body']:
            try:
                request['body_json'] = json.loads(request['body'])
            except:
                request['body_json'] = None
        
        # 尝试解析JSON响应
        if request['response_body']:
            try:
                request['response_json'] = json.loads(request['response_body'])
            except:
                request['response_json'] = None
        
        return request