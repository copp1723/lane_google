#!/usr/bin/env python3
"""Fix remaining database references"""

import os
import re

files_to_fix = [
    'src/models/analytics_snapshot.py',
    'src/models/approval_request.py', 
    'src/models/budget_alert.py',
    'src/models/conversation.py',
    'src/services/conversation.py',
    'src/utils/audit_log.py'
]

for file_path in files_to_fix:
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix remaining db. references
        content = re.sub(r'from src\.config\.database import db', 
                        'from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON, Enum, Index\nfrom sqlalchemy.orm import relationship\nfrom src.config.database import Base', 
                        content)
        
        # Fix remaining db. references
        content = re.sub(r'db\.', '', content)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Fixed {file_path}")

print("All database references fixed!")