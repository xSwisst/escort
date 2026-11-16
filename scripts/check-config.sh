#!/bin/bash

# Validate configuration for all services

set -e

SERVICES=("api" "main" "support" "admin" "photos" "logs" "web_app")
ERRORS=0

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    Проверка конфигурации сервисов                            ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

check_service() {
    local service=$1
    local env_file="$service/.env"

    echo -n "Проверка $service... "

    if [ ! -f "$env_file" ]; then
        echo "❌ .env не найден"
        ERRORS=$((ERRORS + 1))
        return 1
    fi

    # Check for API_SECRET_KEY (required for all except postgres)
    if ! grep -q "^API_SECRET_KEY=" "$env_file" 2>/dev/null; then
        echo "❌ отсутствует API_SECRET_KEY"
        ERRORS=$((ERRORS + 1))
        return 1
    fi

    # Check if API_SECRET_KEY is not default
    if grep -q "^API_SECRET_KEY=change-me" "$env_file" 2>/dev/null; then
        echo "⚠️  API_SECRET_KEY не изменен (default значение)"
        ERRORS=$((ERRORS + 1))
        return 1
    fi

    echo "✅"
    return 0
}

check_api_secret_consistency() {
    echo ""
    echo "Проверка консистентности API_SECRET_KEY..."

    local first_secret=""
    local inconsistent=0

    for service in "${SERVICES[@]}"; do
        local env_file="$service/.env"
        if [ -f "$env_file" ]; then
            local secret=$(grep "^API_SECRET_KEY=" "$env_file" 2>/dev/null | cut -d'=' -f2)

            if [ -z "$first_secret" ]; then
                first_secret="$secret"
            elif [ "$secret" != "$first_secret" ]; then
                echo "❌ $service имеет другой API_SECRET_KEY!"
                inconsistent=1
            fi
        fi
    done

    if [ $inconsistent -eq 0 ]; then
        echo "✅ API_SECRET_KEY одинаковый во всех сервисах"
    else
        echo "❌ API_SECRET_KEY должен быть одинаковым во всех сервисах!"
        ERRORS=$((ERRORS + 1))
    fi
}

# Check each service
for service in "${SERVICES[@]}"; do
    check_service "$service"
done

# Check API_SECRET_KEY consistency
check_api_secret_consistency

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $ERRORS -eq 0 ]; then
    echo "✅ Все проверки пройдены успешно!"
    echo ""
    echo "🚀 Можно запускать: docker compose up -d"
    exit 0
else
    echo "❌ Найдено ошибок: $ERRORS"
    echo ""
    echo "📝 Исправь ошибки и запусти проверку снова"
    echo ""
    echo "💡 Подсказки:"
    echo "  • Скопируй .env.example в .env для каждого сервиса:"
    echo "    cd api && cp .env.example .env"
    echo ""
    echo "  • Сгенерируй секреты:"
    echo "    ./scripts/generate-secrets.sh"
    echo ""
    echo "  • Документация: CONFIG.md"
    exit 1
fi
