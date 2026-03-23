from prometheus_client import Counter, Gauge, Histogram

# -------- HTTP --------

HTTP_REQUESTS = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])

HTTP_LATENCY = Histogram("http_request_latency_seconds", "HTTP request latency", ["path"])

HTTP_IN_PROGRESS = Gauge("http_requests_in_progress", "HTTP requests in progress")
