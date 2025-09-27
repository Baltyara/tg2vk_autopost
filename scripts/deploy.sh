#!/bin/bash
set -e

# Скрипт развертывания tg2vk_autopost на сервере

SERVER_HOST="your-server.com"
SERVER_USER="root"
APP_NAME="tg2vk_autopost"
APP_DIR="/opt/$APP_NAME"
SERVICE_NAME="tg2vk-autopost"

echo "🚀 Развертывание $APP_NAME на сервер $SERVER_HOST"

# Проверяем, что мы в правильной директории
if [ ! -f "requirements.txt" ]; then
    echo "❌ Ошибка: requirements.txt не найден. Запустите из корня проекта"
    exit 1
fi

# Создаем архив проекта
echo "📦 Создание архива проекта..."
tar -czf /tmp/$APP_NAME.tar.gz \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.venv' \
    --exclude='data' \
    --exclude='logs' \
    --exclude='*.log' \
    .

# Копируем на сервер
echo "📤 Копирование на сервер..."
sshpass -p 'kHXUL.x66DJRHx' scp -o StrictHostKeyChecking=no /tmp/$APP_NAME.tar.gz $SERVER_USER@$SERVER_HOST:/tmp/

# Выполняем развертывание на сервере
echo "🔧 Установка на сервере..."
sshpass -p 'kHXUL.x66DJRHx' ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST << EOF
set -e

# Останавливаем сервис если запущен
systemctl stop $SERVICE_NAME.service 2>/dev/null || true

# Создаем директорию приложения
mkdir -p $APP_DIR

# Распаковываем архив
cd $APP_DIR
tar -xzf /tmp/$APP_NAME.tar.gz
rm /tmp/$APP_NAME.tar.gz

# Создаем виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

# Устанавливаем зависимости
pip install --upgrade pip
pip install -r requirements.txt

# Создаем необходимые директории
mkdir -p data/inbox data/state logs

# Устанавливаем права
chown -R root:root $APP_DIR
chmod +x scripts/*.sh

# Создаем systemd сервис
cat > /etc/systemd/system/$SERVICE_NAME.service << 'SERVICE_EOF'
[Unit]
Description=TG2VK AutoPost Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/.venv/bin
ExecStart=$APP_DIR/.venv/bin/python -m tg2vk daemon
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Перезагружаем systemd
systemctl daemon-reload

echo "✅ Установка завершена"
echo "📝 Создайте файл $APP_DIR/.env с настройками"
echo "🚀 Запустите: systemctl start $SERVICE_NAME.service"
echo "📊 Статус: systemctl status $SERVICE_NAME.service"
echo "📋 Логи: journalctl -u $SERVICE_NAME.service -f"

EOF

# Очищаем временный файл
rm /tmp/$APP_NAME.tar.gz

echo "✅ Развертывание завершено!"
echo ""
echo "Следующие шаги:"
echo "1. Подключитесь к серверу: ssh $SERVER_USER@$SERVER_HOST"
echo "2. Создайте файл $APP_DIR/.env с настройками"
echo "3. Запустите сервис: systemctl start $SERVICE_NAME.service"
echo "4. Включите автозапуск: systemctl enable $SERVICE_NAME.service"
