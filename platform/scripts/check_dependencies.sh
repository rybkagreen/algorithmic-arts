#!/bin/bash
set -e
ERRORS=0

check_version() {
    local tool=$1
    local required=$2
    local actual=$($3 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+')

    if [ -z "$actual" ]; then
        echo "❌ $tool не найден"
        ERRORS=$((ERRORS+1))
    else
        echo "✅ $tool $actual (требуется >= $required)"
    fi
}

echo "🔍 Проверка зависимостей ALGORITHMIC ARTS..."
check_version "Docker"         "24.0" "docker --version"
check_version "Docker Compose" "2.24" "docker compose version"
check_version "Python"         "3.12" "python3 --version"
check_version "Node.js"        "22.0" "node --version"
check_version "Git"            "2.40" "git --version"

[ $ERRORS -eq 0 ] && echo "✅ Все зависимости в порядке!" \
                  || echo "❌ Найдено ошибок: $ERRORS. Установите недостающие компоненты."
exit $ERRORS