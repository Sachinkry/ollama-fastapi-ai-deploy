from prometheus_client import Counter, Histogram, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST

registry = CollectorRegistry()
REQUESTS = Counter("requests_total", "Total requests", ["route","model"], registry=registry)
ERRORS   = Counter("errors_total", "Errors", ["route","model"], registry=registry)
LATENCY  = Histogram("latency_seconds", "Request latency", ["route","model"], registry=registry)

def render_metrics():
    return generate_latest(registry), CONTENT_TYPE_LATEST
