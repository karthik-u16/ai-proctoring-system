import os
from datetime import datetime

LOG_DIR = 'logs'

def ensure_log_dir():
    """Create logs directory if it doesn't exist"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

def log_violation(student_id, violation, timestamp):
    """Log a violation to the student's log file"""
    ensure_log_dir()
    log_file = os.path.join(LOG_DIR, f'{student_id}_violations.log')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f'[{timestamp.strftime("%Y-%m-%d %H:%M:%S")}] {violation}\n')