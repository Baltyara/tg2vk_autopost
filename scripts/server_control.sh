#!/bin/bash
# Скрипт управления tg2vk_autopost на сервере

SERVER_HOST="5.129.229.223"
SERVER_USER="root"
SERVICE_NAME="tg2vk-autopost"
APP_DIR="/opt/tg2vk_autopost"

case "$1" in
    "start")
        echo "🚀 Запуск сервиса..."
        ssh $SERVER_USER@$SERVER_HOST "systemctl start $SERVICE_NAME.service"
        ;;
    "stop")
        echo "⏹️ Остановка сервиса..."
        ssh $SERVER_USER@$SERVER_HOST "systemctl stop $SERVICE_NAME.service"
        ;;
    "restart")
        echo "🔄 Перезапуск сервиса..."
        ssh $SERVER_USER@$SERVER_HOST "systemctl restart $SERVICE_NAME.service"
        ;;
    "status")
        echo "📊 Статус сервиса..."
        ssh $SERVER_USER@$SERVER_HOST "systemctl status $SERVICE_NAME.service"
        ;;
    "logs")
        echo "📋 Логи сервиса..."
        ssh $SERVER_USER@$SERVER_HOST "journalctl -u $SERVICE_NAME.service -f"
        ;;
    "enable")
        echo "🔧 Включение автозапуска..."
        ssh $SERVER_USER@$SERVER_HOST "systemctl enable $SERVICE_NAME.service"
        ;;
    "disable")
        echo "🔧 Отключение автозапуска..."
        ssh $SERVER_USER@$SERVER_HOST "systemctl disable $SERVICE_NAME.service"
        ;;
    "batch")
        echo "📦 Запуск пакетной обработки..."
        ssh $SERVER_USER@$SERVER_HOST "cd $APP_DIR && source .venv/bin/activate && python -m tg2vk batch"
        ;;
    "sync")
        echo "🔄 Запуск синхронизации..."
        ssh $SERVER_USER@$SERVER_HOST "cd $APP_DIR && source .venv/bin/activate && python -m tg2vk sync"
        ;;
    "backfill")
        echo "📥 Запуск бэкфилла..."
        ssh $SERVER_USER@$SERVER_HOST "cd $APP_DIR && source .venv/bin/activate && python -m tg2vk backfill"
        ;;
    "status-app")
        echo "📊 Статус приложения..."
        ssh $SERVER_USER@$SERVER_HOST "cd $APP_DIR && source .venv/bin/activate && python -m tg2vk status"
        ;;
    "shell")
        echo "🐚 Подключение к серверу..."
        ssh $SERVER_USER@$SERVER_HOST
        ;;
    *)
        echo "Использование: $0 {start|stop|restart|status|logs|enable|disable|batch|sync|backfill|status-app|shell}"
        echo ""
        echo "Команды:"
        echo "  start      - Запустить сервис"
        echo "  stop       - Остановить сервис"
        echo "  restart    - Перезапустить сервис"
        echo "  status     - Показать статус сервиса"
        echo "  logs       - Показать логи сервиса"
        echo "  enable     - Включить автозапуск"
        echo "  disable    - Отключить автозапуск"
        echo "  batch      - Запустить пакетную обработку"
        echo "  sync       - Запустить синхронизацию"
        echo "  backfill   - Запустить бэкфилл"
        echo "  status-app - Показать статус приложения"
        echo "  shell      - Подключиться к серверу"
        exit 1
        ;;
esac
