#!/bin/bash
# Kafka Topics Management Script for ALGORITHMIC ARTS Platform
# Usage: ./scripts/topics.sh [create|delete|list|check|help]

set -euo pipefail

# Configuration
KAFKA_BOOTSTRAP_SERVERS="${KAFKA_BOOTSTRAP_SERVERS:-kafka:9092}"
KAFKA_TIMEOUT="${KAFKA_TIMEOUT:-30}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default topics for ALGORITHMIC ARTS platform
declare -a DEFAULT_TOPICS=(
    "company.events"
    "partnership.events"
    "user.events"
    "auth.events"
    "ai.events"
    "crm.sync.events"
    "notification.events"
    "search.index.events"
    "reporting.metrics.events"
    "billing.transaction.events"
)

# Function to display usage
usage() {
    echo "Kafka Topics Management Script"
    echo ""
    echo "Usage: $0 [command] [topic_name]"
    echo ""
    echo "Commands:"
    echo "  create      Create all default topics or specific topic"
    echo "  delete      Delete all default topics or specific topic"
    echo "  list        List all topics"
    echo "  check       Check if topics exist and are healthy"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 create"
    echo "  $0 create company.events"
    echo "  $0 delete partnership.events"
    echo "  $0 list"
    echo "  $0 check"
    echo ""
    echo "Environment variables:"
    echo "  KAFKA_BOOTSTRAP_SERVERS - Kafka bootstrap servers (default: kafka:9092)"
    echo "  KAFKA_TIMEOUT - Timeout in seconds (default: 30)"
}

# Function to check if kafka-topics.sh is available
check_kafka_cli() {
    if ! command -v kafka-topics.sh &>/dev/null; then
        echo "Error: kafka-topics.sh not found. Please ensure Kafka is installed or use docker."
        echo "You can run this script inside the kafka container: docker exec -it kafka bash"
        exit 1
    fi
}

# Function to create a topic
create_topic() {
    local topic_name="$1"
    local partitions="${2:-6}"
    local replication_factor="${3:-1}"
    
    echo "Creating topic: $topic_name with $partitions partitions and replication factor $replication_factor..."
    
    if kafka-topics.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" \
        --create \
        --topic "$topic_name" \
        --partitions "$partitions" \
        --replication-factor "$replication_factor" \
        --config cleanup.policy=delete \
        --config retention.ms=604800000 \  # 7 days retention
        --config max.message.bytes=10485760; then  # 10MB max message size
        echo "✓ Topic '$topic_name' created successfully"
        return 0
    else
        echo "✗ Failed to create topic '$topic_name'"
        return 1
    fi
}

# Function to delete a topic
delete_topic() {
    local topic_name="$1"
    
    echo "Deleting topic: $topic_name..."
    
    if kafka-topics.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" \
        --delete \
        --topic "$topic_name"; then
        echo "✓ Topic '$topic_name' deleted successfully"
        return 0
    else
        echo "✗ Failed to delete topic '$topic_name'"
        return 1
    fi
}

# Function to list topics
list_topics() {
    echo "Listing all topics..."
    kafka-topics.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" --list
}

# Function to check topic health
check_topic() {
    local topic_name="$1"
    
    echo "Checking topic: $topic_name..."
    
    # Check if topic exists
    if kafka-topics.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" --list | grep -q "^$topic_name$"; then
        echo "✓ Topic '$topic_name' exists"
        
        # Get topic description
        kafka-topics.sh --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" --describe --topic "$topic_name" | head -n 2
        return 0
    else
        echo "✗ Topic '$topic_name' does not exist"
        return 1
    fi
}

# Function to check all default topics
check_all_topics() {
    echo "Checking all default topics..."
    local success_count=0
    local total_count=${#DEFAULT_TOPICS[@]}
    
    for topic in "${DEFAULT_TOPICS[@]}"; do
        if check_topic "$topic"; then
            ((success_count++))
        fi
        echo ""
    done
    
    echo "Summary: $success_count/$total_count topics found"
    
    if [ "$success_count" -eq "$total_count" ]; then
        echo "✓ All topics are healthy"
        return 0
    else
        echo "✗ Some topics are missing"
        return 1
    fi
}

# Function to create all default topics
create_all_topics() {
    echo "Creating all default topics..."
    local success_count=0
    local total_count=${#DEFAULT_TOPICS[@]}
    
    for topic in "${DEFAULT_TOPICS[@]}"; do
        if create_topic "$topic" 6 1; then
            ((success_count++))
        fi
        echo ""
    done
    
    echo "Summary: $success_count/$total_count topics created"
    
    if [ "$success_count" -eq "$total_count" ]; then
        echo "✓ All topics created successfully"
        return 0
    else
        echo "✗ Some topics failed to create"
        return 1
    fi
}

# Function to delete all default topics
delete_all_topics() {
    echo "Deleting all default topics..."
    local success_count=0
    local total_count=${#DEFAULT_TOPICS[@]}
    
    for topic in "${DEFAULT_TOPICS[@]}"; do
        if delete_topic "$topic"; then
            ((success_count++))
        fi
        echo ""
    done
    
    echo "Summary: $success_count/$total_count topics deleted"
    
    if [ "$success_count" -eq "$total_count" ]; then
        echo "✓ All topics deleted successfully"
        return 0
    else
        echo "✗ Some topics failed to delete"
        return 1
    fi
}

# Main script logic
main() {
    local command="$1"
    local topic_name="$2"
    
    case "$command" in
        create)
            if [ -z "${topic_name:-}" ]; then
                create_all_topics
            else
                create_topic "$topic_name"
            fi
            ;;
        delete)
            if [ -z "${topic_name:-}" ]; then
                delete_all_topics
            else
                delete_topic "$topic_name"
            fi
            ;;
        list)
            list_topics
            ;;
        check)
            if [ -z "${topic_name:-}" ]; then
                check_all_topics
            else
                check_topic "$topic_name"
            fi
            ;;
        help|--)
            usage
            ;;
        *)
            echo "Error: Unknown command '$command'"
            echo ""
            usage
            exit 1
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ $# -eq 0 ]; then
        usage
        exit 1
    fi
    
    main "$@"
fi