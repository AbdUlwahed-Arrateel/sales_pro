#!/bin/bash
# سكريبت تشغيل سريع لنظام سيلز برو (للتطوير المحلي فقط)
set -e
echo "══════════════════════════════════"
echo "  سيلز برو — نظام إدارة المبيعات"
echo "══════════════════════════════════"

# إنشاء البيئة الافتراضية إن لم توجد
if [ ! -d "venv" ]; then
    echo "⚙  إنشاء البيئة الافتراضية..."
    python3 -m venv venv
fi

# تفعيل البيئة
source venv/bin/activate

# تثبيت المكتبات
echo "📦 تثبيت المكتبات..."
pip install -q -r requirements.txt

# إنشاء قاعدة البيانات
echo "🗄  إنشاء قاعدة البيانات..."
python manage.py migrate

# إنشاء المدير إن لم يوجد
if python manage.py shell -c "from accounts.models import User; exit(0 if User.objects.filter(username='admin').exists() else 1)" 2>/dev/null; then
    echo "ℹ  الحساب موجود مسبقاً: admin"
else
    echo "👤 إنشاء حساب المدير الرئيسي (سيُطلب منك اختيار كلمة مرور)..."
    python manage.py createsuperuser_owner --username admin
fi

echo ""
echo "🚀 جاري تشغيل الخادم..."
echo "🌐 افتح المتصفح: http://127.0.0.1:8000"
echo "══════════════════════════════════"
python manage.py runserver
