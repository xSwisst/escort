#!/bin/bash

# Generate secrets for new_escort project

set -e

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    Генерация секретов для new_escort                         ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Проверка наличия openssl
if ! command -v openssl &> /dev/null; then
    echo "❌ Ошибка: openssl не установлен"
    exit 1
fi

# Генерация секретов
API_SECRET=$(openssl rand -hex 32)
ADMIN_API_KEY=$(openssl rand -hex 32)
WEB_APP_SECRET=$(openssl rand -hex 32)
MAIN_WEBHOOK_SECRET=$(openssl rand -hex 16)
SUPPORT_WEBHOOK_SECRET=$(openssl rand -hex 16)
ADMIN_WEBHOOK_SECRET=$(openssl rand -hex 16)

echo "✅ Секреты сгенерированы"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 ИСПОЛЬЗУЙ ЭТИ ЗНАЧЕНИЯ В .env ФАЙЛАХ:"
echo ""
echo "─────────────────────────────────────────────────────────────────────────────"
echo "API_SECRET_KEY (используй во ВСЕХ сервисах):"
echo "─────────────────────────────────────────────────────────────────────────────"
echo "$API_SECRET"
echo ""
echo "Скопируй в:"
echo "  • api/.env"
echo "  • main/.env"
echo "  • support/.env"
echo "  • admin/.env"
echo "  • photos/.env"
echo "  • logs/.env"
echo "  • web_app/.env"
echo ""
echo "─────────────────────────────────────────────────────────────────────────────"
echo "ADMIN_API_KEY (только для api/.env):"
echo "─────────────────────────────────────────────────────────────────────────────"
echo "$ADMIN_API_KEY"
echo ""
echo "─────────────────────────────────────────────────────────────────────────────"
echo "WEB_APP_SESSION_SECRET (только для web_app/.env):"
echo "─────────────────────────────────────────────────────────────────────────────"
echo "$WEB_APP_SECRET"
echo ""
echo "─────────────────────────────────────────────────────────────────────────────"
echo "Webhook секреты (по одному для каждого бота):"
echo "─────────────────────────────────────────────────────────────────────────────"
echo "MAIN_WEBHOOK_SECRET_TOKEN:    $MAIN_WEBHOOK_SECRET"
echo "SUPPORT_WEBHOOK_SECRET_TOKEN: $SUPPORT_WEBHOOK_SECRET"
echo "ADMIN_WEBHOOK_SECRET_TOKEN:   $ADMIN_WEBHOOK_SECRET"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Сохрани эти значения в безопасном месте (password manager)"
echo ""
