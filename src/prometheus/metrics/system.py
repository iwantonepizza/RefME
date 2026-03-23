from prometheus_client import Counter, Gauge

# -------- SYSTEM (node_exporter style) --------

CPU_USAGE = Gauge("node_cpu_usage_percent", "CPU usage percent")
RAM_USAGE = Gauge("node_memory_usage_bytes", "Memory usage in bytes")
RAM_TOTAL = Gauge("node_memory_total_bytes", "Total memory in bytes")
DISK_USAGE = Gauge("node_disk_usage_bytes", "Disk usage in bytes")
DISK_TOTAL = Gauge("node_disk_total_bytes", "Total disk in bytes")
DISK_IO_READ = Counter("node_disk_read_bytes_total", "Total disk read bytes")
DISK_IO_WRITE = Counter("node_disk_written_bytes_total", "Total disk written bytes")
NET_BYTES_SENT = Counter("node_network_transmit_bytes_total", "Total network bytes sent")
NET_BYTES_RECV = Counter("node_network_receive_bytes_total", "Total network bytes received")
SYSTEM_UPTIME = Gauge("node_system_uptime_seconds", "System uptime in seconds")
