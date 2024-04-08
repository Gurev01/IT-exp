# Используйте официальный образ Python
FROM python:3.8-slim


RUN apt-get update && apt-get install -y ffmpeg

# Установите рабочую директорию в контейнере
WORKDIR /app

# Копируйте файлы проекта в рабочую директорию
COPY . /app

# Установите зависимости
RUN pip install --no-cache-dir streamlit

# Копируйте файл зависимостей
COPY requirements.txt /app

# Установите зависимости из файла requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем приложение Streamlit
CMD ["streamlit", "run", "app.py"]
