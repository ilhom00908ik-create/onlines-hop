# API Documentation - Online Shop

## Base URL

```
http://localhost:8000/api
```

## Authentication

JWT (JSON Web Token) bilan autentifikatsiya:

### Headers

```
Authorization: Bearer <your_access_token>
```

## ✅ Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Muvaffaqiyatli so'rov |
| 201 | Created - Resurs muvaffaqiyatli yaratildi |
| 400 | Bad Request - Noto'g'ri so'rov |
| 401 | Unauthorized - Autentifikatsiya talab qilinadi |
| 403 | Forbidden - Ruxsat yo'q |
| 404 | Not Found - Resurs topilmadi |
| 500 | Server Error - Server xatosi |

---

## 🔐 Authentication Endpoints

### Ro'yxatdan o'tish

```http
POST /auth/register/
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepassword123",
  "password2": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_id": 1,
  "username": "newuser"
}
```

### Tizimga kirish

```http
POST /auth/login/
Content-Type: application/json

{
  "username": "newuser",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_id": 1,
  "username": "newuser"
}
```

### Token Yangilash

```http
POST /auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 🛍️ Product Endpoints

### Mahsulotlar ro'yxati

```http
GET /products/
GET /products/?category=1
GET /products/?status=approved
GET /products/?search=phone
```

**Response (200 OK):**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Samsung Galaxy S23",
      "description": "Eng yangi Samsung telefoniki",
      "price": "999.99",
      "stock": 50,
      "image": "http://localhost:8000/media/products/samsung.jpg",
      "status": "approved",
      "created_at": "2026-08-21T10:30:00Z",
      "updated_at": "2026-08-21T11:00:00Z",
      "seller": 2,
      "seller_name": "seller1",
      "category": {
        "id": 1,
        "name": "Elektronika",
        "slug": "elektronika"
      },
      "brand": {
        "id": 1,
        "name": "Samsung"
      }
    }
  ]
}
```

### Mahsulot yaratish (Sotuvchi)

```http
POST /products/
Authorization: Bearer <token>
Content-Type: multipart/form-data

{
  "name": "Yangi Telefon",
  "description": "Eng yangi model",
  "price": "500.00",
  "stock": "20",
  "image": <file>,
  "category": 1,
  "brand": 1
}
```

**Response (201 Created):**
```json
{
  "id": 51,
  "name": "Yangi Telefon",
  "description": "Eng yangi model",
  "price": "500.00",
  "stock": 20,
  "image": "http://localhost:8000/media/products/...",
  "status": "pending",
  "created_at": "2026-08-21T12:00:00Z",
  "seller": 2,
  "category": 1,
  "brand": 1
}
```

### Mahsulot tafsilotlari

```http
GET /products/1/
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Samsung Galaxy S23",
  "description": "Eng yangi Samsung telefoniki",
  "price": "999.99",
  "stock": 50,
  "image": "http://localhost:8000/media/products/samsung.jpg",
  "status": "approved",
  "created_at": "2026-08-21T10:30:00Z",
  "updated_at": "2026-08-21T11:00:00Z",
  "seller": 2,
  "seller_name": "seller1",
  "category": {
    "id": 1,
    "name": "Elektronika"
  },
  "brand": {
    "id": 1,
    "name": "Samsung"
  }
}
```

### Mahsulotni yangilash

```http
PUT /products/1/
Authorization: Bearer <token>
Content-Type: multipart/form-data

{
  "name": "Samsung Galaxy S24",
  "price": "1099.99",
  "stock": 40
}
```

### Mahsulotni o'chirish

```http
DELETE /products/1/
Authorization: Bearer <token>
```

---

## 📦 Orders Endpoints

### Mening buyurtmalarim

```http
GET /orders/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 3,
      "user_name": "customer1",
      "customer_name": "Ali Karim",
      "phone": "+998901234567",
      "address": "Tashkent, Uzbekistan",
      "total_price": "1599.98",
      "status": "delivered",
      "created_at": "2026-08-20T15:30:00Z",
      "updated_at": "2026-08-21T10:00:00Z",
      "items": [
        {
          "id": 1,
          "product": 1,
          "product_name": "Samsung Galaxy S23",
          "quantity": 1,
          "price": "999.99"
        },
        {
          "id": 2,
          "product": 5,
          "product_name": "Sony Wireless Headphones",
          "quantity": 1,
          "price": "299.99"
        }
      ]
    }
  ]
}
```

### Yangi buyurtma yaratish

```http
POST /orders/
Authorization: Bearer <token>
Content-Type: application/json

{
  "customer_name": "Ali Karim",
  "phone": "+998901234567",
  "address": "Tashkent, Uzbekistan"
}
```

---

## 💬 Chat Endpoints

### Xabarlar ro'yxati

```http
GET /messages/
Authorization: Bearer <token>
```

### Xabar yuborish

```http
POST /messages/
Authorization: Bearer <token>
Content-Type: application/json

{
  "receiver": 2,
  "message": "Assalomu alaykum! Mahsulot haqida savolim bor."
}
```

---

## 🎬 Reels Endpoints

### Reel videolar ro'yxati

```http
GET /reels/
GET /reels/?ordering=-created_at
```

**Response (200 OK):**
```json
{
  "count": 20,
  "results": [
    {
      "id": 1,
      "title": "Yangi mahsulot taqdim etilish",
      "description": "Eng yangi gadjet ko'runi",
      "video_file": "http://localhost:8000/media/product_videos/...",
      "thumbnail": "http://localhost:8000/media/products/...",
      "is_approved": true,
      "created_at": "2026-08-21T09:00:00Z",
      "views_count": 1500,
      "user": 2,
      "user_name": "seller1",
      "likes_count": 250,
      "comments_count": 45
    }
  ]
}
```

### Yangi reel yuklash

```http
POST /reels/
Authorization: Bearer <token>
Content-Type: multipart/form-data

{
  "title": "Yangi smartfon obzor",
  "description": "Telefon haqida batafsil ma'lumot",
  "video_file": <video_file>,
  "thumbnail": <image_file>
}
```

### Reel izohları

```http
GET /reels/1/comments/
```

### Izoh qo'shish

```http
POST /reels/1/comments/
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "Juda yoqdi! Qachon boshqa video bo'ladi?"
}
```

---

## 📂 Categories & Brands

### Kategoriyalar

```http
GET /categories/
```

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "name": "Elektronika",
      "slug": "elektronika"
    },
    {
      "id": 2,
      "name": "Kiyim va oyoq kiyim",
      "slug": "kiyim"
    }
  ]
}
```

### Brendlar

```http
GET /brands/
```

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "name": "Samsung"
    },
    {
      "id": 2,
      "name": "Apple"
    }
  ]
}
```

---

## ⚠️ Error Responses

### 400 Bad Request

```json
{
  "field_name": [
    "Bu maydon talab qilinadi."
  ]
}
```

### 401 Unauthorized

```json
{
  "detail": "Autentifikatsiya kalit topilmadi."
}
```

### 403 Forbidden

```json
{
  "detail": "Faqat yaratuvchi tahrirlashi mumkin."
}
```

### 404 Not Found

```json
{
  "detail": "Sahifa topilmadi."
}
```

---

## 📝 Pagination

Ro'yxat API'lari pagination'ni qo'llab-quvvatlaydi:

```
GET /products/?page=1&page_size=12
```

**Response:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## 🔍 Filtering & Search

### Search

```http
GET /products/?search=phone
```

### Ordering

```http
GET /products/?ordering=-price
GET /products/?ordering=created_at
```

---

## 📚 Rate Limiting

Hozircha rate limiting o'rnatilmagan, lekin production'da tavsiya ediladi:

```python
# settings.py
'DEFAULT_THROTTLE_CLASSES': [
    'rest_framework.throttling.AnonRateThrottle',
    'rest_framework.throttling.UserRateThrottle'
],
'DEFAULT_THROTTLE_RATES': {
    'anon': '100/hour',
    'user': '1000/hour'
}
```

---

## 🧪 Testing API

### cURL bilan Test Qilish

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# Mahsulotlar ro'yxati
curl http://localhost:8000/api/products/

# Token bilan so'rov
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/orders/
```

### Postman bilan Test Qilish

1. Postman'ni o'chib oling
2. `POST` request'ni yarating: `http://localhost:8000/api/auth/login/`
3. Body - raw JSON:
   ```json
   {
     "username": "testuser",
     "password": "password123"
   }
   ```
4. Authorization tab'iga o'tib Bearer Token qo'shing
5. API'ni test qiling!

---

## 📞 Support

Muammolar uchun [GitHub Issues](https://github.com/yourusername/online_shop/issues) sahifasida qaraza bering.
