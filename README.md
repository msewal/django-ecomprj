# Django E-commerce Project

Bu proje, Django kullanılarak geliştirilmiş bir e-ticaret uygulamasıdır.

## Kurulum

1. **Gerekli Paketleri Yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Veritabanı Ayarlarını Yapılandırın:**
   - `settings.py` dosyasında veritabanı ayarlarını kontrol edin. SQLite kullanıyorsanız, ayarlar şu şekilde olmalıdır:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.sqlite3',
             'NAME': BASE_DIR / 'db.sqlite3',
         }
     }
     ```

3. **Veritabanı Migration'larını Uygulayın:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Sunucuyu Başlatın:**
   ```bash
   python manage.py runserver
   ```

5. **Tarayıcıda Projeyi Görüntüleyin:**
   - Tarayıcınızda `http://127.0.0.1:8000/` adresine giderek projenizi görüntüleyebilirsiniz.

## Bağımlılıklar

Projenin bağımlılıkları `requirements.txt` dosyasında listelenmiştir. Bu dosyayı kullanarak gerekli paketleri yükleyebilirsiniz.

## Geliştirme

- **Kod Kalitesi:**
  - `black`, `flake8`, ve `isort` gibi araçları kullanarak kodunuzun kalitesini artırabilirsiniz.

- **Güvenlik:**
  - Projenizin güvenliğini artırmak için `django-cors-headers` gibi güvenlik paketlerini kullanabilirsiniz.

## Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır. 