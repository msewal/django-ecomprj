# ⛽ Petrolist
# *Django E-Commerce Platform*

**Bu proje, Django ile geliştirilmiş bir e-ticaret platformudur. Kullanıcıların ürünleri görüntüleyip sepete ekleyebileceği, sipariş verebileceği ve ödeme yapabileceği dinamik ve genişletilebilir bir sistem sunar.**

## Kullanılan Teknolojiler

- **Backend**: Django, Python
- **Frontend**: HTML, CSS (Bootstrap / custom styles), JavaScript
- **Veritabanı**: SQLite (geliştirme aşamasında)
- **Ödeme Entegrasyonu**: Stripe (test modunda)

---

## Proje Yapısı
```
django-ecomprj/
├── .env
├── requirements.txt 
├── pyproject.toml 
├── ecommerce/
│ ├── manage.py
│ ├── accounts/ # Kullanıcı yönetimi
│ ├── core/ # Ürün, sipariş ve ödeme işlemleri
│ ├── templates/
│ ├── static/ # CSS, JS, görseller
│ ├── db.sqlite3
```
---

## **Özellikler**

### Kullanıcı Sistemi
- Kayıt olma, giriş yapma ve çıkış işlemleri
- Profil yönetimi ve telefon numarası ile ilişkilendirme

### Ürün ve Kategori Yönetimi
- Ürün listeleme, kategoriye göre filtreleme
- Ürün detay sayfası ve yorum yapma özelliği

### Sepet ve Sipariş
- Sepete ürün ekleme/çıkarma
- Sipariş verme ve geçmiş siparişleri görüntüleme
- Sipariş toplam tutar ve adet hesaplama

### Ödeme Sistemi
- Stripe ile ödeme (test modunda)
- Kullanıcıya özel ödeme kaydı ve durumu
---
## **Kurulum**

1. Depoyu klonla:
```bash
git clone https://github.com/msewal/django-ecomprj.git
cd django-ecomprj
```
2. Sanal ortamı oluştur:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
3. Gereksinimleri yükle:
```bash
pip install -r requirements.txt
```
4. .env dosyasını oluştur:
```
SECRET_KEY=your_django_secret
DEBUG=True
STRIPE_PUBLIC_KEY=your_stripe_key
STRIPE_SECRET_KEY=your_stripe_secret
```

5. Veritabanını hazırla:
```
python ecommerce/manage.py makemigrations
python ecommerce/manage.py migrate
```

6. Sunucuyu başlat:
```
python ecommerce/manage.py runserver
```
---
## Test Kullanıcıları
Aşağıdaki test kart bilgileri Stripe tarafından test amaçlı sağlanmaktadır:
---
```
| Kart Numarası       | Tarih | CVC | Açıklama                 |
| ------------------- | ----- | --- | ------------------------ |
| 4242 4242 4242 4242 | 12/34 | 123 | Başarılı ödeme           |
| 4000 0000 0000 9995 | 12/34 | 123 | Yetersiz bakiye          |
| 4000 0025 0000 3155 | 12/34 | 123 | Kimlik doğrulama gerekli |
```

## **Geliştirici**
##### Melek Şevval Erdoğan


#
