from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django_countries.fields import CountryField
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils import timezone
import uuid

# Define your existing models
class Musteri(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='musteri')
    tel_no = models.CharField(max_length=12, verbose_name="Telefon Numarası")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.tel_no}"

    class Meta:
        verbose_name_plural = "Müşteriler"

class Kategori(models.Model):
    isim = models.CharField(max_length=100, default="")
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    resim = models.ImageField(upload_to='static/img/categories/', verbose_name="Kategori Resmi", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.isim)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.isim

    class Meta:
        verbose_name_plural = "Kategoriler"

    @classmethod
    def get_all_categories(cls):
        return cls.objects.all()

class Urun(models.Model):
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE, related_name='urunler')
    isim = models.CharField(max_length=200)
    aciklama = models.TextField()
    fiyat = models.DecimalField(max_digits=10, decimal_places=2)
    stok = models.PositiveIntegerField(default=0)
    resim = models.ImageField(upload_to='static/img/products/', verbose_name="Ürün Resmi")
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    aktif = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.isim)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.isim

    def get_absolute_url(self):
        return reverse('urun_ayrinti', kwargs={'pk': self.pk})

    class Meta:
        verbose_name_plural = "Ürünler"

class Sepet(models.Model):
    kullanici = models.ForeignKey(User, on_delete=models.CASCADE)
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE)
    adet = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.kullanici.username} - {self.urun.isim}"

    class Meta:
        verbose_name_plural = "Sepetler"

class Siparis(models.Model):
    SiparisDurumu = (
        ('beklemede', 'Beklemede'),
        ('onaylandi', 'Onaylandı'),
        ('kargoda', 'Kargoda'),
        ('tamamlandi', 'Tamamlandı'),
        ('iptal', 'İptal Edildi'),
    )

    kullanici = models.ForeignKey(User, on_delete=models.CASCADE)
    siparis_no = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    ad = models.CharField(max_length=100)
    soyad = models.CharField(max_length=100)
    email = models.EmailField()
    telefon = models.CharField(max_length=20)
    adres = models.TextField()
    sehir = models.CharField(max_length=100)
    ulke = models.CharField(max_length=100)
    posta_kodu = models.CharField(max_length=20)
    toplam_tutar = models.DecimalField(max_digits=10, decimal_places=2)
    durum = models.CharField(max_length=20, choices=SiparisDurumu, default='beklemede')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sipariş #{self.siparis_no}"

    class Meta:
        verbose_name_plural = "Siparişler"

class SiparisEdilenler(models.Model):
    siparis = models.ForeignKey(Siparis, on_delete=models.CASCADE, related_name='siparis_edilenler')
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE)
    adet = models.PositiveIntegerField(default=1)
    fiyat = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.siparis.siparis_no} - {self.urun.isim}"

    class Meta:
        verbose_name_plural = "Sipariş Edilenler"

class Yorum(models.Model):
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE, related_name='yorumlar')
    kullanici = models.ForeignKey(User, on_delete=models.CASCADE)
    yorum = models.TextField()
    puan = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    admin_reply = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    aktif = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.kullanici.username} - {self.urun.isim}"

    class Meta:
        verbose_name_plural = "Yorumlar"
        ordering = ['-created_at']

class YorumYanit(models.Model):
    yorum = models.ForeignKey(Yorum, on_delete=models.CASCADE, related_name='yanitlar')
    kullanici = models.ForeignKey(User, on_delete=models.CASCADE)
    yanit = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return f"Yanıt: {self.yorum}"

    class Meta:
        verbose_name_plural = "Yorum Yanıtları"

class BultenAboneligi(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = "Bülten Abonelikleri"

class IletisimMesaji(models.Model):
    ad = models.CharField(max_length=100)
    email = models.EmailField()
    konu = models.CharField(max_length=200)
    mesaj = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    okundu = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.ad} - {self.konu}"

    class Meta:
        verbose_name_plural = "İletişim Mesajları"
        ordering = ['-created_at']

class AppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "Uygulama Kullanıcıları"

class UserPayment(models.Model):
    app_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    payment_bool = models.BooleanField(default=False)
    stripe_checkout_id = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Payment for {self.app_user.username}'

    class Meta:
        verbose_name_plural = "Kullanıcı Ödemeleri"

@receiver(post_save, sender=User)
def create_user_payment(sender, instance, created, **kwargs):
    if created:
        UserPayment.objects.create(app_user=instance)

class Odeme_Adresi(models.Model):
    Kullanıcı = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adresler')
    Mahalle = models.CharField(max_length=100, default="")
    Sokak_Adresi = models.CharField(max_length=50)
    Bina_No = models.CharField(max_length=100)
    Daire_No = models.CharField(max_length=100, default="")
    Il = models.CharField(max_length=50, default="")
    Ilce = models.CharField(max_length=50, default="")
    Ülke = CountryField()
    Posta_Kodu = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.Kullanıcı.username} - {self.Sokak_Adresi}"

    class Meta:
        verbose_name_plural = "Ödeme Adresleri"