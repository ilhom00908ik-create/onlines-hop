# Online Shop Django - O'rnatish va Ishga Tushirish Ko'rsatmasi

## 📋 Talablar

- Python 3.9+
- pip (Python package manager)
- Git
- PostgreSQL (production uchun tavsiya)

## 🚀 Local Development O'rnatish

### 1. Repository'ni Klonlash

```bash
git clone https://github.com/yourusername/online_shop.git
cd online_shop
```

### 2. Virtual Environment Yaratish

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Kerakli Paketlarni O'rnatish

```bash
pip install -r requirements.txt
```

### 4. Environment Variables O'rnatish

```bash
# .env faylini yaratish (Windows)
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

`.env` faylida quyidagi o'zgaruvchilarni to'g'rilang:

```
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
GEMINI_API_KEY=your-gemini-api-key
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id
```

### 5. Database Migratsiyalarini Bajarish

```bash
# Migratsiyalarni yaratish
python manage.py makemigrations

# Migratsiyalarni qo'llash
python manage.py migrate
```

### 6. Admin Foydalanuvchisi Yaratish

```bash
python manage.py createsuperuser
```

Ko'rsatmalarni bajaring va parol qo'ying.

### 7. Sample Ma'lumotlarni Joylashtirish (Ixtiyoriy)

```bash
python manage.py seed_data
```

Bu buyruq:
- 5 ta test kategoriyasi
- 10 ta test brendi
- Admin foydalanuvchisi (admin/admin123)
- Test sotuvchi (seller1/seller123)
- 5 ta misol mahsuloti

### 8. Static Fayllarni To'plash

```bash
python manage.py collectstatic --noinput
```

### 9. Serverini Ishga Tushirish

```bash
python manage.py runserver
```

Brauzer orqali `http://localhost:8000/` ga o'ting.

### 10. Admin Panelga Kirish

`http://localhost:8000/admin/` ga o'tib yaratgan admin hisobingiz bilan kiring.

## 🧪 Testlarni Ishga Tushirish

### Barcha Testlarni Bajarish

```bash
python manage.py test
```

### Pytest bilan Testlarni Bajarish (Tavsiya)

```bash
pytest
```

### Kod Qoplamasi (Coverage) Bilan

```bash
pytest --cov=store --cov-report=html
```

## 📊 Database Migratsiya

### Yangi Migration Yaratish (Model o'zgargan bo'lsa)

```bash
python manage.py makemigrations
```

### Barcha Migratsiyalarni Ko'rish

```bash
python manage.py showmigrations
```

### Migratsiyani Ortga Qaytarish

```bash
python manage.py migrate store 0001
```

## 🔧 Production Konfiguratsiyasi

### 1. Secret Key Almashtirlish

Production'da yangi secret key yaratish:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Bu kalitni `.env` faylida o'rnatish:

```
SECRET_KEY=your-generated-secret-key
```

### 2. DEBUG Nolga O'rnatish

```
DEBUG=False
```

### 3. ALLOWED_HOSTS O'rnatish

```
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 4. Database PostgreSQL'ga O'tkazish

`.env` faylida:

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=online_shop_db
DB_USER=postgres_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. CORS va Security

Production'da CORS sozlamalarini tekshiring:

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
]

# HTTPS enforce
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 6. Gunicorn bilan Ishga Tushirish

```bash
pip install gunicorn
gunicorn core.wsgi:application --timeout 120
```

### 7. Nginx Konfiguratsiyasi (Namuna)

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /path/to/online_shop/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/online_shop/media/;
    }
}
```

## 📱 API Endpoints

### Autentifikatsiya

```
POST   /api/auth/register/      - Ro'yxatdan o'tish
POST   /api/auth/login/         - Tizimga kirish
POST   /api/auth/token/         - Token olish
POST   /api/auth/token/refresh/ - Token yangilash
```

### Mahsulotlar

```
GET    /api/products/           - Mahsulotlar ro'yxati
POST   /api/products/           - Yangi mahsulot (Sotuvchi)
GET    /api/products/<id>/      - Mahsulot tafsilotlari
PUT    /api/products/<id>/      - Mahsulotni yangilash (Sotuvchi)
DELETE /api/products/<id>/      - Mahsulotni o'chirish (Sotuvchi)
```

### Kategoriyalar & Brendlar

```
GET    /api/categories/         - Kategoriyalar
GET    /api/brands/             - Brendlar
```

### Buyurtmalar

```
GET    /api/orders/             - Mening buyurtmalarim
POST   /api/orders/             - Yangi buyurtma
GET    /api/orders/<id>/        - Buyurtma tafsilotlari
PUT    /api/orders/<id>/        - Buyurtmani yangilash
DELETE /api/orders/<id>/        - Buyurtmani o'chirish
```

### Reel Videolar

```
GET    /api/reels/              - Reel videolar
POST   /api/reels/              - Yangi reel yuklash
GET    /api/reels/<id>/comments/ - Reel izohları
```

## 🐛 Troubleshooting

### ModuleNotFoundError: No module named 'rest_framework'

```bash
pip install -r requirements.txt
```

### Permission denied when running migrations

```bash
# Windows
python manage.py migrate

# Linux/macOS
sudo python manage.py migrate
```

### Static files not loading

```bash
python manage.py collectstatic --noinput
```

### Database lock error

```bash
rm db.sqlite3
python manage.py migrate
```

### CORS xatosi

`.env` faylida CORS_ALLOWED_ORIGINS'ni tekshiring.

## 📚 Foydalı Komandalarilar

```bash
# Shell'ga kirish (Django shell)
python manage.py shell

# Database dumpini yaratish
python manage.py dumpdata > backup.json

# Database dumpini qayta joylashtirish
python manage.py loaddata backup.json

# Email test
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Salom', 'test@example.com', ['user@example.com'])

# Logs'ni ko'rish
tail -f logs/django.log
```

## 🔐 Security Checklist

- [ ] SECRET_KEY production'da o'zgartirilgan
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS to'g'ridagi domenlar bilan
- [ ] HTTPS enabled
- [ ] Database passwords secure
- [ ] API keys environment variables'da
- [ ] CORS properly configured
- [ ] SQL injection protection (ORM istifoda)
- [ ] XSS protection (Django templates)
- [ ] CSRF protection enabled
- [ ] Rate limiting configured
- [ ] Logging enabled

## 📞 Qo'shimcha Yordam

Muammo bo'lsa, [Issues](https://github.com/yourusername/online_shop/issues) sahifasida bildirilastiring yoki [Discussions](https://github.com/yourusername/online_shop/discussions)'da savollaringizni so'rashtiring.

## 📄 Lisenziya

MIT License - [LICENSE](LICENSE) faylini ko'ring.

## 👥 Kuxjat

Loyihaga hissa qo'shuvchilarga raxmat! [CONTRIBUTING.md](CONTRIBUTING.md) ni o'qing qo'shimcha tafsilot uchun.
