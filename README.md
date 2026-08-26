# Online Shop - Django Rest Framework loyihasi

Bu loyiha Django va Django REST Framework dan foydalanib yaratilgan e-commerce (onlayn do'kon) platformasi.

## Loyiha Tuzilmasi

```
online_shop/
├── core/                 # Django loyihasi konfiguratsiyalari
│   ├── settings.py      # Asosiy sozlamalar
│   ├── urls.py          # Asosiy URL yo'naltirilari
│   ├── wsgi.py          # WSGI server konfiguratsiyasi
│   └── asgi.py          # ASGI server konfiguratsiyasi
│
├── store/               # Asosiy aplikatsiya
│   ├── models.py        # Baza ma'lumotlari modellari
│   ├── views.py         # Ko'rinishlar (views)
│   ├── serializers.py   # REST API serialayzerlari
│   ├── forms.py         # Django formlari
│   ├── urls.py          # Store aplikatsiyasi URL'lari
│   ├── admin.py         # Django Admin konfiguratsiyasi
│   ├── migrations/      # Baza migratsiyalari
│   └── templates/       # HTML shablonlari
│
├── media/               # Yuklangan fayllar (rasmlar, videolar)
├── manage.py            # Django boshqaruv skripti
├── db.sqlite3           # SQLite baza ma'lumotlari
├── requirements.txt     # Boʻlimni qaysiligi
└── .gitignore          # Git uchun e'tibor qilmaslik kerak bo'lgan fayllar

```

## Asosiy Modellar

### Profile
- Foydalanuvchining profil ma'lumotlari
- Dostop turlari: Xaridor, Sotuvchi, Admin
- Avatar, telefon raqami, bio

### Product
- Mahsulot ma'lumotlari
- Kategoriya va Brend bilan bog'lanish
- Status: Kutilmoqda, Tasdiqlangan, Rad etilgan

### Category & Brand
- Mahsulot tasnifi va brendlar ro'yxati

### Cart & CartItem
- Savat va savat elementlari

### Order & OrderItem
- Buyurtma boshqaruvi
- Buyurtmadagi mahsulotlar

### ReelsVideo, ReelLike, ReelComment
- Video reels (TikTok kabi)
- Laiklar va izohlar

### ChatMessage
- Foydalanuvchilar orasidagi xabarlar

## Nima Tozalandi va To'g'rilandi

### 1. **settings.py**
- ✅ Import qismini tartibga solish
- ✅ Takrorlangan MEDIA_URL va MEDIA_ROOT o'chirib tashlash
- ✅ EMAIL_BACKEND konfiguratsiyasini to'g'rilash
- ✅ Gemini API kalitini environment variables'ga o'tkazish
- ✅ JWT va REST Framework sozlamalarini to'g'rilash

### 2. **models.py**
- ✅ Profile modeliga avatar va bio qo'shish
- ✅ Product modeliga category va brand bog'lanishlarini qo'shish
- ✅ ReelLike va ReelComment modellarini yaratish
- ✅ Order modeliga customer_name, phone, address va total_price qo'shish
- ✅ Barcha modellarga Meta klassi qo'shish
- ✅ __str__ metodlarini takomillashtirish

### 3. **forms.py**
- ✅ Profile modeliga mos keluvchi formlarni yangilash
- ✅ ProductForm, OrderForm va ReelsVideoForm qo'shish
- ✅ Bootstrap CSS klassilarini qo'shish

### 4. **serializers.py**
- ✅ Barcha modellar uchun to'g'ri serializerlar yaratish
- ✅ Nested serializers bilan munosabat yo'naltirilari
- ✅ ValidationError xabarlarini Uzbek tilida

### 5. **admin.py**
- ✅ Barcha modellar uchun admin registratsiyasi
- ✅ Search, filter va list_editable sozlamalarini qo'shish
- ✅ Fieldsets bilan admin interfeysi takomillashtirish

### 6. **views.py**
- ✅ Template views to'liq qilish
- ✅ REST API endpoints yaratish
- ✅ Autentifikatsiya va avtorizatsiya qo'shish
- ✅ Error handling qo'shish

### 7. **urls.py**
- ✅ Barcha yangi URL patterns bilan yangilash
- ✅ API va template views uchun alohida yo'naltirilari

### 8. **Qo'shimcha Fayllar**
- ✅ .gitignore yaratish
- ✅ requirements.txt yaratish

## Installed Packages

```
Django==6.1
djangorestframework==3.14.0
django-corsheaders==4.3.1
djangorestframework-simplejwt==5.3.2
Pillow==10.1.0
python-decouple==3.8
requests==2.31.0
google-generativeai==0.3.0
```

## O'rnatish va Ishga Tushirish

### 1. Virtual Environment yaratish
```bash
python -m venv venv
```

### 2. Virtual Environmentni aktivlashtirish
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Paketlarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. Migratsiyalarni bajarish
```bash
python manage.py migrate
```

### 5. Super Foydalanuvchi yaratish (Admin)
```bash
python manage.py createsuperuser
```

### 6. Serverini ishga tushirish
```bash
python manage.py runserver
```

Brauzer orqali `http://localhost:8000/` ga o'ting.

## API Endpoints

### Autentifikatsiya
- `POST /api/auth/register/` - Ro'yxatdan o'tish
- `POST /api/auth/login/` - Tizimga kirish
- `POST /api/auth/token/` - Token olish
- `POST /api/auth/token/refresh/` - Token yangilash

### Mahsulotlar
- `GET /api/products/` - Mahsulotlar ro'yxati
- `POST /api/products/` - Yangi mahsulot yaratish
- `GET /api/products/<id>/` - Mahsulot tafsilotlari
- `PUT /api/products/<id>/` - Mahsulotni yangilash
- `DELETE /api/products/<id>/` - Mahsulotni o'chirish

### Kategoriyalar
- `GET /api/categories/` - Kategoriyalar ro'yxati

### Brendlar
- `GET /api/brands/` - Brendlar ro'yxati

### Reel Videolar
- `GET /api/reels/` - Reel videolar ro'yxati
- `POST /api/reels/` - Yangi reel yaratish
- `GET /api/reels/<id>/comments/` - Reel izohları

### Buyurtmalar
- `GET /api/orders/` - Buyurtmalar ro'yxati
- `POST /api/orders/` - Yangi buyurtma yaratish
- `GET /api/orders/<id>/` - Buyurtma tafsilotlari

### Chat
- `GET /api/messages/` - Xabarlar ro'yxati
- `POST /api/messages/` - Yangi xabar yuborish

## Security Tavsiyalari

1. **SECRET_KEY** - Production'da environment variable'dan foydalaning
2. **DEBUG** - Production'da `False` qiling
3. **ALLOWED_HOSTS** - Production'da to'g'ri host larni qo'shing
4. **GEMINI_API_KEY** - Environment variable'da saqlang
5. **HTTPS** - Production'da har doim HTTPS ishlating

## Loyiha Holatı

✅ **Tayyor** - Barcha asosiy xususiyatlar ishga tushirilgan va sog'lom holatda.

## Ushbu Loyihada Istifodalanadigan Texnologiyalar

- **Backend**: Django 6.1
- **API**: Django REST Framework
- **Autentifikatsiya**: JWT (JSON Web Tokens)
- **Baza**: SQLite (Development), PostgreSQL (Production tavsiyasi)
- **Frontend**: HTML, CSS, JavaScript
- **Media Upload**: Pillow (Rasm qayta ishlash)

## Qayta ishlash bo'yicha

Loyiha hozir production'ga tayyor emas. Production'ga ushbu ishlarni bajarishingiz kerak:

1. Database'ni PostgreSQL'ga o'tkazish
2. Statik fayllarni cloud'ga o'tkazish (S3, GCS)
3. Media fayllarni cloud'ga o'tkazish
4. CORS sozlamalarini to'g'rilash
5. Email backend'ni to'g'rilash (SendGrid, Gmail)
6. SSL sertifikatni o'rnatish
7. Environment variables bilan konfiguratsiyani boshqarish

## Muallif

Online Shop Platform 2026

## Lisenziya

MIT License
