import os
from datetime import datetime
from violation_logger import LOG_DIR

REPORT_DIR = 'reports'

def ensure_report_dir():
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

def generate_report(student_id):
    ensure_report_dir()
    log_file = os.path.join(LOG_DIR, f'{student_id}_violations.log')
    report_path = os.path.join(REPORT_DIR, f'{student_id}_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
    
    violations = []
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            violations = f.readlines()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Proctoring Report - {student_id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #333; }}
            .violation {{ padding: 10px; margin: 5px 0; background: #f8d7da; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>AI Proctoring Report for {student_id}</h1>
        <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <h2>Violations Detected: {len(violations)}</h2>
        <div>
    """
    for v in violations:
        html_content += f'<div class="violation">{v.strip()}</div>'
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    with open(report_path, 'w') as f:
        f.write(html_content)
    
    return report_path