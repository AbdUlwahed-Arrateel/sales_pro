import getpass

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from accounts.models import User


class Command(BaseCommand):
    """
    ينشئ حساب "مالك" (owner) — الحساب الرئيسي الذي يدير باقي حسابات الموظفين.
    يمكن استخدامه تفاعلياً أو مباشرة عبر خيارات سطر الأوامر:

        python manage.py createsuperuser_owner
        python manage.py createsuperuser_owner --username admin --noinput --password admin123
    """
    help = 'إنشاء حساب مالك رئيسي (owner) للنظام'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default=None, help='اسم المستخدم')
        parser.add_argument('--first-name', type=str, default='', help='الاسم الأول')
        parser.add_argument('--last-name', type=str, default='', help='الاسم الأخير')
        parser.add_argument('--email', type=str, default='', help='البريد الإلكتروني')
        parser.add_argument('--password', type=str, default=None, help='كلمة المرور (مع --noinput فقط)')
        parser.add_argument('--noinput', '--no-input', action='store_true', dest='noinput',
                             help='عدم طلب أي مُدخلات تفاعلية (يتطلب --username و --password)')

    def handle(self, *args, **options):
        noinput = options['noinput']

        if noinput:
            username = options['username']
            password = options['password']
            if not username or not password:
                raise CommandError('في وضع --noinput يجب تمرير --username و --password')
        else:
            username = options['username'] or input('اسم المستخدم: ').strip()
            while not username:
                username = input('اسم المستخدم (مطلوب): ').strip()

            while True:
                password = getpass.getpass('كلمة المرور: ')
                password2 = getpass.getpass('تأكيد كلمة المرور: ')
                if password != password2:
                    self.stderr.write(self.style.ERROR('كلمتا المرور غير متطابقتين، حاول مرة أخرى.'))
                    continue
                if len(password) < 6:
                    self.stderr.write(self.style.ERROR('كلمة المرور يجب ألا تقل عن 6 أحرف.'))
                    continue
                break

        if User.objects.filter(username=username).exists():
            raise CommandError(f'اسم المستخدم "{username}" مستخدم مسبقاً.')

        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=options['first_name'],
                last_name=options['last_name'],
                email=options['email'],
                is_staff=True,
                is_superuser=True,
            )
        except IntegrityError as e:
            raise CommandError(f'تعذّر إنشاء المستخدم: {e}')

        self.stdout.write(self.style.SUCCESS(
            f'تم إنشاء حساب المالك "{user.username}" بنجاح.'
        ))
