import sys
try:
    from aiyxdata_tradar.report.html_v2 import render_html_content_v2
    render_html_content_v2({}, 0, 'daily', {})
except Exception as e:
    import traceback
    traceback.print_exc()
