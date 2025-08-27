"""
Performance monitoring utilities for the RAG chatbot
"""
import time
import logging
from functools import wraps

def track_performance(operation_name: str):
    """Decorator to track operation performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time
                logging.info(f"🚀 {operation_name} completed in {duration:.2f}s")
                return result
            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time
                logging.error(f"❌ {operation_name} failed after {duration:.2f}s: {str(e)}")
                raise
        return wrapper
    return decorator

def log_response_time(start_time: float, operation: str):
    """Log response time for an operation"""
    duration = time.time() - start_time
    logging.info(f"⏱️ {operation}: {duration:.2f}s")
    return duration
