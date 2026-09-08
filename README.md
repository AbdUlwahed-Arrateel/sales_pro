# نظام إدارة المبيعات والمخزون - Sales Pro

## متطلبات التشغيل
- Python 3.10+
- pip

## متغيرات البيئة (مهم قبل النشر الفعلي)
المشروع يعمل محلياً بإعدادات افتراضية آمنة للتطوير فقط. **قبل النشر على سيرفر حقيقي** عرّف المتغيرات التالية:

| المتغير | الوصف | مثال |
|---|---|---|
| `DJANGO_SECRET_KEY` | مفتاح سري عشوائي وطويل، لا يُشارك أبداً | `openssl rand -hex 32` |
| `DJANGO_DEBUG` | يجب أن تكون `False` في الإنتاج | `False` |
| `DJANGO_ALLOWED_HOSTS` | أسماء النطاقات المسموحة، مفصولة بفاصلة | `example.com,www.example.com` |
| `DJANGO_SECURE_COOKIES` | `True` عند التشغيل عبر HTTPS | `True` |

```bash
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export DJANGO_DEBUG=False
export DJANGO_ALLOWED_HOSTS=example.com
```

## خطوات التشغيل

```bash
# 1. تثبيت المتطلبات
pip install -r requirements.txt

# 2. إنشاء قاعدة البيانات
python manage.py migrate

# 3. إنشاء حساب المالك الرئيسي (تفاعلي)
python manage.py createsuperuser_owner

# أو مباشرة بدون تفاعل:
python manage.py createsuperuser_owner --username admin --noinput --password "كلمة-مرور-قوية"

# 4. تشغيل الخادم
python manage.py runserver

# افتح المتصفح على: http://127.0.0.1:8000
```

