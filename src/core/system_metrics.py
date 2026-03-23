import asyncio
import time

import psutil

from src.prometheus.metrics.system import (
    CPU_USAGE,
    DISK_IO_READ,
    DISK_IO_WRITE,
    DISK_TOTAL,
    DISK_USAGE,
    NET_BYTES_RECV,
    NET_BYTES_SENT,
    RAM_TOTAL,
    RAM_USAGE,
    SYSTEM_UPTIME,
)


async def collect_system_metrics(interval: int = 3):
    """Сбор системных метрик в стиле node_exporter."""
    start_time = time.time()
    last_disk_io = psutil.disk_io_counters()
    last_net_io = psutil.net_io_counters()

    while True:
        try:
            # CPU
            CPU_USAGE.set(psutil.cpu_percent())

            # Memory
            mem = psutil.virtual_memory()
            RAM_USAGE.set(mem.used)
            RAM_TOTAL.set(mem.total)

            # Disk
            disk = psutil.disk_usage("/")
            DISK_USAGE.set(disk.used)
            DISK_TOTAL.set(disk.total)

            # Disk I/O
            current_disk_io = psutil.disk_io_counters()
            if current_disk_io and last_disk_io:
                DISK_IO_READ.inc(current_disk_io.read_bytes - last_disk_io.read_bytes)
                DISK_IO_WRITE.inc(current_disk_io.write_bytes - last_disk_io.write_bytes)
            last_disk_io = current_disk_io

            # Network
            current_net_io = psutil.net_io_counters()
            if current_net_io and last_net_io:
                NET_BYTES_SENT.inc(current_net_io.bytes_sent - last_net_io.bytes_sent)
                NET_BYTES_RECV.inc(current_net_io.bytes_recv - last_net_io.bytes_recv)
            last_net_io = current_net_io

            # Uptime
            SYSTEM_UPTIME.set(time.time() - start_time)

        except Exception as e:
            asyncio.get_event_loop().call_exception_handler(
                {"message": f"System metrics collection failed: {e}", "exception": e}
            )

        await asyncio.sleep(interval)
