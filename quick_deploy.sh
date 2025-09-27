#!/bin/bash
# Быстрое развертывание tg2vk_autopost

echo "🚀 Быстрое развертывание TG2VK AutoPost"
echo "========================================"

# Проверяем, что мы в правильной директории
if [ ! -f "requirements.txt" ]; then
    echo "❌ Ошибка: requirements.txt не найден. Запустите из корня проекта"
    exit 1
fi

# Развертываем на сервер
echo "📦 Развертывание на сервер..."
./scripts/deploy.sh

echo ""
echo "✅ Развертывание завершено!"
echo ""
echo "Следующие шаги:"
echo "1. Подключитесь к серверу: ssh user@your-server.com"
echo "2. Перейдите в директорию: cd /opt/tg2vk_autopost"
echo "3. Скопируйте конфигурацию: cp configs/config.sample.env .env"
echo "4. Отредактируйте .env файл: nano .env"
echo "5. Запустите сервис: systemctl start tg2vk-autopost.service"
echo "6. Включите автозапуск: systemctl enable tg2vk-autopost.service"
echo ""
echo "Управление с локального компьютера:"
echo "./scripts/server_control.sh start|stop|status|logs"
echo ""
echo "Документация: DEPLOYMENT.md"
