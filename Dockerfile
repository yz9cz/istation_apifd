# iStation API Docker Image
FROM python:3.11-slim

# معلومات المشروع
LABEL maintainer="iStation Team"
LABEL description="iStation API - خادم البحث عن أسماء اللاعبين"
LABEL version="2.0.0"

# إعداد متغيرات البيئة
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# إنشاء مستخدم غير root
RUN groupadd -r istation && useradd -r -g istation istation

# تثبيت dependencies النظام
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# إعداد مجلد العمل
WORKDIR /app

# نسخ ملفات المتطلبات
COPY requirements.txt .

# تثبيت Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# تثبيت Playwright browsers
RUN playwright install chromium && \
    playwright install-deps chromium

# نسخ ملفات المشروع
COPY . .

# تغيير ملكية الملفات
RUN chown -R istation:istation /app

# التبديل للمستخدم غير root
USER istation

# إنشاء المجلدات المطلوبة
RUN mkdir -p logs temp

# فتح المنفذ
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health')" || exit 1

# أمر التشغيل
CMD ["python", "main.py"]
