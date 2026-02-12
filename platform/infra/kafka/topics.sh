#!/bin/bash
# Создание всех Kafka топиков при первом запуске
KAFKA="kafka:9092"
PARTITIONS=3
REPLICATION=1

create_topic() {
    kafka-topics.sh --create \
        --bootstrap-server $KAFKA \
        --topic $1 \
        --partitions $PARTITIONS \
        --replication-factor $REPLICATION \
        --if-not-exists
}

echo "🔧 Создание Kafka топиков..."

# Company domain
create_topic "company.created"
create_topic "company.updated"
create_topic "company.enriched"
create_topic "company.deleted"

# Partnership domain
create_topic "partnership.matched"
create_topic "partnership.status_changed"
create_topic "partnership.deal_closed"

# User domain
create_topic "user.created"
create_topic "user.updated"
create_topic "user.login_failed"

# Billing domain
create_topic "billing.subscription_created"
create_topic "billing.subscription_changed"
create_topic "billing.payment_succeeded"
create_topic "billing.payment_failed"

# AI domain
create_topic "ai.analysis.queue"
create_topic "ai.analysis.results"

# CRM / Notifications
create_topic "crm.sync.requested"
create_topic "notification.events"

echo "✅ Топики созданы"