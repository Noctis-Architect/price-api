# USD Price Scraping & Caching API (v1.0.0)

وب‌سرویس پرسرعت و بهینه‌سازی‌شده برای دریافت نرخ لحظه‌ای دلار (بازار آزاد، اسکناس تهران و صرافی‌ها) با مکانیزم چندمنبعی (Multi-Source Fallback)، کش رم و دیسک (In-Memory & Disk Cache) و به‌روزرسانی خودکار هر ۳۰ دقیقه در پس‌زمینه.

---

## 🚀 ویژگی‌های کلیدی

1. **مکانیزم چندمنبعی با پشتیبان‌گیری خودکار (Failover / Fallback):**
   - منبع ۱: **Bonbast (بن‌بست)** — مرجع اسکناس نقدی دلار آزاد بازار تهران
   - منبع ۲: **TGJU (شبکه اطلاع‌رسانی طلا و ارز)** — استعلام نرخ لحظه‌ای بازار ارز
   - منبع ۳: **TetherLand (تترلند)** — نرخ لحظه‌ای دلار دیجیتال / تتر با نقدینگی بالا
   - منبع ۴: **Ramzinex (رمزینکس)** — نرخ بازار آزاد و سفارشات خرید و فروش
   - منبع ۵: **Wallex (والکس)** — نرخ تتر به تومان
   - *اگر هر یک از منابع دچار قطعی یا محدودیت شود، سیستم بلافاصله از منبع بعدی نرخ را برمی‌گرداند تا سرویس هیچ‌گاه بدون پاسخ نماند.*

2. **سیستم کشینگ سبک و پرسرعت (Ultra-Fast Caching):**
   - پاسخ‌ها مستقیماً از **حافظه رم (In-Memory)** سرو می‌شوند. زمان پاسخ کمتر از **۱ میلی‌ثانیه** است.
   - هیچ درخواستی از سمت کاربران باعث اجرای مجدد اسکرپر یا اشغال منابع سرور نمی‌شود.
   - کش به صورت فایل JSON در `data/cache.json` ذخیره می‌شود تا در صورت ریستارت سرویس نیز بلافاصله اطلاعات بدون تأخیر در دسترس باشد.

3. **به‌روزرسانی خودکار هر ۳۰ دقیقه:**
   - تسک پس‌زمینه (Background Scheduler) هر ۳۰ دقیقه تمام منابع را استعلام کرده و کش را به‌روزرسانی می‌کند.

4. **امنیت و کلید دسترسی (API Key Authentication):**
   - امکان ارسال کلید از طریق Header (`X-API-Key` یا `Authorization: Bearer <KEY>`) و همچنین پارامتر کوئری (`?api_key=<KEY>`).

---

## 🔑 اطلاعات احراز هویت و دامنه

- **دامنه سرور:** `api.wp-hub.org`
- **آی‌پی سرور (جهت تنظیم A Record در DNS):** `91.107.240.253`
- **کلید دسترسی اختصاصی (API Key):**
  ```text
  wphub_0935ce87e51d0a0511ce3393037fd1cb
  ```

---

## 📡 اندپوینت‌ها (Endpoints)

### ۱. دریافت نرخ کامل و جزییات منابع
```http
GET /api/v1/usd
X-API-Key: wphub_0935ce87e51d0a0511ce3393037fd1cb
```
یا با کوئری پارامتر:
```http
GET /api/v1/usd?api_key=wphub_0935ce87e51d0a0511ce3393037fd1cb
```

**نمونه پاسخ:**
```json
{
  "status": "success",
  "currency": "USD",
  "unit": "toman",
  "price": 257400,
  "buy": 257200,
  "sell": 257400,
  "price_rial": 2574000,
  "change_toman": null,
  "change_percent": null,
  "active_source": "bonbast",
  "active_source_name": "Bonbast (بن‌بست)",
  "updated_at": "2026-10-13T11:11:06.623453+00:00",
  "cached": true,
  "cache_age_seconds": 15.2,
  "sources": {
    "bonbast": {
      "source_id": "bonbast",
      "source_name": "Bonbast (بن‌بست)",
      "status": "online",
      "price_toman": 257400,
      "buy_toman": 257200,
      "sell_toman": 257400,
      "price_rial": 2574000
    },
    "tgju": {
      "source_id": "tgju",
      "source_name": "TGJU (شبکه اطلاع‌رسانی طلا و ارز)",
      "status": "online",
      "price_toman": 258705,
      "price_rial": 2587050
    },
    "tetherland": {
      "source_id": "tetherland",
      "source_name": "TetherLand (تترلند)",
      "status": "online",
      "price_toman": 257200
    },
    "ramzinex": {
      "source_id": "ramzinex",
      "status": "online",
      "price_toman": 257149
    },
    "wallex": {
      "source_id": "wallex",
      "status": "online",
      "price_toman": 256200
    }
  }
}
```

---

### ۲. دریافت نرخ خلاصه (فقط قیمت)
با افزودن `?simple=true` خروجی بسیار سبک و بدون متادیتا برگشت داده می‌شود:
```http
GET /api/v1/usd?simple=true&api_key=wphub_0935ce87e51d0a0511ce3393037fd1cb
```

**نمونه پاسخ:**
```json
{
  "price": 257400,
  "buy": 257200,
  "sell": 257400,
  "price_rial": 2574000,
  "unit": "toman",
  "source": "bonbast",
  "updated_at": "2026-10-13T11:11:06.623453+00:00"
}
```

---

### ۳. بررسی سلامت سرویس (Health Check)
```http
GET /api/v1/health
```

**نمونه پاسخ:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "cache_ready": true,
  "cache_age_seconds": 120.4,
  "update_interval_minutes": 30
}
```

---

### ۴. به‌روزرسانی دستی کش (Manual Cache Refresh)
```http
POST /api/v1/refresh
X-API-Key: wphub_0935ce87e51d0a0511ce3393037fd1cb
```

---

## 🛠️ نحوه راه‌اندازی و مدیریت در سرور

### سرویس Systemd
سرویس تحت systemd با نام `price-api.service` پیکربندی شده است:
```bash
# بررسی وضعیت سرویس
sudo systemctl status price-api.service

# ریستارت سرویس
sudo systemctl restart price-api.service

# مشاهده لاگ‌ها
sudo journalctl -u price-api.service -f
```

### تنظیم Nginx و SSL
کانفیگ Nginx در مسیر `/etc/nginx/sites-available/api.wp-hub.org` ایجاد و فعال شده است.

پس از ست کردن رکورد A در کلودفلر/DNS برای `api.wp-hub.org` به آی‌پی `91.107.240.253`:
- در صورت فعال بودن پروکسی کلودفلر (Orange Cloud)، نیاز به اقدام خاصی نیست و SSL کلودفلر خودکار فعال است.
- در صورت اتصال مستقیم (DNS Only)، اسکریپت آماده زیر گواهی Let's Encrypt را فعال می‌کند:
  ```bash
  cd /home/noctis/api-price
  ./scripts/setup_ssl.sh
  ```

---

## 🧪 تست‌های خودکار
برای اجرای تست‌های واحد:
```bash
cd /home/noctis/api-price
./venv/bin/pytest
```
