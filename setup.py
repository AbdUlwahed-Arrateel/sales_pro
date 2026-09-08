#!/usr/bin/env python3
"""
سكريبت إعداد نظام المبيعات (للتطوير والتجربة المحلية فقط).
لبيئة إنتاج حقيقية، اضبط متغيرات البيئة الموضحة في README.md أولاً.
"""
import subprocess
import secrets
import os

def run(cmd):
    print(f"  ▶ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout: print(result.stdout)
    if result.stderr and 'error' in result.stderr.lower(): print("⚠", result.stderr)
    return result.returncode == 0

print("=" * 50)
print("  إعداد نظام إدارة المبيعات - سيلز برو")
print("=" * 50)

print("\n📦 تثبيت المتطلبات...")
run("pip install -r requirements.txt")

print("\n🗄️  إنشاء قاعدة البيانات...")
run("python manage.py makemigrations")
run("python manage.py migrate")

print("\n👤 إنشاء حساب المدير الرئيسي...")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()
from accounts.models import User

if not User.objects.filter(username='admin').exists():
    generated_password = secrets.token_urlsafe(9)
    User.objects.create_user(
        username='admin',
        password=generated_password,
        first_name='المدير',
        last_name='العام',
        is_staff=True,
        is_superuser=True
    )
    print("  ✅ تم إنشاء المستخدم: admin")
    print(f"  🔑 كلمة المرور (احفظها الآن، لن تظهر مرة أخرى): {generated_password}")
else:
    print("  ℹ️  المستخدم admin موجود مسبقاً")

print("\n✅ تم الإعداد بنجاح!")
print("\n🚀 لتشغيل النظام:")
print("   python manage.py runserver")
print("\n🌐 افتح المتصفح على:")
print("   http://127.0.0.1:8000")
print("=" * 50)
