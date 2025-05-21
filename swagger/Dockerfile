FROM python:3.11-slim

WORKDIR /app

# Сначала копируем только requirements.txt для кэширования
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Затем копируем остальное
COPY . .

# Удаляем кэш Python (лучше чем отдельный RUN для __pycache__)
RUN find . -type d -name "__pycache__" -exec rm -rf {} + \
    && find . -type f -name "*.py[co]" -delete