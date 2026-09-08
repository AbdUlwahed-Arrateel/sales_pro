# نظام إدارة المبيعات والمخزون - Sales Pro

## متطلبات التشغيل
- Python 3.10+
- pip

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

