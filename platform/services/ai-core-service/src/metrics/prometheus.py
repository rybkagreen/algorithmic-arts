from prometheus_client import Counter, Histogram

# LLM метрики
llm_calls = Counter("llm_calls_total",
    "Total LLM API calls", ["provider", "status"])
llm_latency = Histogram("llm_latency_seconds",
    "LLM response latency", ["provider"])
llm_cost = Counter("llm_cost_rub_total",
    "Total LLM cost in RUB", ["provider"])

# Agent метрики
agent_runs = Counter("agent_runs_total",
    "Total agent executions", ["agent_name", "status"])
agent_latency = Histogram("agent_latency_seconds",
    "Agent execution latency", ["agent_name"])

# RAG метрики
rag_queries = Counter("rag_queries_total",
    "Total RAG queries", ["status"])
rag_latency = Histogram("rag_latency_seconds",
    "RAG pipeline latency", [])

# Embedding метрики
embedding_calls = Counter("embedding_calls_total",
    "Total embedding calls", ["source", "status"])
embedding_latency = Histogram("embedding_latency_seconds",
    "Embedding generation latency", ["source"])

# Kafka метрики
kafka_messages = Counter("kafka_messages_total",
    "Total Kafka messages processed", ["topic", "status"])