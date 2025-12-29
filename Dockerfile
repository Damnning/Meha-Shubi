# Используем легкий образ Python
FROM python:3.10-slim

# Отключаем буферизацию вывода (чтобы логи сразу шли в консоль)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Копируем requirements и ставим зависимости
COPY requirements.txt .
# Ставим системные зависимости для сборки (если нужны) и python либы
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]