# (C) 2026 AIYXDATA. All rights reserved.
# Project: AIYXDATA-TRADAR

# coding=utf-8
"""
HTML 报告渲染模块 V2 (测试版) - 明亮科技风

提供更加现代、明亮、且具备增强交互能力的报告页面样式。
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from aiyxdata_tradar.report.helpers import html_escape
from aiyxdata_tradar.utils.time import convert_time_for_display

def render_html_content_v2(
    report_data: Dict,
    total_titles: int,
    mode: str = "daily",
    update_info: Optional[Dict] = None,
    *,
    region_order: Optional[List[str]] = None,
    get_time_func: Optional[Callable[[], datetime]] = None,
    rss_items: Optional[List[Dict]] = None,
    rss_new_items: Optional[List[Dict]] = None,
    display_mode: str = "keyword",
    standalone_data: Optional[Dict] = None,
    ai_analysis: Optional[Any] = None,
    show_new_section: bool = True,
) -> str:
    """渲染 HTML 内容 V2 (明亮科技风)"""
    
    # 颜色方案 (霓虹色系)
    NEON_COLORS = [
        "#00f2ff", # Cyan
        "#ff00ff", # Magenta
        "#39ff14", # Lime
        "#fff01f", # Yellow
        "#ff3131", # Red
        "#bc13fe", # Purple
        "#00d4ff", # Sky
    ]
    
    # 版本号逻辑
    now = get_time_func() if get_time_func else datetime.now()
    version_tag = f"V1.01.{now.strftime('%m%d')}"

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TrendRadar | {version_tag}</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=Noto+Sans+SC:wght@400;500;700;800&display=swap');

            :root {{
                --bg-color: #f7fafc;
                --card-bg: rgba(255, 255, 255, 0.85);
                --text-primary: #1e293b;
                --text-secondary: #64748b;
                --accent-cyan: #00f2ff;
                --accent-magenta: #ff00ff;
                --accent-lime: #39ff14;
                --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
                --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                --shadow-neon: 0 0 20px rgba(0, 242, 255, 0.2);
                --glass-bg: rgba(255, 255, 255, 0.7);
                --glass-border: rgba(255, 255, 255, 0.3);
                --header-bg: #ffffff;
            }}

            /* Solarized Light */
            [data-theme="solarized-light"] {{
                --bg-color: #fdf6e3;
                --card-bg: #eee8d5;
                --text-primary: #657b83;
                --text-secondary: #93a1a1;
                --header-bg: #eee8d5;
                --accent-cyan: #268bd2;
            }}

            /* Solarized Dark */
            [data-theme="solarized-dark"] {{
                --bg-color: #002b36;
                --card-bg: #073642;
                --text-primary: #839496;
                --text-secondary: #586e75;
                --header-bg: #073642;
                --accent-cyan: #268bd2;
            }}

            /* Nord */
            [data-theme="nord"] {{
                --bg-color: #2e3440;
                --card-bg: #3b4252;
                --text-primary: #d8dee9;
                --text-secondary: #94a3b8;
                --header-bg: #3b4252;
                --accent-cyan: #81a1c1;
            }}

            /* Dracula */
            [data-theme="dracula"] {{
                --bg-color: #282a36;
                --card-bg: #44475a;
                --text-primary: #f8f8f2;
                --text-secondary: #6272a4;
                --header-bg: #44475a;
                --accent-cyan: #ff79c6;
            }}

            /* Gruvbox */
            [data-theme="gruvbox"] {{
                --bg-color: #282828;
                --card-bg: #3c3836;
                --text-primary: #ebdbb2;
                --text-secondary: #928374;
                --header-bg: #3c3836;
                --accent-cyan: #fe8019;
            }}

            /* Monokai */
            [data-theme="monokai"] {{
                --bg-color: #272822;
                --card-bg: #3e3d32;
                --text-primary: #f8f8f2;
                --text-secondary: #75715e;
                --header-bg: #3e3d32;
                --accent-cyan: #f92672;
            }}

            /* Catppuccin */
            [data-theme="catppuccin"] {{
                --bg-color: #1e1e2e;
                --card-bg: #313244;
                --text-primary: #cdd6f4;
                --text-secondary: #a6adc8;
                --header-bg: #313244;
                --accent-cyan: #cba6f7;
            }}

            * {{ box-sizing: border-box; }}
            
            body {{
                font-family: 'Inter', 'Noto Sans SC', sans-serif;
                margin: 0;
                padding: 40px 20px;
                background-color: var(--bg-color);
                background-image: 
                    radial-gradient(at 0% 0%, rgba(0, 242, 255, 0.05) 0px, transparent 50%),
                    radial-gradient(at 100% 0%, rgba(255, 0, 255, 0.05) 0px, transparent 50%);
                color: var(--text-primary);
                line-height: 1.6;
                overflow-x: hidden;
            }}

            @keyframes fadeInUp {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}

            .container {{
                max-width: 1200px;
                margin: 0 auto;
                animation: fadeInUp 0.8s ease-out;
            }}

            /* Header Section - Inspired by User Reference */
            .header {{
                background: var(--header-bg);
                padding: 30px 40px;
                border-radius: 24px;
                box-shadow: var(--shadow-md);
                margin-bottom: 40px;
                position: relative;
                border-top: 6px solid var(--accent-cyan);
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 15px;
                z-index: 10; /* Lower than modal */
            }}

            .header-top-tag {{
                font-size: 11px;
                font-weight: 800;
                color: #3b82f6;
                letter-spacing: 2px;
                text-transform: uppercase;
            }}

            .header-main {{
                width: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
                position: relative;
                margin: 10px 0;
            }}

            .header-title-group {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}

            .header-title {{
                font-size: 36px;
                font-weight: 900;
                color: var(--text-primary);
                margin: 0;
                letter-spacing: -1px;
            }}

            .version-tag {{
                font-size: 13px;
                font-weight: 700;
                color: #94a3b8;
                background: #f1f5f9;
                padding: 2px 10px;
                border-radius: 6px;
            }}

            .header-buttons {{
                position: absolute;
                right: 0;
                display: flex;
                gap: 10px;
            }}

            .header-btn {{
                padding: 10px 20px;
                border-radius: 12px;
                font-size: 13px;
                font-weight: 700;
                border: 1px solid #e2e8f0;
                background: #ffffff;
                cursor: pointer;
                transition: all 0.2s;
                color: #475569;
                display: flex;
                align-items: center;
                gap: 6px;
            }}

            .header-btn:hover {{ background: #f8fafc; border-color: #cbd5e1; transform: translateY(-2px); }}
            
            /* Enhanced Button Colors - Image 3 Style */
            .header-btn-refresh {{ background: #00a8e8; color: white; border: none; }}
            .header-btn-refresh:hover {{ background: #0091c7; }}
            .header-btn-save {{ background: #ffffff; color: #475569; border: 1px solid #e2e8f0; }}
            .header-btn-save:hover {{ background: #f1f5f9; }}

            /* Floating Draggable Configuration Button */
            .floating-config-btn {{
                position: fixed;
                right: 30px;
                top: 50%;
                width: 56px;
                height: 56px;
                background: #00a8e8;
                color: white;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 15px rgba(0, 168, 232, 0.4);
                cursor: grab;
                z-index: 999;
                transition: transform 0.2s, box-shadow 0.2s;
                font-size: 20px;
            }}

            .floating-config-btn:hover {{
                transform: scale(1.1);
                box-shadow: 0 6px 20px rgba(0, 168, 232, 0.5);
            }}

            .floating-config-btn:active {{
                cursor: grabbing;
            }}

            .meta-box {{
                background: #f8fafc;
                border-radius: 16px;
                padding: 20px 40px;
                display: flex;
                gap: 50px;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
            }}

            .meta-entry {{
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 5px;
            }}

            .meta-key {{
                font-size: 10px;
                font-weight: 800;
                color: #94a3b8;
                letter-spacing: 1px;
                text-transform: uppercase;
            }}

            .meta-val {{
                font-size: 18px;
                font-weight: 800;
                color: #1e293b;
            }}

            /* Grid Layout for Cards */
            .cards-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 30px;
            }}

            /* Topic Card */
            .card {{
                background: #ffffff;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: var(--shadow-sm);
                display: flex;
                flex-direction: column;
                height: 600px; /* Slightly taller to show ~10 items */
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                border: 1px solid #f1f5f9;
            }}

            .card:hover {{
                transform: translateY(-8px);
                box-shadow: var(--shadow-md), 0 10px 20px rgba(0,0,0,0.05);
            }}

            .card-header {{
                padding: 20px 24px;
                background: #ffffff;
                border-bottom: 1px solid #f1f5f9;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-top: 5px solid #ddd;
            }}

            .card-title {{
                font-weight: 800;
                font-size: 18px;
                color: #0f172a;
                display: flex;
                align-items: center;
                gap: 10px;
            }}

            .card-count {{
                font-size: 13px;
                background: #f1f5f9;
                padding: 4px 12px;
                border-radius: 8px;
                color: #64748b;
                font-weight: 700;
            }}

            .card-body {{
                padding: 0;
                flex-grow: 1;
                overflow-y: auto;
                scrollbar-width: thin;
                scrollbar-color: #cbd5e1 transparent;
            }}

            .card-body::-webkit-scrollbar {{ width: 4px; }}
            .card-body::-webkit-scrollbar-track {{ background: transparent; }}
            .card-body::-webkit-scrollbar-thumb {{ background: #e2e8f0; border-radius: 10px; }}

            .news-list {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}

            .news-item {{
                padding: 16px 24px;
                border-bottom: 1px solid #f8fafc;
                display: flex;
                gap: 15px;
                transition: background 0.2s;
            }}

            .news-item:hover {{
                background: #fcfdfe;
            }}

            .news-item:last-child {{ border-bottom: none; }}

            .news-rank {{
                font-size: 14px;
                font-weight: 800;
                color: #e2e8f0;
                min-width: 24px;
                padding-top: 2px;
            }}

            .news-content {{
                flex: 1;
            }}

            .news-title-link {{
                font-size: 15px;
                font-weight: 700;
                color: #334155;
                text-decoration: none;
                transition: color 0.2s;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
                overflow: hidden;
                line-height: 1.5;
            }}

            .news-title-link:hover {{ color: #00a8e8; }}

            .news-meta {{
                display: flex;
                gap: 12px;
                margin-top: 6px;
                font-size: 12px;
                color: #94a3b8;
            }}

            .source-tag {{
                font-weight: 800;
                color: #94a3b8;
            }}

            .time-tag {{
                font-weight: 600;
                color: #64748b;
                display: inline-flex;
                align-items: center;
                gap: 4px;
            }}

            /* Light Styled AI Analysis Card (Bottom) */
            .ai-card {{
                width: 100%;
                background: rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(12px);
                color: #1e293b;
                padding: 0;
                border-radius: 24px;
                margin-top: 40px;
                margin-bottom: 30px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                box-shadow: var(--shadow-md);
            }}

            .ai-card .card-title {{ color: #0f172a; font-size: 24px; margin-bottom: 20px; display: block; }}
            .ai-content {{ 
                font-size: 16px; 
                color: #334155; 
                line-height: 1.8;
                letter-spacing: 0.3px;
                word-wrap: break-word;
            }}
            .ai-content p {{ margin-bottom: 1em; }}
            .ai-content h1, .ai-content h2, .ai-content h4, .ai-content h5 {{ color: #0f172a; margin-top: 1.5em; margin-bottom: 0.5em; font-weight: 600; }}
            .ai-content h3 {{
                color: #0f172a;
                margin-top: 25px;
                margin-bottom: 10px;
                border-left: 4px solid var(--accent-cyan);
                padding-left: 12px;
                font-weight: 600;
            }}
            .ai-content ul, .ai-content ol {{ padding-left: 20px; margin-bottom: 1em; }}
            .ai-content li {{ margin-bottom: 0.5em; }}
            .ai-content blockquote {{ border-left: 4px solid #cbd5e1; padding-left: 1em; color: #64748b; margin: 1em 0; }}
            .ai-content pre {{ padding: 12px; background-color: #f1f5f9; border-radius: 8px; overflow-x: auto; margin-bottom: 1em; font-size: 0.9em; }}
            .ai-content code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; background-color: #f1f5f9; padding: 0.2em 0.4em; border-radius: 4px; font-size: 0.9em; }}
            .ai-content pre code {{ background-color: transparent; padding: 0; }}
            .ai-error {{
                color: #ef4444;
                background: #fef2f2;
                border: 1px solid #fee2e2;
                padding: 15px 20px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .ai-error::before {{
                content: "⚠️";
                font-size: 18px;
            }}

            /* --- Search Styles --- */
            .search-container {{
                position: relative;
                width: 100%;
                max-width: 600px;
                margin: 0 auto;
            }}

            .search-input {{
                width: 100%;
                padding: 15px 45px 15px 50px;
                border-radius: 30px;
                border: 2px solid #e2e8f0;
                font-size: 16px;
                outline: none;
                transition: all 0.3s;
                background: #f8fafc;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
            }}

            .search-input:focus {{
                border-color: var(--accent-cyan);
                background: #ffffff;
                box-shadow: 0 0 0 4px rgba(0, 242, 255, 0.1);
            }}

            .search-icon {{
                position: absolute;
                left: 20px;
                top: 50%;
                transform: translateY(-50%);
                color: #94a3b8;
                font-size: 18px;
            }}

            .search-clear {{
                position: absolute;
                right: 20px;
                top: 50%;
                transform: translateY(-50%);
                color: #cbd5e1;
                cursor: pointer;
                font-size: 18px;
                display: none;
                transition: color 0.2s;
            }}
            .search-clear:hover {{ color: #f43f5e; }}

            #search-results-container {{
                margin-bottom: 40px;
            }}

            .search-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding: 0 20px;
            }}

            .search-header h2 {{
                font-size: 20px;
                color: #1e293b;
                display: flex;
                align-items: center;
                gap: 10px;
                margin: 0;
            }}

            .search-close-btn {{
                background: #f1f5f9;
                border: 1px solid #e2e8f0;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 600;
                color: #475569;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 6px;
            }}

            .search-close-btn:hover {{
                background: #e2e8f0;
                color: #0f172a;
            }}

            /* --- Visual Configuration Modal Styles --- */
            .modal-overlay {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: rgba(15, 23, 42, 0.6);
                backdrop-filter: blur(8px);
                z-index: 9999;
                display: none;
                justify-content: center;
                align-items: center;
            }}

            .modal-overlay.active-modal {{
                display: flex !important;
            }}

            .modal-window {{
                position: absolute;
                width: 90vw;
                height: 90vh;
                max-width: 1400px;
                background: white;
                border-radius: 24px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4);
                display: flex;
                flex-direction: column;
                overflow: hidden;
                resize: both;
                min-width: 800px;
                min-height: 500px;
                border: 1px solid #e2e8f0;
            }}

            .modal-header {{
                height: 60px;
                background: #1e293b;
                color: white;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 24px;
                cursor: move;
                user-select: none;
            }}

            .modal-title {{
                font-weight: 800;
                font-size: 16px;
                display: flex;
                align-items: center;
                gap: 12px;
            }}

            .modal-controls {{
                display: flex;
                gap: 12px;
            }}

            .action-btn {{
                width: 36px;
                height: 36px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.2s;
                color: #cbd5e1;
                background: rgba(255, 255, 255, 0.05);
            }}

            .action-btn:hover {{
                background: rgba(255, 255, 255, 0.15);
                color: white;
                transform: scale(1.1);
            }}

            .modal-body {{
                flex: 1;
                position: relative;
                background: #f8fafc;
            }}

            iframe#config-iframe {{
                width: 100%;
                height: 100%;
                border: none;
            }}

            .active-modal {{
                display: flex !important;
                animation: modalFadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            }}

            @keyframes modalFadeIn {{
                from {{ opacity: 0; transform: scale(0.95); }}
                to {{ opacity: 1; transform: scale(1); }}
            }}

            /* Controls Overlay Group (Mobile fallback) */
            .controls {{ display: none; }}

            #loading {{
                display: none;
                position: fixed;
                top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(255,255,255,0.9);
                backdrop-filter: blur(10px);
                z-index: 2000;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }}

            .spinner {{
                width: 60px; height: 60px;
                border: 5px solid #f1f5f9;
                border-top: 5px solid var(--accent-cyan);
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }}

            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}

            /* Print/Export hides */
            .is-exporting .controls {{ display: none !important; }}

            @media (max-width: 900px) {{
                .header-buttons {{ position: static; margin-top: 15px; }}
                .header-main {{ flex-direction: column; }}
                .meta-box {{ padding: 15px; gap: 20px; flex-wrap: wrap; justify-content: center; }}
            }}
        </style>
    </head>
    <body>
        <div id="loading">
            <div class="spinner"></div>
            <p style="margin-top: 20px; font-weight: 700; color: #1e293b;">同步中 / Synchronizing...</p>
        </div>

        <div class="floating-config-btn" id="floating-config-btn" title="可视化配置 / Config" onclick="openConfig()">
            <i class="fas fa-cog"></i>
        </div>

        <div class="container" id="main-content">
            <header class="header">
                <!-- Theme Switcher -->
                <div class="theme-switcher-container">
                    <i class="fa-solid fa-palette" style="color: var(--text-secondary); font-size: 14px;"></i>
                    <select id="theme-select" onchange="setTheme(this.value)">
                        <option value="default">默认主题 (Standard)</option>
                        <option value="solarized-light">Solarized Light</option>
                        <option value="solarized-dark">Solarized Dark</option>
                        <option value="nord">Nord</option>
                        <option value="dracula">Dracula</option>
                        <option value="gruvbox">Gruvbox</option>
                        <option value="monokai">Monokai</option>
                        <option value="catppuccin">Catppuccin</option>
                    </select>
                </div>
                <div class="header-top-tag">AIYX DATA TECH RADAR</div>
                <div class="header-main">
                    <div class="header-title-group">
                        <h1 class="header-title">DATA RADAR 热点分析</h1>
                        <span class="version-tag">{version_tag}</span>
                    </div>
                    <div class="header-buttons">
                        <button class="header-btn header-btn-refresh" onclick="triggerRefresh(this)">
                            <i class="fas fa-sync-alt"></i> 刷新数据 / Refresh
                        </button>
                        <button class="header-btn header-btn-save" onclick="exportLongImage()">
                            <i class="fas fa-image"></i> 保存图片 / Save
                        </button>
                    </div>
                </div>
                
                <div class="search-container">
                    <i class="fas fa-search search-icon"></i>
                    <input type="text" id="global-search" class="search-input" placeholder="输入关键词搜索历史资讯 (默认检索过去7天)..." autocomplete="off">
                    <i class="fas fa-times-circle search-clear" id="search-clear-btn" onclick="clearSearch()"></i>
                </div>
                
                <div class="meta-box" style="margin-top: 20px;">
                    <div class="meta-entry">
                        <span class="meta-key">NODE</span>
                        <span class="meta-val">{"当前榜单" if mode == "current" else "增量分析" if mode == "incremental" else "全天推总"}</span>
                    </div>
                    <div class="meta-entry">
                        <span class="meta-key">新闻总数</span>
                        <span class="meta-val">{total_titles} 条</span>
                    </div>
                    <div class="meta-entry">
                        <span class="meta-key">热点关键词</span>
                        <span class="meta-val">{len(report_data.get("stats", []))} 个</span>
                    </div>
                    <div class="meta-entry">
                        <span class="meta-key">生成时间</span>
                        <span class="meta-val">{now.strftime('%m-%d %H:%M')}</span>
                    </div>
                </div>
            </header>

            <!-- Search Results Container -->
            <div id="search-results-container" style="display: none;">
                <div class="search-header">
                    <h2><i class="fas fa-search"></i> 搜索结果: <span id="search-keyword-display"></span> (<span id="search-count-display">0</span> 条)</h2>
                    <button class="search-close-btn" onclick="clearSearch()"><i class="fas fa-times"></i> 关闭搜索</button>
                </div>
                <div class="cards-grid" id="search-cards-grid">
                    <!-- Search results will be injected here -->
                </div>
            </div>

            <div class="cards-grid" id="main-cards-grid">
    """

    # AI Analysis moved to after grid
    ai_html = ""
    if ai_analysis:
        if ai_analysis.success:
            # 整合多个 AI 分析维度
            ai_sections = []
            if ai_analysis.core_trends:
                ai_sections.append(f"### 🔥 核心热点与态势\n{ai_analysis.core_trends}")
            if ai_analysis.sentiment_controversy:
                ai_sections.append(f"### 🎭 舆情风向与争议\n{ai_analysis.sentiment_controversy}")
            if ai_analysis.signals:
                ai_sections.append(f"### 📡 异动与弱信号\n{ai_analysis.signals}")
            if ai_analysis.rss_insights:
                ai_sections.append(f"### 🗞️ RSS 深度洞察\n{ai_analysis.rss_insights}")
            if ai_analysis.outlook_strategy:
                ai_sections.append(f"### 🎯 研判与策略建议\n{ai_analysis.outlook_strategy}")

            full_ai_content = "\n\n".join(ai_sections)

            # Extract basic metadata
            ai_model = "Unknown"
            if ai_analysis and hasattr(ai_analysis, 'metadata') and isinstance(ai_analysis.metadata, dict):
                ai_model = ai_analysis.metadata.get("model", "Unknown")
            # For output readability, remove 'openai/' prefix if it was automatically injected
            display_model = ai_model.replace("openai/", "") if ai_model.startswith("openai/") else ai_model

            from datetime import datetime
            if get_time_func:
                report_time = get_time_func().strftime("%Y-%m-%d %H:%M:%S")
            else:
                report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            safe_full_ai_content = html_escape(full_ai_content)
            ai_html = f"""
                    <div class="card ai-card">
                        <div class="card-header" style="border-top-color: var(--accent-cyan)">
                            <span class="card-title">✨ AI 深度分析研判</span>
                            <div style="font-size: 12px; color: #888; user-select: none;">🕒 {report_time} &nbsp;|&nbsp; 🤖 {display_model}</div>
                        </div>
                        <div class="card-body">
                            <textarea id="raw-ai-content" style="display:none;">{safe_full_ai_content}</textarea>
                            <div id="rendered-ai-content" class="ai-content markdown-body" style="padding: 30px;"></div>
                        </div>
                    </div>
                    <script>
                        document.addEventListener("DOMContentLoaded", function() {{
                            if (typeof marked !== 'undefined') {{
                                const rawText = document.getElementById('raw-ai-content').value;
                                document.getElementById('rendered-ai-content').innerHTML = marked.parse(rawText);
                            }} else {{
                                document.getElementById('rendered-ai-content').innerText = document.getElementById('raw-ai-content').value;
                            }}
                        }});
                    </script>
            """
        else:
            # 渲染错误信息
            error_msg = ai_analysis.error or "未知错误 (Unknown Error)"
            ai_html = f"""
                    <div class="card ai-card">
                        <div class="card-title">✨ AI 深度分析研判</div>
                        <div class="ai-content">
                            <div class="ai-error">{html_escape(str(error_msg))}</div>
                        </div>
                    </div>
            """

    # --- Section: News Cards (Dynamic) ---
    # Merge Stats and Standalone Data for unified card rendering
    all_blocks = []
    
    # Keyword blocks
    for idx, stat in enumerate(report_data.get("stats", [])):
        if stat["count"] > 0:
            all_blocks.append({
                "title": stat["word"],
                "count": stat["count"],
                "titles": stat["titles"],
                "type": "keyword"
            })

    # Standalone Platforms
    if standalone_data and "platforms" in standalone_data:
        for p in standalone_data["platforms"]:
            all_blocks.append({
                "title": p['name'],
                "count": len(p['items']),
                "titles": p['items'],
                "type": "source"
            })

    # RSS Feeds
    if standalone_data and "rss_feeds" in standalone_data:
        for r in standalone_data["rss_feeds"]:
            all_blocks.append({
                "title": r['name'],
                "count": len(r['items']),
                "titles": r['items'],
                "type": "rss"
            })

    # Render Blocks
    for idx, block in enumerate(all_blocks):
        color = NEON_COLORS[idx % len(NEON_COLORS)]
        icon = "🔥" if block['type'] == 'keyword' else "🌐" if block['type'] == 'source' else "🗞️"
        html += f"""
                <div class="card">
                    <div class="card-header" style="border-top-color: {color}">
                        <span class="card-title"><span style="color: {color}">{icon}</span> {block['title']}</span>
                        <span class="card-count">{block['count']} items</span>
                    </div>
                    <div class="card-body">
                        <ul class="news-list">
        """
        
        # NO LIMIT - Show all items, scroll will handle overflow
        display_titles = block["titles"]
        for i, news in enumerate(display_titles):
            title = news.get("title", "Untitled")
            url = news.get("url", "#")
            source = news.get("source_name") or block['title']
            
            html += f"""
                            <li class="news-item">
                                <span class="news-rank">{i+1:02d}</span>
                                <div class="news-content">
                                    <a href="{url}" class="news-title-link" target="_blank">{html_escape(title)}</a>
                                    <div class="news-meta">
                                        <span class="source-tag">{source}</span>
                                        {f'<span class="time-tag" style="margin-left: 10px;">🕒 {news["time_display"]}</span>' if news.get("time_display") else ''}
                                    </div>
                                </div>
                            </li>
            """
        
        html += """
                        </ul>
                    </div>
                </div>
        """

    html += f"""
            </div><!-- end cards-grid -->
            
            {ai_html}
            
            <footer style="margin-top: 50px; text-align: center; color: #94a3b8; font-size: 13px; padding-bottom: 50px;">
                TrendRadar AI Data Top &copy; 2026 Powered by AIYX Data Tech
            </footer>
        </div>

        <div class="controls">
            <button class="btn btn-refresh" onclick="triggerRefresh()">
                <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                刷新数据
            </button>
            <button class="btn btn-image" onclick="exportLongImage()">
                <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                导出长图
            </button>
        </div>

        <script>
            function triggerRefresh() {{
                document.getElementById('loading').style.display = 'flex';
                fetch('/api/refresh', {{ 
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{}})
                }})
                    .then(r => r.json())
                    .then(data => {{
                        if(data.success) {{
                            window.location.reload();
                        }} else {{
                            alert('Refresh failed: ' + data.error);
                            document.getElementById('loading').style.display = 'none';
                        }}
                    }})
                    .catch(e => {{
                        console.error(e);
                        document.getElementById('loading').style.display = 'none';
                    }});
            }}

            async function exportLongImage() {{
                const body = document.body;
                body.classList.add('is-exporting');
                
                try {{
                    const canvas = await html2canvas(document.getElementById('main-content'), {{
                        useCORS: true,
                        scale: 2,
                        backgroundColor: '#f0f4f8'
                    }});
                    
                    const link = document.createElement('a');
                    link.download = `TrendRadar_Report_${{new Date().getTime()}}.png`;
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                }} catch (e) {{
                    console.error('Export failed', e);
                }} finally {{
                    body.classList.remove('is-exporting');
                }}
            }}

        // --- Theme Management ---
        function setTheme(theme) {{
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('aiyxdata_tradar-theme', theme);
            const select = document.getElementById('theme-select');
            if (select) select.value = theme;
        }}

        document.addEventListener('DOMContentLoaded', () => {{
            const savedTheme = localStorage.getItem('aiyxdata_tradar-theme') || 'default';
            setTheme(savedTheme);
        }});

        // --- Visual Configuration Modal Logic ---
        function openConfig() {{
            try {{
                const overlay = document.getElementById('config-overlay');
                if (overlay) {{
                    overlay.classList.add('active-modal');
                    console.log('Modal opened successfully');
                }} else {{
                    console.error('Config overlay element not found');
                    alert('Error: Config overlay not found');
                }}
            }} catch (e) {{
                console.error('Failed to open config', e);
                alert('JS Error: ' + e.message);
            }}
        }}

        function closeConfig() {{
            const overlay = document.getElementById('config-overlay');
            if (overlay) overlay.classList.remove('active-modal');
        }}

        // Draggable Modal Logic
        (function() {{
            const modal = document.getElementById('config-modal');
            const handle = document.getElementById('modal-drag-handle');
            let isDragging = false;
            let offsetModalX, offsetModalY;

            handle.addEventListener('mousedown', (e) => {{
                if (e.target.closest('.action-btn')) return;
                isDragging = true;
                offsetModalX = e.clientX - modal.offsetLeft;
                offsetModalY = e.clientY - modal.offsetTop;
                document.addEventListener('mousemove', onMouseMove);
                document.addEventListener('mouseup', onMouseUp);
                document.body.style.userSelect = 'none';
            }});

            function onMouseMove(e) {{
                if (!isDragging) return;
                let left = e.clientX - offsetModalX;
                let top = e.clientY - offsetModalY;
                left = Math.max(0, Math.min(left, window.innerWidth - modal.offsetWidth));
                top = Math.max(0, Math.min(top, window.innerHeight - modal.offsetHeight));
                modal.style.left = left + 'px';
                modal.style.top = top + 'px';
                modal.style.margin = '0';
            }}

            function onMouseUp() {{
                isDragging = false;
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
                document.body.style.userSelect = 'auto';
            }}
        }})();
        // Floating Config Button Drag Logic
        (function() {{
            const btn = document.getElementById('floating-config-btn');
            let isDragging = false;
            let startY;
            let startTop;

            btn.addEventListener('mousedown', (e) => {{
                isDragging = false; // Reset dragging state on mousedown
                startY = e.clientY;
                startTop = btn.offsetTop;
                
                function onMouseMove(e) {{
                    if (Math.abs(e.clientY - startY) > 5) {{
                        isDragging = true;
                        let top = startTop + (e.clientY - startY);
                        // Boundary check
                        top = Math.max(0, Math.min(top, window.innerHeight - 60));
                        btn.style.top = top + 'px';
                        btn.style.bottom = 'auto'; // Disable bottom centering
                    }}
                }}

                function onMouseUp() {{
                    document.removeEventListener('mousemove', onMouseMove);
                    document.removeEventListener('mouseup', onMouseUp);
                    // If we weren't dragging, it's a click
                    if (!isDragging) {{
                        openConfig();
                    }}
                }}

                document.addEventListener('mousemove', onMouseMove);
                document.addEventListener('mouseup', onMouseUp);
            }});
        }})();

        // --- Search Functionality ---
        let searchTimeout = null;
        
        document.addEventListener('DOMContentLoaded', () => {{
            const searchInput = document.getElementById('global-search');
            const clearBtn = document.getElementById('search-clear-btn');
            
            if (searchInput) {{
                searchInput.addEventListener('input', (e) => {{
                    const kw = e.target.value.trim();
                    if (clearBtn) {{
                        clearBtn.style.display = kw.length > 0 ? 'block' : 'none';
                    }}
                    
                    if (searchTimeout) clearTimeout(searchTimeout);
                    
                    if (kw.length === 0) {{
                        clearSearch();
                        return;
                    }}
                    
                    searchTimeout = setTimeout(() => {{
                        performSearch(kw);
                    }}, 500); // 500ms debounce
                }});
                
                // Also trigger search on Enter, bypassing debounce
                searchInput.addEventListener('keydown', (e) => {{
                    if (e.key === 'Enter') {{
                        e.preventDefault();
                        const kw = e.target.value.trim();
                        if (searchTimeout) clearTimeout(searchTimeout);
                        if (kw.length > 0) {{
                            performSearch(kw);
                        }} else {{
                            clearSearch();
                        }}
                    }}
                }});
            }}
        }});
        
        function clearSearch() {{
            const searchInput = document.getElementById('global-search');
            const clearBtn = document.getElementById('search-clear-btn');
            const searchResultsContainer = document.getElementById('search-results-container');
            const mainCardsGrid = document.getElementById('main-cards-grid');
            
            if (searchInput) searchInput.value = '';
            if (clearBtn) clearBtn.style.display = 'none';
            if (searchResultsContainer) searchResultsContainer.style.display = 'none';
            if (mainCardsGrid) mainCardsGrid.style.display = 'grid'; // Restore main grid
        }}
        
        function performSearch(keyword) {{
            const searchResultsContainer = document.getElementById('search-results-container');
            const mainCardsGrid = document.getElementById('main-cards-grid');
            const searchCardsGrid = document.getElementById('search-cards-grid');
            const kwDisplay = document.getElementById('search-keyword-display');
            const countDisplay = document.getElementById('search-count-display');
            
            // Show loading
            document.getElementById('loading').style.display = 'flex';
            
            fetch('/api/search?kw=' + encodeURIComponent(keyword))
                .then(r => r.json())
                .then(data => {{
                    document.getElementById('loading').style.display = 'none';
                    if (data.success) {{
                        if (mainCardsGrid) mainCardsGrid.style.display = 'none';
                        if (searchResultsContainer) searchResultsContainer.style.display = 'block';
                        
                        if (kwDisplay) kwDisplay.textContent = String(keyword).replace(/</g, '&lt;').replace(/>/g, '&gt;');
                        if (countDisplay) countDisplay.textContent = data.count || 0;
                        
                        renderSearchResults(data.data, searchCardsGrid);
                    }} else {{
                        alert('搜索失败/Search failed: ' + (data.error || 'Unknown Error'));
                    }}
                }})
                .catch(e => {{
                    console.error('Search error:', e);
                    document.getElementById('loading').style.display = 'none';
                    alert('网络或服务器错误/Network or Server Error');
                }});
        }}
        
        function renderSearchResults(dataObj, container) {{
            if (!container) return;
            container.innerHTML = '';
            
            const neonColors = ["#00f2ff", "#ff00ff", "#39ff14", "#fff01f", "#ff3131", "#bc13fe", "#00d4ff"];
            let idx = 0;
            
            for (const dateStr in dataObj) {{
                if (!dataObj.hasOwnProperty(dateStr)) continue;
                const items = dataObj[dateStr];
                if (!items || items.length === 0) continue;
                
                const color = neonColors[idx % neonColors.length];
                idx++;
                
                const card = document.createElement('div');
                card.className = 'card';
                
                let listHtml = '<ul class="news-list">';
                items.forEach((news, i) => {{
                    const title = news.title || 'Untitled';
                    const url = news.url || '#';
                    const source = news.source_name || 'News';
                    const timeDisp = news.time_display || '';
                    
                    const safeTitle = String(title).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                    const safeUrl = String(url).replace(/"/g, '&quot;');
                    
                    const timeHtml = timeDisp ? '<span class="time-tag" style="margin-left: 10px;">🕒 ' + timeDisp + '</span>' : '';
                    const rankStr = (i+1).toString().padStart(2, '0');
                    
                    listHtml += '<li class="news-item">';
                    listHtml += '    <span class="news-rank">' + rankStr + '</span>';
                    listHtml += '    <div class="news-content">';
                    listHtml += '        <a href="' + safeUrl + '" class="news-title-link" target="_blank">' + safeTitle + '</a>';
                    listHtml += '        <div class="news-meta">';
                    listHtml += '            <span class="source-tag">' + String(source).replace(/</g, '&lt;') + '</span>';
                    listHtml += '            ' + timeHtml;
                    listHtml += '        </div>';
                    listHtml += '    </div>';
                    listHtml += '</li>';
                }});
                listHtml += '</ul>';
                
                card.innerHTML = '<div class="card-header" style="border-top-color: ' + color + '">' +
                                 '<span class="card-title"><span style="color: ' + color + '">📅</span> ' + dateStr + '</span>' +
                                 '<span class="card-count">' + items.length + ' items</span>' +
                                 '</div>' +
                                 '<div class="card-body">' + listHtml + '</div>';
                
                container.appendChild(card);
            }}
            
            if (idx === 0) {{
                container.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; font-weight: 600; color: #64748b; padding: 60px;">暂无相关搜索结果 / No results found</div>';
            }}
        }}
    </script>
        </div>

        <!-- Visual Configuration Modal Container -->
        <div class="modal-overlay" id="config-overlay">
            <div class="modal-window" id="config-modal">
                <div class="modal-header" id="modal-drag-handle">
                    <div class="modal-title">
                        <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                        </svg>
                        TrendRadar 可视化配置中心 / Config Center
                    </div>
                    <div class="modal-controls">
                        <div class="action-btn" title="刷新报告 / Refresh Report" onclick="location.reload()">
                            <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                            </svg>
                        </div>
                        <div class="action-btn" title="关闭面板 / Close Panel" onclick="closeConfig()">
                            <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                <path d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </div>
                    </div>
                </div>
                <div class="modal-body">
                    <iframe id="config-iframe" src="config_editor/index.html"></iframe>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html
