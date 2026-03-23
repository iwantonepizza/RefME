from prometheus_client import Counter, Histogram

# -------- LLM --------

LLM_REQUESTS = Counter("llm_requests_total", "Total LLM requests", ["model", "type"])  # chat | completion | stream

LLM_ERRORS = Counter("llm_errors_total", "Total LLM errors", ["model", "type"])

LLM_LATENCY = Histogram("llm_latency_seconds", "LLM request latency", ["model", "type"])

LLM_FIRST_TOKEN_LATENCY = Histogram("llm_first_token_latency_seconds", "Time to first token", ["model"])

LLM_TOKENS_IN = Counter("llm_tokens_input_total", "Input tokens", ["model"])

LLM_TOKENS_OUT = Counter("llm_tokens_output_total", "Output tokens", ["model"])
