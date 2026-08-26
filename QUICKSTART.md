# 🚀 QUICKSTART - Online Shop Django

## Eng tez yo'l bilan lokalta ishga tushirish

### 1️⃣ Repository'ni Klonlash

```bash
git clone https://github.com/yourusername/online_shop.git
cd online_shop
```

### 2️⃣ Virtual Environment (Windows)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Virtual Environment (Linux/macOS)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4️⃣ Paketlarni O'rnatish

```bash
pip install -r requirements.txt
```

### 5️⃣ Migratsiyalarni Bajarish

```bash
python manage.py migrate
```

### 6️⃣ Sample Ma'lumot Qo'shish (Ixtiyoriy)

```bash
python manage.py seed_data
```

Login: `admin` / `admin123`

### 7️⃣ Serverini Ishga Tushirish

```bash
python manage.py runserver
```

### 8️⃣ Brauzerda Ochish

```
http://localhost:8000
Admin: http://localhost:8000/admin
API: http://localhost:8000/api
```

---

## Docker bilan Ishga Tushirish (Eng oson)

```bash
# Environment faylini yaratish
copy .env.example .env

# Docker containers'ni ishga tushirish
docker-compose up -d

# Migratsiyalarni bajarish (automatic)
docker-compose exec web python manage.py migrate

# Admin yaratish (ixtiyoriy)
docker-compose exec web python manage.py createsuperuser

# Logs ko'rish
docker-compose logs -f web
```

**Access:**
- App: `http://localhost`
- Admin: `http://localhost/admin`
- API: `http://localhost/api`

---

## Testing

```bash
# Barcha testlarni bajarish
python manage.py test

# Pytest bilan
pytest

# Coverage bilan
pytest --cov=store --cov-report=html
```

---

## API Test Qilish

### cURL

```bash
# Ro'yxatdan o'tish
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "test123456",
    "password2": "test123456"
  }'

# Tizimga kirish
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "test123456"}'

# Mahsulotlarni ko'rish
curl http://localhost:8000/api/products/
```

---

## Foydalanuvchiga buyrultmalar

### Admin Panelga Kirish

1. Go to `http://localhost:8000/admin`
2. Credentials:
   - Username: `admin`
   - Password: `admin123` (seed_data bilan yaratilgan)

### Mahsulot Yaratish (Sotuvchi)

1. Login: `seller1` / `seller123`
2. Go to `http://localhost:8000/seller/dashboard`
3. Mahsulot qo'shish tugmasini bosing

### Savat va Buyurtma

1. Mahsulotlarni ko'rish
2. "Savatga qo'shish" tugmasini bosing
3. Savatka o'tish: `http://localhost:8000/cart`
4. Checkout: `http://localhost:8000/checkout`

---

## Helpful Commands

```bash
# admin yaratish
python manage.py createsuperuser

# Shell (Python repl)
python manage.py shell

# Database reset
python manage.py flush

# Migrations ko'rish
python manage.py showmigrations

# Specific migration'ni qaytarish
python manage.py migrate store 0001

# Static files to'plash
python manage.py collectstatic --noinput

# Server norsatini o'zgartirish
python manage.py runserver 0.0.0.0:8080
```

---

## Troubleshooting

| Masala | Yechim |
|--------|--------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| Database error | `python manage.py migrate` |
| Static files yo'q | `python manage.py collectstatic --noinput` |
| Port 8000 band | `python manage.py runserver 8001` |
| Permission error | `sudo` bilan bajarish yoki Windows Administrator mode |

---

## Production Deployment

Production'ga chiqarish uchun:

1. [SETUP.md](SETUP.md) - O'rnatish ko'rsatmasi
2. [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Deployment checklist
3. [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API dokumentatsiya

---

## 📚 Ko'proq Ma'lumot

- [README.md](README.md) - Asl Readme
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Full API docs
- [SETUP.md](SETUP.md) - Setup guide
- [Django Docs](https://docs.djangoproject.com/)

---

## ❓ Savol Bo'lsa

- [GitHub Issues](https://github.com/yourusername/online_shop/issues)
- [GitHub Discussions](https://github.com/yourusername/online_shop/discussions)

Ommaviy qo'llab-quvvatlash yo'lida berishni unutmaydi! 🙏
