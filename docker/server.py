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
import re
import random
import html
import uuid
import datetime as datetime_module

# Web 服务器配置 (Web Server Config)
WEBSERVER_PORT = int(os.environ.get("WEBSERVER_PORT", "8080"))

# 路径探测逻辑 (Path detection logic)
def detect_path(env_key, default_paths):
    env_val = os.environ.get(env_key)
    if env_val:
        return env_val
    for p in default_paths:
        if os.path.exists(p):
            return p
    return default_paths[0]

WEBSERVER_DIR = detect_path("WEBSERVER_DIR", ["/app/output", "/AIYXDATA-TRADAR/output", "/TrendRadar/output", "./output"])
CONFIG_DIR = Path(detect_path("CONFIG_DIR", ["/TrendRadar/config", "/app/config", "/AIYXDATA-TRADAR/config", "./config"]))
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

    def get_data_version(self):
        """获取数据版本时间戳 (Get data version timestamp)"""
        try:
            latest_time = None
            db_dirs = [Path("/app/output/rss"), Path("/app/output/news")]

            for db_dir in db_dirs:
                if not db_dir.exists():
                    continue
                for db_file in db_dir.glob("*.db"):
                    mtime = db_file.stat().st_mtime
                    if latest_time is None or mtime > latest_time:
                        latest_time = mtime

            if latest_time:
                return datetime.fromtimestamp(latest_time).isoformat()
            return datetime.now().isoformat()
        except Exception as e:
            print(f"[API] 获取数据版本出错: {e}")
            return datetime.now().isoformat()

    def search_database(self, keywords, days):
        """搜索数据库 (Search database)"""
        try:
            # 简单实现：返回空结果
            # 实际应用中应连接真实数据库
            return {}
        except Exception as e:
            print(f"[API] 搜索数据库出错: {e}")
            return None

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
                'frequency_words': CONFIG_DIR / 'frequency_words.txt',
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

        # 3. 实时关键词搜索 (Real-time keyword search)
        elif path == '/api/search':
            query_params = urllib.parse.parse_qs(parsed_path.query)
            keyword = query_params.get('kw', [''])[0].strip()
            days = int(query_params.get('days', ['3650'])[0])  # 默认10年以获取所有数据

            if not keyword or len(keyword) > 100:
                return self.send_json_response(400, {"success": False, "error": "Invalid keyword"})

            try:
                import sqlite3
                from datetime import datetime, timedelta

                # 分割多关键词
                keywords = [k.strip() for k in keyword.split() if k.strip()]
                if not keywords:
                    return self.send_json_response(400, {"success": False, "error": "Empty keywords"})

                # 计算时间范围
                now = datetime.now()
                days_ago = now - timedelta(days=max(1, min(days, 3650)))
                days_ago_timestamp = int(days_ago.timestamp())  # 秒级时间戳

                # 搜索数据库
                all_results = []

                # 查找所有数据库文件
                db_dirs = [
                    Path(WEBSERVER_DIR) / "rss",
                    Path(WEBSERVER_DIR) / "news"
                ]

                db_files = []
                for db_dir in db_dirs:
                    if db_dir.exists():
                        db_files.extend(db_dir.glob("*.db"))

                # 搜索所有数据库
                for db_path in sorted(db_files, reverse=True):
                    try:
                        conn = sqlite3.connect(str(db_path))
                        conn.row_factory = sqlite3.Row
                        cursor = conn.cursor()

                        # 检查表结构
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                        tables = [t[0] for t in cursor.fetchall()]

                        # 执行搜索 - 支持多关键词
                        for kw in keywords:
                            if 'rss_items' in tables:
                                # RSS数据库结构
                                query = """
                                SELECT i.title, i.url, i.feed_id, f.name as source, i.published_at
                                FROM rss_items i
                                LEFT JOIN rss_feeds f ON i.feed_id = f.id
                                WHERE (i.title LIKE ? OR i.summary LIKE ?)
                                AND i.published_at >= ?
                                ORDER BY i.published_at DESC
                                """
                                params = (f'%{kw}%', f'%{kw}%', days_ago.isoformat())
                            elif 'news_items' in tables:
                                # News数据库结构
                                query = """
                                SELECT i.title, i.url, i.platform_id, p.name as source, i.first_crawl_time as published_at
                                FROM news_items i
                                LEFT JOIN platforms p ON i.platform_id = p.id
                                WHERE (i.title LIKE ?)
                                AND i.first_crawl_time >= ?
                                ORDER BY i.first_crawl_time DESC
                                """
                                params = (f'%{kw}%', days_ago.isoformat())
                            else:
                                continue

                            cursor.execute(query, params)
                            rows = cursor.fetchall()

                            for row in rows:
                                all_results.append({
                                    'title': row['title'],
                                    'url': row['url'],
                                    'source_name': row['source'] or row.get('feed_id') or row.get('platform_id'),
                                    'published_at': row['published_at']
                                })

                        conn.close()
                    except Exception as e:
                        print(f"[API] 搜索数据库 {db_path} 出错: {e}")

                # 去重
                seen = set()
                unique_results = []
                for item in all_results:
                    key = (item['title'], item['url'])
                    if key not in seen:
                        seen.add(key)
                        unique_results.append(item)

                # 按时间排序
                unique_results.sort(key=lambda x: x['published_at'], reverse=True)

                # 按source_name分组
                items_dict = {}
                for item in unique_results:
                    source = item['source_name']
                    if source not in items_dict:
                        items_dict[source] = []
                    items_dict[source].append(item)

                return self.send_json_response(200, {
                    "success": True,
                    "data": items_dict,
                    "count": len(unique_results),
                    "keywords": keywords,
                    "search_time": datetime.now().isoformat(),
                    "data_version": self.get_data_version()
                })
            except Exception as e:
                import traceback
                print(f"[API] 搜索功能出错: {e}")
                traceback.print_exc()
                return self.send_json_response(500, {"success": False, "error": str(e)})

        # 4. 搜索历史 (Search history)
        elif path == '/api/search_history':
            try:
                history_file = Path(WEBSERVER_DIR) / "data" / "search_history.json"

                # GET: 获取搜索历史
                if self.command == 'GET':
                    if not history_file.exists():
                        return self.send_json_response(200, {"success": True, "searches": []})

                    with open(history_file, 'r', encoding='utf-8') as f:
                        loaded = json.load(f)

                    # Handle both old array format and new object format
                    if isinstance(loaded, list):
                        searches = loaded
                    else:
                        searches = loaded.get("searches", [])

                    return self.send_json_response(200, {
                        "success": True,
                        "searches": searches[-20:] if len(searches) > 20 else searches
                    })

                # POST: 保存搜索历史
                elif self.command == 'POST':
                    content_length = int(self.headers.get('Content-Length', 0))
                    body = self.rfile.read(content_length).decode('utf-8')
                    data = json.loads(body)
                    keyword = data.get('keyword', '').strip()

                    if not keyword:
                        return self.send_json_response(400, {"success": False, "error": "Empty keyword"})

                    # 创建data目录
                    history_file.parent.mkdir(parents=True, exist_ok=True)

                    # 读取现有历史
                    searches = []
                    if history_file.exists():
                        with open(history_file, 'r', encoding='utf-8') as f:
                            loaded = json.load(f)
                        if isinstance(loaded, list):
                            searches = loaded
                        else:
                            searches = loaded.get("searches", [])

                    # 添加新搜索记录
                    new_search = {
                        "keyword": keyword,
                        "timestamp": datetime.now().isoformat()
                    }
                    searches.insert(0, new_search)

                    # 保存历史（最多保留50条）
                    with open(history_file, 'w', encoding='utf-8') as f:
                        json.dump({"searches": searches[:50]}, f, ensure_ascii=False, indent=2)

                    return self.send_json_response(200, {"success": True})

            except Exception as e:
                return self.send_json_response(500, {"success": False, "error": str(e)})

        # 5. 获取报告详情 (Get report details)
        elif path.startswith('/api/report/'):
            try:
                report_id = path.split('/')[-1]

                # 验证报告ID格式（防止路径遍历）
                if not re.match(r'^report_\d{8}_\d{6}_\d{4}$', report_id):
                    return self.send_json_response(400, {"success": False, "error": "Invalid report ID"})

                report_file = Path(WEBSERVER_DIR) / "data" / "reports" / f"{report_id}.json"

                if not report_file.exists():
                    return self.send_json_response(404, {"success": False, "error": "Report not found"})

                with open(report_file, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)

                return self.send_json_response(200, {
                    "success": True,
                    "data": report_data
                })
            except Exception as e:
                return self.send_json_response(500, {"success": False, "error": str(e)})
        return super().do_GET()

    def do_POST(self):
        """处理自定义 POST 路由 (Handle custom POST routes)"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        # 读取请求体 (Read request body)
        content_length = int(self.headers.get('Content-Length', 0))
        # 针对 refresh 允许空 body (Allow empty body specifically for refresh)
        if content_length == 0 and path != '/api/refresh':
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
                # 后端自动兜底逻辑 (Backend auto-fix logic)
                # 针对 glm-* 系列模型，如果缺失 zhipu/ 前缀则自动补全，防止 LiteLLM 报错
                if file_type == 'config':
                    content = re.sub(r'(model:\s*)"(glm-[^"]+)"', r'\1"zhipu/\2"', content)
                    content = re.sub(r'(model:\s*)(glm-\S+)', r'\1zhipu/\2', content)

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

        # 3. 刷新数据 (Refresh data)
        elif path == '/api/refresh':
            try:
                import subprocess
                # 触发单次抓取与报告生成 (Trigger single crawl and report generation)
                # 使用 nohup 避免阻塞 (Use nohup to avoid blocking)
                cmd = ["python3", os.path.abspath(__file__).replace("server.py", "manage.py"), "run"]
                subprocess.Popen(cmd)
                return self.send_json_response(200, {"success": True, "message": "Backend refresh triggered."})
            except Exception as e:
                return self.send_json_response(500, {"success": False, "error": str(e)})

        # 4. 检查 AI 连接 (Check AI Connection)
        elif path == '/api/check_ai_connection':
            api_base = payload.get('api_base') or "https://api.openai.com/v1"
            api_key = payload.get('api_key')

            if not api_key:
                return self.send_json_response(400, {"success": False, "error": "Missing API Key"})

            try:
                import requests
                # 遵循 OpenAI 规范的简单模型列表请求 (Simple models list request following OpenAI spec)
                base_url = api_base.rstrip('/')
                check_url = f"{base_url}/models"
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }

                # 发送测试请求 (Send test request)
                response = requests.get(check_url, headers=headers, timeout=10)
                
                # 如果 /models 不存在 (404)，尝试以最小代价请求 /chat/completions 进行验证
                if response.status_code == 404:
                    chat_url = f"{base_url}/chat/completions"
                    chat_payload = {
                        "model": payload.get('model') or "gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": "hi"}],
                        "max_tokens": 1
                    }
                    response = requests.post(chat_url, headers=headers, json=chat_payload, timeout=10)

                if response.status_code == 200:
                    return self.send_json_response(200, {"success": True, "message": "连接成功 / Connection Successful"})
                else:
                    try:
                        err_data = response.json()
                        err_msg = err_data.get('error', {}).get('message', response.text)
                    except:
                        err_msg = response.text
                    return self.send_json_response(200, {"success": False, "error": f"API 响应错误 ({response.status_code}): {err_msg[:200]}"})
            except Exception as e:
                return self.send_json_response(200, {"success": False, "error": f"连接失败 / Connection Failed: {str(e)}"})

        # 5. 获取 AI 模型列表 (Get AI Model List)
        elif path == '/api/get_ai_models':
            api_base = payload.get('api_base') or "https://api.openai.com/v1"
            api_key = payload.get('api_key')

            if not api_key:
                return self.send_json_response(400, {"success": False, "error": "Missing API Key"})

            try:
                import requests
                base_url = api_base.rstrip('/')
                check_url = f"{base_url}/models"
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }

                response = requests.get(check_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    # 提取模型 ID (Extract model IDs)
                    models = []
                    if isinstance(data, dict) and 'data' in data:
                        for m in data['data']:
                            if isinstance(m, dict) and 'id' in m:
                                models.append(m['id'])
                    elif isinstance(data, list):
                        # 兼容某些非标准返回 (Compat for non-standard returns)
                        for m in data:
                            if isinstance(m, dict) and 'id' in m:
                                models.append(m['id'])
                    
                    # 按字母排序 (Sort alphabetically)
                    models.sort()
                    return self.send_json_response(200, {"success": True, "models": models})
                else:
                    return self.send_json_response(200, {"success": False, "error": f"API 返回错误 ({response.status_code})"})
            except Exception as e:
                return self.send_json_response(200, {"success": False, "error": f"获取失败: {str(e)}"})

        # 6. 生成报告 (Generate Report)
        elif path == '/api/generate_report':
            try:
                keywords = payload.get('keywords', [])
                days = payload.get('days', 7)

                if not keywords or not isinstance(keywords, list):
                    return self.send_json_response(400, {"success": False, "error": "Invalid keywords"})

                keywords = [kw.strip() for kw in keywords if isinstance(kw, str) and kw.strip()]
                if not keywords:
                    return self.send_json_response(400, {"success": False, "error": "Empty keywords"})

                if not isinstance(days, int) or days < 1 or days > 30:
                    return self.send_json_response(400, {"success": False, "error": "Days must be 1-30"})

                # 执行搜索 (Execute search with same logic as /api/search)
                import sqlite3
                from datetime import datetime, timedelta

                now = datetime.now()
                days_ago = now - timedelta(days=max(1, min(days, 30)))
                days_ago_str = days_ago.isoformat()

                all_results = []
                db_dirs = [Path("/app/output/rss"), Path("/app/output/news")]

                for db_dir in db_dirs:
                    if not db_dir.exists():
                        continue

                    for db_file in sorted(db_dir.glob("*.db"), reverse=True):
                        try:
                            conn = sqlite3.connect(str(db_file))
                            conn.row_factory = sqlite3.Row
                            cursor = conn.cursor()

                            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rss_items';")
                            if not cursor.fetchone():
                                conn.close()
                                continue

                            for kw in keywords:
                                query = """
                                SELECT title, url, feed_id as source_name, published_at
                                FROM rss_items
                                WHERE title LIKE ?
                                AND published_at >= ?
                                ORDER BY published_at DESC
                                """
                                cursor.execute(query, (f'%{kw}%', days_ago_str))
                                rows = cursor.fetchall()

                                for row in rows:
                                    all_results.append({
                                        'title': row['title'],
                                        'url': row['url'],
                                        'source_name': row['source_name'],
                                        'published_at': row['published_at']
                                    })

                            conn.close()
                        except Exception as e:
                            print(f"[API] 搜索数据库出错 {db_file}: {e}")
                            continue

                # 去重
                seen = set()
                unique_results = []
                for item in all_results:
                    key = (item['title'], item['url'])
                    if key not in seen:
                        seen.add(key)
                        unique_results.append(item)

                # 按时间排序
                unique_results.sort(key=lambda x: x['published_at'], reverse=True)

                # 按source_name分组
                search_results = {}
                for item in unique_results:
                    source = item['source_name']
                    if source not in search_results:
                        search_results[source] = []
                    search_results[source].append(item)

                # 生成报告ID
                report_id = f"report_{now.strftime('%Y%m%d')}_{now.strftime('%H%M%S')}_{random.randint(1000, 9999)}"

                # 准备报告数据
                report_data = {
                    "id": report_id,
                    "keywords": keywords,
                    "days": days,
                    "created_at": now.isoformat(),
                    "data_version": self.get_data_version(),
                    "result_count": len(unique_results),
                    "results": search_results
                }

                # 保存报告
                reports_dir = Path(WEBSERVER_DIR) / "data" / "reports"
                reports_dir.mkdir(parents=True, exist_ok=True)

                report_file = reports_dir / f"{report_id}.json"
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, ensure_ascii=False, indent=2)

                # 更新搜索历史
                history_file = Path(WEBSERVER_DIR) / "data" / "search_history.json"
                history_data = {"searches": []}

                if history_file.exists():
                    with open(history_file, 'r', encoding='utf-8') as f:
                        loaded = json.load(f)
                        # Handle both old array format and new object format
                        if isinstance(loaded, list):
                            history_data = {"searches": loaded}
                        else:
                            history_data = loaded

                history_data["searches"].insert(0, {
                    "id": report_id,
                    "keywords": keywords,
                    "created_at": now.isoformat(),
                    "result_count": report_data["result_count"],
                    "days": days
                })

                # 保留最近100条记录
                history_data["searches"] = history_data["searches"][:100]

                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump(history_data, f, ensure_ascii=False, indent=2)

                return self.send_json_response(200, {
                    "success": True,
                    "report_id": report_id,
                    "report_url": f"/report.html?id={report_id}",
                    "result_count": report_data["result_count"]
                })
            except Exception as e:
                import traceback
                print(f"[API] 生成报告出错: {e}")
                traceback.print_exc()
                return self.send_json_response(500, {"success": False, "error": str(e)})

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
