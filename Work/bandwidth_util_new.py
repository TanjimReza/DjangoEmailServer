import requests
import psutil
import time
from functools import wraps

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

        # Return the result and the total bandwidth used
        global total_bandwidth_used
        total_bandwidth_used += total_mb
        return result, total_mb

    return wrapper


@measure_bandwidth
def make_request(url):
    response = requests.get(url)
    return response.text


# Example usage
if __name__ == "__main__":
    make_request("http://www.google.com")
    make_request("http://dev.venturebit.net")
    make_request("http://venturebit.net")
    make_request("http://blog.venturebit.net")

    print(f"Total bandwidth used: {total_bandwidth_used:.2f} MB")
