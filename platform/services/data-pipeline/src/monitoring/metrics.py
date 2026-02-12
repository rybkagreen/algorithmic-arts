from prometheus_client import Counter, Histogram, Gauge

# Scraper метрики
scraper_requests = Counter("scraper_requests_total",
    "Total scraper requests", ["scraper", "status"])
scraper_latency = Histogram("scraper_latency_seconds",
    "Scraper request latency", ["scraper"])

# Transform метрики
transform_calls = Counter("transform_calls_total",
    "Total transform calls", ["transform_type", "status"])
transform_latency = Histogram("transform_latency_seconds",
    "Transform latency", ["transform_type"])

# Load метрики
load_operations = Counter("load_operations_total",
    "Total load operations", ["operation", "status"])
load_latency = Histogram("load_latency_seconds",
    "Load operation latency", ["operation"])

# Kafka метрики
kafka_messages = Counter("kafka_messages_total",
    "Total Kafka messages processed", ["topic", "status"])

# Celery метрики
celery_tasks = Counter("celery_tasks_total",
    "Total Celery tasks executed", ["task", "status"])
celery_latency = Histogram("celery_latency_seconds",
    "Celery task latency", ["task"])