import sys
try:
    from aiyxdata_tradar.report.html_v2 import render_html_content_v2
    import datetime
    render_html_content_v2({}, 0, 'daily', {}, get_time_func=lambda: datetime.datetime.now())
except Exception as e:
    import traceback
    traceback.print_exc()
