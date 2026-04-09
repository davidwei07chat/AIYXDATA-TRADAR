# (C) 2026 AIYXDATA. All rights reserved.
# Project: AIYXDATA-TRADAR

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIYXDATA-TRADAR 自定义配置保存服务器 / AIYXDATA-TRADAR Custom Config Server
"""

import os
import sys
import json
import posixpath
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from datetime import datetime
import shutil

# Web 服务器配置 (Web Server Config)
WEBSERVER_PORT = int(os.environ.get("WEBSERVER_PORT", "8080"))
WEBSERVER_DIR = "/AIYXDATA-TRADAR/output"
CONFIG_DIR = Path("/AIYXDATA-TRADAR/config")
PROFILES_DIR = CONFIG_DIR / "profiles"

# 确保 profiles 目录存在 (Ensure profiles directory exists)
PROFILES_DIR.mkdir(parents=True, exist_ok=True)


class ConfigServerHandler(SimpleHTTPRequestHandler):
    """
    支持跨域及 POST 保存配置的 HTTP 处理器 / HTTP Handler supporting CORS and POST configuration saves
    """

    def end_headers(self):
        """添加跨域支持与禁缓存 (Add CORS support and disable caching)"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        super().end_headers()

    def do_OPTIONS(self):
        """处理预检请求 (Handle preflight CORS requests)"""
        self.send_response(200)
        self.end_headers()

    def send_json_response(self, code, data):
        """通用的 JSON 响应发送器 (Generic JSON response sender)"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_GET(self):
        """处理自定义 GET 路由 (Handle custom GET routes)"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        # 0. 读取单个当前配置文件 (Read a single current config file)
        if path == '/api/load':
            query_params = urllib.parse.parse_qs(parsed_path.query)
            file_type = query_params.get('file', [None])[0]
            
            file_map = {
                'config': CONFIG_DIR / 'config.yaml',
                'frequency': CONFIG_DIR / 'frequency_words.txt',
                'timeline': CONFIG_DIR / 'timeline.yaml',
                'analysis_prompt': CONFIG_DIR / 'ai_analysis_prompt.txt',
                'translation_prompt': CONFIG_DIR / 'ai_translation_prompt.txt'
            }
            
            if file_type not in file_map:
                return self.send_json_response(400, {"success": False, "error": f"Invalid file type: {file_type}."})
            
            target_file = file_map[file_type]
            if not target_file.exists():
                return self.send_json_response(404, {"success": False, "error": f"File not found: {target_file.name}"})
            
            try:
                with open(target_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                return self.send_json_response(200, {"success": True, "content": content})
            except Exception as e:
                return self.send_json_response(500, {"success": False, "error": str(e)})

        # 1. 列出所有配置方案 (List all config profiles)
        elif path == '/api/profiles/list':

            try:
                profiles = []
                # 扫描 zip 或 yaml 文件作为方案标识 (Scan for yaml files as profiles)
                for item in PROFILES_DIR.iterdir():
                    if item.is_file() and item.suffix == '.yaml':
                        stat = item.stat()
                        profiles.append({
                            "name": item.stem, # 去扩展名 (filename without ext)
                            "mtime": int(stat.st_mtime), # 时间戳 (Timestamp)
                            "size": stat.st_size
                        })
                # 按修改时间降序排列 (按最新排序)
                profiles.sort(key=lambda x: x["mtime"], reverse=True)
                return self.send_json_response(200, {"success": True, "profiles": profiles})
            except Exception as e:
                return self.send_json_response(500, {"success": False, "error": str(e)})

        # 2. 加载特定配置方案 (Load a specific config profile)
        elif path == '/api/profiles/load':
            query_params = urllib.parse.parse_qs(parsed_path.query)
            if 'name' not in query_params:
                return self.send_json_response(400, {"success": False, "error": "Missing 'name' parameter."})
            
            profile_name = query_params['name'][0]
            if '..' in profile_name or '/' in profile_name:
                return self.send_json_response(400, {"success": False, "error": "Invalid profile name."})

            profile_file = PROFILES_DIR / f"{profile_name}.yaml"
            if not profile_file.exists():
                return self.send_json_response(404, {"success": False, "error": "Profile not found."})

            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 尝试解析为 JSON (试图判断是否是三合一方案)
                try:
                    data = json.loads(content)
                    return self.send_json_response(200, {"success": True, "type": "bundle", "data": data})
                except json.JSONDecodeError:
                    # 如果不是 JSON，说明是旧版仅 config.yaml 字符串方案
                    return self.send_json_response(200, {"success": True, "type": "legacy", "content": content})
            except Exception as e:
                return self.send_json_response(500, {"success": False, "error": str(e)})

        # 默认回退给静态文件服务器处理 (Fallback to static file server)
        return super().do_GET()

    def do_POST(self):
        """处理自定义 POST 路由 (Handle custom POST routes)"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        # 读取请求体 (Read request body)
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return self.send_json_response(400, {"success": False, "error": "Empty request body"})
            
        post_data = self.rfile.read(content_length)

        try:
            payload = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            return self.send_json_response(400, {"success": False, "error": "Invalid JSON format."})

        # 1. 保存主配置文件 (Apply/Save main configuration)
        if path == '/api/save':
            file_type = payload.get('file')
            content = payload.get('content')

            if not file_type or content is None:
                return self.send_json_response(400, {"success": False, "error": "Missing 'file' or 'content' in payload."})

            file_map = {
                'config': CONFIG_DIR / 'config.yaml',
                'frequency': CONFIG_DIR / 'frequency_words.txt',
                'timeline': CONFIG_DIR / 'timeline.yaml',
                'analysis_prompt': CONFIG_DIR / 'ai_analysis_prompt.txt',
                'translation_prompt': CONFIG_DIR / 'ai_translation_prompt.txt'
            }

            if file_type not in file_map:
                return self.send_json_response(400, {"success": False, "error": f"Invalid file type: {file_type}."})

            target_file = file_map[file_type]

            try:
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.send_json_response(200, {"success": True, "message": f"{target_file.name} saved successfully."})
            except Exception as e:
                self.send_json_response(500, {"success": False, "error": f"Failed to save {target_file.name}: {str(e)}"})

        # 2. 保存配置为新方案 (Save as a new profile)
        elif path == '/api/profiles/save':
            # 可以是字符串 (旧版兼容) 也可以是对象 (新版打包)
            content = payload.get('content') 
            name = payload.get('name', '').strip()

            if not content:
                return self.send_json_response(400, {"success": False, "error": "Profile content is empty."})

            if '..' in name or '/' in name:
                return self.send_json_response(400, {"success": False, "error": "Invalid characters in profile name."})

            if not name:
                now_str = datetime.now().strftime("%Y%m%d%H%M")
                name = f"{now_str}_AIYXDATA-TRADAR"
                
            new_profile_path = PROFILES_DIR / f"{name}.yaml"

            try:
                # 如果 content 是对象，存为 JSON 字符串
                if isinstance(content, dict):
                    to_write = json.dumps(content, ensure_ascii=False, indent=2)
                else:
                    to_write = str(content)

                with open(new_profile_path, 'w', encoding='utf-8') as f:
                    f.write(to_write)

                # 容量控制逻辑 (Capacity control logic: Limit to 5)
                # 获取所有 yaml 文件
                existing_profiles = list(PROFILES_DIR.glob('*.yaml'))
                if len(existing_profiles) > 5:
                    # 获取文件修改时间并排序，最早修改的在最前面
                    existing_profiles.sort(key=lambda x: x.stat().st_mtime)
                    # 需要删除的文件数
                    files_to_delete = existing_profiles[:len(existing_profiles)-5]
                    for f_del in files_to_delete:
                        try:
                            f_del.unlink()
                        except Exception as e:
                            print(f"[Warn] Failed to delete old profile {f_del.name}: {e}")

                return self.send_json_response(200, {"success": True, "message": f"Profile '{name}' saved successfully.", "name": name})
            except Exception as e:
                return self.send_json_response(500, {"success": False, "error": f"Failed to save profile: {str(e)}"})

        else:
            return self.send_json_response(404, {"success": False, "error": f"API endpoint {path} not found."})


def run(server_class=HTTPServer, handler_class=ConfigServerHandler, port=WEBSERVER_PORT, directory=WEBSERVER_DIR):
    """启动自定义服务器 (Start the custom server)"""
    # 更改工作目录以伺服带有前端文件的文件夹
    os.chdir(directory)
    
    # 绑定到 0.0.0.0 (Bind to all interfaces)
    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    
    print(f"✅ AIYXDATA-TRADAR 自定义配置服务器已启动 / Custom Config Web Server started")
    print(f"🌐 端口 / Port: {port}")
    print(f"📁 根目录 / Root Dir: {directory}")
    print(f"🔒 支持 API 保存功能 / Contains config save APIs")
    print("--------------------------------------------------")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        print("🛑 服务器已停止 / Web server stopped")


if __name__ == '__main__':
    run()
