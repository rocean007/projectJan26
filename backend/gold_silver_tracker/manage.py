#!/usr/bin/env python
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gold_tracker.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
    # Frontend: http://localhost:8000
    # API Test: http://localhost:8000/api/prices/
    # Health Check: http://localhost:8000/api/health/