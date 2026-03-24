from prometheus_client import Counter, Gauge, Histogram

# -------- HTTP --------

HTTP_REQUESTS = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])

HTTP_LATENCY = Histogram("http_request_latency_seconds", "HTTP request latency", ["path"])

HTTP_IN_PROGRESS = Gauge("http_requests_in_progress", "HTTP requests in progress")


# -------- Repository --------

REPOSITORY_REQUESTS = Counter(
    "repository_requests_total",
    "Total repository requests",
    ["repository", "operation", "status"]
)

REPOSITORY_LATENCY = Histogram(
    "repository_request_latency_seconds",
    "Repository request latency",
    ["repository", "operation"]
)
