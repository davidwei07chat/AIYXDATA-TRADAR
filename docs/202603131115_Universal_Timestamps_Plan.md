# 实施方案：全量文章显示日期时间 / Implementation Plan: Universal Article Timestamps

为了满足用户“所有显示链接的文章都要跟有日期时间”的需求，我们需要统一报告生成和渲染阶段的时间处理逻辑。
To meet the user requirement that "all article links must display timestamps," we need to unify the time processing logic during report generation and rendering.

## 拟议变更 / Proposed Changes

### 1. 报告生成层 (Report Generation Layer)
#### [MODIFY] [generator.py](file:///TrendRadar/aiyxdata_tradar/report/generator.py)
- 在 `prepare_report_data` 函数中，确保处理 `new_titles` 时正确从数据源提取时间信息并赋值给 `time_display`。
- Ensure `prepare_report_data` correctly extracts time info and populates `time_display` when processing `new_titles`.

### 2. HTML 渲染层 (HTML Rendering Layer)
#### [MODIFY] [html_v2.py](file:///TrendRadar/aiyxdata_tradar/report/html_v2.py)
- 在 `render_html_content_v2` 的主循环中，确保所有类型的区块（Keywords, Sources, RSS）在渲染新闻条目时都包含日期时间标签。
- 优化 CSS 样式以确保时间标签在移动端和网页端显示美观（例如：使用灰色字体、时钟图标）。
- Ensure all block types (Keywords, Sources, RSS) in `render_html_content_v2` include timestamp tags.
- Optimize CSS for elegant timestamp display (e.g., secondary color, clock icon).

#### [MODIFY] [rss_html.py](file:///TrendRadar/aiyxdata_tradar/report/rss_html.py)
- 更新 RSS 专用模板，确保每条新闻标题旁显式渲染 `published_at` 时间。
- Update the RSS-specific template to explicitly render `published_at` next to each article title.

---

## 验证计划 / Verification Plan

### 自动化验证 / Automated Verification
- 运行 `python3 /TrendRadar/docker/manage.py run` 生成新报告。
- Run `python3 /TrendRadar/docker/manage.py run` to generate a new report.
- 使用 `grep` 检查生成的 HTML 文件中是否包含 `🕒` 图标和时间字符串。
- Use `grep` to check generated HTML for `🕒` icons and time strings.

### 手动验证 / Manual Verification
- 请用户检查最新生成的报告页面，确认每一行新闻链接旁是否都出现了日期时间。
- Ask the user to check the newly generated report to confirm timestamps appear next to every news link.

---
**创建记录 (Creation Record)**: 2026-03-13 11:15, Antigravity, /TrendRadar/docs/202603131115 Universal_Timestamps_Plan.md
**技术栈 (Tech Stack)**: Python 3.10, HTML5/CSS3
