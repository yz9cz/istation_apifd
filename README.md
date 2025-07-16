# iStation API - خادم البحث عن أسماء اللاعبين

API محلي عالي الأداء للبحث عن أسماء اللاعبين في الألعاب المختلفة.

## الألعاب المدعومة

- **PUBG Mobile** - باستخدام متصفحات متوازية
- **Free Fire** - API سريع
- **Jawaker** - البحث في منصة جواكر
- **BigOLive** - البحث في منصة البث المباشر
- **Poppo Live** - البحث في منصة البث المباشر

## متطلبات النظام

- Python 3.8 أو أحدث
- نظام التشغيل: Windows, macOS, Linux

## التثبيت

### الطريقة الأولى: التثبيت التلقائي

```bash
python install.py
```

### الطريقة الثانية: التثبيت اليدوي

#### 1. تثبيت Python Dependencies

```bash
pip install -r requirements.txt
```

#### 2. تثبيت Playwright Browsers (مطلوب لـ PUBG)

```bash
playwright install chromium
```

### الطريقة الثالثة: Docker

#### تشغيل مع Docker Compose

```bash
docker-compose up -d
```

#### تشغيل مع Docker

```bash
# بناء الصورة
docker build -t istation-api .

# تشغيل الحاوية
docker run -d -p 8001:8001 --name istation-api istation-api
```

## تشغيل الخادم

### التشغيل العادي
```bash
python main.py
```

### التشغيل مع سكريبت التشغيل
```bash
python run.py run --host 0.0.0.0 --port 8001
```

### التشغيل مع إعادة التحميل التلقائي (للتطوير)
```bash
python run.py run --reload
```

الخادم سيعمل على: `http://localhost:8001`

## الاستخدام

### API Endpoint

**POST** `/get_player_name`

### Body Parameters

```json
{
    "player_id": "معرف_اللاعب",
    "game_type": "نوع_اللعبة"
}
```

### أنواع الألعاب المدعومة

- `pubg` - PUBG Mobile
- `freefire` أو `ff` - Free Fire
- `jawaker` أو `jw` - Jawaker
- `bigolive` أو `bigo` - BigOLive
- `poppolive` أو `poppo` - Poppo Live

### أمثلة الاستخدام

#### PUBG Mobile
```bash
curl -X POST "http://localhost:8001/get_player_name" \
     -H "Content-Type: application/json" \
     -d '{"player_id": "5443564406", "game_type": "pubg"}'
```

#### Free Fire
```bash
curl -X POST "http://localhost:8001/get_player_name" \
     -H "Content-Type: application/json" \
     -d '{"player_id": "11442289597", "game_type": "freefire"}'
```

#### Jawaker
```bash
curl -X POST "http://localhost:8001/get_player_name" \
     -H "Content-Type: application/json" \
     -d '{"player_id": "1230574182", "game_type": "jawaker"}'
```

### Response Format

```json
{
    "player_name": "اسم_اللاعب"
}
```

أو في حالة عدم العثور على اللاعب:

```json
{
    "player_name": null
}
```

## الوثائق التفاعلية

بعد تشغيل الخادم، يمكنك الوصول إلى الوثائق التفاعلية على:

- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

## Health Check

للتحقق من حالة الخادم:

**GET** `/health`

```bash
curl http://localhost:8001/health
```

## إحصائيات الأداء

للحصول على إحصائيات الأداء:

**GET** `/stats`

```bash
curl http://localhost:8001/stats
```

## الميزات

- ⚡ **أداء عالي**: معالجة متوازية للطلبات
- 🎮 **متصفحات متوازية**: 10 متصفحات لـ PUBG
- 🌐 **Connection Pool**: إدارة ذكية للاتصالات
- 📊 **إحصائيات**: مراقبة الأداء في الوقت الفعلي
- 🔄 **Async/Await**: معالجة غير متزامنة
- 🛡️ **Error Handling**: معالجة محسنة للأخطاء

## استكشاف الأخطاء

### خطأ Playwright
إذا واجهت خطأ في Playwright:
```bash
playwright install chromium
```

### خطأ في المنافذ
إذا كان المنفذ 8001 مستخدم، يمكنك تغييره في `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8002)  # تغيير المنفذ
```

## أوامر مفيدة

### فحص حالة النظام
```bash
python run.py status
```

### تشغيل الاختبارات
```bash
python run.py test
```

### Docker Commands

#### عرض السجلات
```bash
docker-compose logs -f istation-api
```

#### إعادة تشغيل الخدمة
```bash
docker-compose restart istation-api
```

#### إيقاف الخدمة
```bash
docker-compose down
```

#### تحديث الصورة
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## ملفات المشروع

- `main.py` - الملف الرئيسي للـ API
- `requirements.txt` - متطلبات Python
- `install.py` - سكريبت التثبيت التلقائي
- `run.py` - سكريبت التشغيل المتقدم
- `Dockerfile` - ملف Docker
- `docker-compose.yml` - إعداد Docker Compose
- `pubg_player.py` - وحدة PUBG
- `freefire_player.py` - وحدة Free Fire
- `jawaker_player.py` - وحدة Jawaker
- `bigolive_player.py` - وحدة BigOLive
- `poppolive_player.py` - وحدة Poppo Live
- `connection_pool.py` - إدارة الاتصالات

## أوامر مفيدة

### فحص حالة النظام
```bash
python run.py status
```

### تشغيل الاختبارات
```bash
python run.py test
```

### Docker Commands

#### عرض السجلات
```bash
docker-compose logs -f istation-api
```

#### إعادة تشغيل الخدمة
```bash
docker-compose restart istation-api
```

#### إيقاف الخدمة
```bash
docker-compose down
```

#### تحديث الصورة
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## ملفات المشروع

- `main.py` - الملف الرئيسي للـ API
- `requirements.txt` - متطلبات Python
- `install.py` - سكريبت التثبيت التلقائي
- `run.py` - سكريبت التشغيل المتقدم
- `Dockerfile` - ملف Docker
- `docker-compose.yml` - إعداد Docker Compose
- `pubg_player.py` - وحدة PUBG
- `freefire_player.py` - وحدة Free Fire
- `jawaker_player.py` - وحدة Jawaker
- `bigolive_player.py` - وحدة BigOLive
- `poppolive_player.py` - وحدة Poppo Live
- `connection_pool.py` - إدارة الاتصالات

## المطورون

تم تطوير هذا المشروع لتوفير API سريع وموثوق للبحث عن أسماء اللاعبين.
