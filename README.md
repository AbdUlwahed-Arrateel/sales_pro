<div align="center">

<img src="https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django&logoColor=white"/>
<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>

</div>

---

<div dir="rtl">

# 🛒 سيلز برو — نظام إدارة المبيعات والمخزون

نظام متكامل لإدارة المبيعات، المخزون، الزبائن، الموردين، والمصروفات، مبني بـ **Django 4.2** مع واجهة عربية احترافية وكاملة الاتجاه (RTL).

##  المميزات الرئيسية

| الوحدة | الوصف |
|--------|--------|
| 🏪 **نقطة البيع (POS)** | واجهة بيع سريعة مع دعم لوحة المفاتيح (Enter، Arrows، F-Keys) |
| 📦 **إدارة المخزون** | تتبع الأصناف والكميات مع تنبيهات النقص التلقائية |
|  **إدارة الزبائن** | ملفات كاملة، كشوفات حساب، وتتبع المديونيات |
| 🚚 **إدارة الموردين** | تسجيل الموردين وربطهم بعمليات الشراء |
| 🧾 **الفواتير والمدفوعات** | إنشاء الفواتير وتسجيل الدفعات وتتبع الأرصدة |
| 💰 **المصروفات** | تسجيل وتصنيف المصروفات التشغيلية |
| 📊 **التقارير** | تقارير الأرباح والخسائر وملخصات المبيعات |
|  **نظام الأدوار والصلاحيات** | أدوار وظيفية مخصصة قابلة للتعديل لكل موظف |

## 🖥️ متطلبات التشغيل

- Python **3.10** أو أحدث
- pip

## 🚀 خطوات التشغيل المحلي

```bash
# 1. استنساخ المشروع
git clone https://gitlab.com/YOUR_USERNAME/salespro.git
cd salespro/sales_system

# 2. إنشاء بيئة افتراضية وتفعيلها
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows

# 3. تثبيت المتطلبات
pip install -r requirements.txt

# 4. إنشاء قاعدة البيانات
python manage.py migrate

# 5. إنشاء حساب المالك الرئيسي
python manage.py createsuperuser_owner

# 6. تشغيل الخادم
python manage.py runserver
```

ثم افتح المتصفح على: **http://127.0.0.1:8000**

> 💡 **بدلاً من الخطوات 1–6** يمكنك تشغيل `python start.sh` مباشرة على Linux/macOS وستُنفَّذ كل الخطوات تلقائياً.

## ⚙️ متغيرات البيئة (للنشر الفعلي على السيرفر)

المشروع يعمل محلياً بإعدادات افتراضية آمنة للتطوير. **قبل النشر على سيرفر حقيقي** عرّف المتغيرات التالية:

| المتغير | الوصف | القيمة الافتراضية |
|---------|--------|-------------------|
| `DJANGO_SECRET_KEY` | مفتاح تشفير سري — لا يُشارك أبداً | قيمة تطوير غير آمنة |
| `DJANGO_DEBUG` | وضع التصحيح | `False` |
| `DJANGO_ALLOWED_HOSTS` | النطاقات المسموح بها (مفصولة بفاصلة) | `localhost,127.0.0.1` |
| `DJANGO_SECURE_COOKIES` | تفعيل الكوكيز الآمنة عبر HTTPS | `True` |

```bash
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export DJANGO_DEBUG=False
export DJANGO_ALLOWED_HOSTS=yourdomain.com
export DJANGO_SECURE_COOKIES=True
```

## 🗂️ هيكل المشروع

```
sales_system/
├── accounts/        # نظام المستخدمين والأدوار والصلاحيات
├── customers/       # إدارة الزبائن وكشوفات الحساب
├── inventory/       # الأصناف، المخزون، المشتريات، الموردون
├── sales/           # الفواتير والمدفوعات
├── expenses/        # المصروفات وفئاتها
├── pos/             # واجهة نقطة البيع
├── reports/         # التقارير المالية
├── core/            # الإعدادات والروابط الرئيسية
├── templates/       # قوالب HTML
├── static/          # CSS و JavaScript
└── manage.py
```

## 🛠️ التقنيات المستخدمة

- **Backend:** Django 4.2, Python 3.10+
- **Database:** SQLite (التطوير) / PostgreSQL (الإنتاج)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Icons:** Font Awesome 6

</div>

---

# 🛒 SalesPro — Sales & Inventory Management System

A full-featured sales and inventory management system built with **Django 4.2**, featuring a professional Arabic RTL interface.

##  Key Features

- **Point of Sale (POS)** — Fast sales interface with full keyboard support
- **Inventory Management** — Track products with low-stock alerts
- **Customer Management** — Full profiles, statements, and debt tracking
- **Supplier Management** — Link suppliers to purchase transactions
- **Invoices & Payments** — Create invoices and track balances
- **Expenses** — Log and categorize operational expenses
- **Reports** — Profit/loss reports and sales summaries
- **Role-Based Access Control** — Customizable roles and permissions per employee

## 🚀 Quick Start

```bash
git clone https://gitlab.com/YOUR_USERNAME/salespro.git
cd salespro/sales_system
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser_owner
python manage.py runserver
```
or you just can write 'python start.sh' on linux/MacOS

Visit **http://127.0.0.1:8000**

## ⚙️ Environment Variables (Production)

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Strong random secret key |
| `DJANGO_DEBUG` | Set to `False` in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hostnames |
| `DJANGO_SECURE_COOKIES` | Set to `True` when using HTTPS |

## 🛠️ Tech Stack

`Django 4.2` · `Python 3.10+` · `SQLite` · `Vanilla JS` · `Font Awesome`



