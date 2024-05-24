import time
from functools import wraps

import psutil
import requests

from ..models import BandwidthLog

total_bandwidth_used = 0


def measure_bandwidth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get initial network IO counters
        initial_io_counters = psutil.net_io_counters()
        initial_bytes_sent = initial_io_counters.bytes_sent
        initial_bytes_recv = initial_io_counters.bytes_recv

        # Call the decorated function
        result = func(*args, **kwargs)

        # Get final network IO counters
        final_io_counters = psutil.net_io_counters()
        final_bytes_sent = final_io_counters.bytes_sent
        final_bytes_recv = final_io_counters.bytes_recv

        # Calculate the bandwidth used
        bytes_sent = final_bytes_sent - initial_bytes_sent
        bytes_recv = final_bytes_recv - initial_bytes_recv
        total_bytes = bytes_sent + bytes_recv
        total_mb = total_bytes / (1024 * 1024)

        print(f"Bandwidth used: {total_mb:.2f} MB")

        # Log the bandwidth usage to the database
        try:
            BandwidthLog.objects.create(
                function_name=func.__name__,
                bytes_sent=bytes_sent,
                bytes_received=bytes_recv,
                total_bytes=total_bytes,
                total_mb=total_mb
            )
            print("Bandwidth log created successfully")
        except Exception as e:
            print(f"Error creating bandwidth log: {e}")

        # Update global total bandwidth used
        global total_bandwidth_used
        total_bandwidth_used += total_mb

        return result, total_mb

    return wrapper
