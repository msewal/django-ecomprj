from django.contrib import admin
from .models import (
    Musteri, Kategori, Urun, Sepet, Siparis, SiparisEdilenler,
    Yorum, YorumYanit, BultenAboneligi, IletisimMesaji,
    AppUser, UserPayment, Odeme_Adresi
)

@admin.register(Musteri)
class MusteriAdmin(admin.ModelAdmin):
    list_display = ('user', 'tel_no', 'created_at')
    search_fields = ('user__username', 'tel_no')
    list_filter = ('created_at',)

@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ('isim', 'slug', 'created_at')
    search_fields = ('isim',)
    prepopulated_fields = {'slug': ('isim',)}

@admin.register(Urun)
class UrunAdmin(admin.ModelAdmin):
    list_display = ('isim', 'kategori', 'fiyat', 'stok', 'aktif', 'created_at')
    list_filter = ('kategori', 'aktif', 'created_at')
    search_fields = ('isim', 'aciklama')
    prepopulated_fields = {'slug': ('isim',)}

@admin.register(Sepet)
class SepetAdmin(admin.ModelAdmin):
    list_display = ('kullanici', 'urun', 'adet', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('kullanici__username', 'urun__isim')

@admin.register(Siparis)
class SiparisAdmin(admin.ModelAdmin):
    list_display = ('siparis_no', 'kullanici', 'toplam_tutar', 'durum', 'created_at')
    list_filter = ('durum', 'created_at')
    search_fields = ('siparis_no', 'kullanici__username', 'ad', 'soyad', 'email')
    readonly_fields = ('siparis_no',)

@admin.register(SiparisEdilenler)
class SiparisEdilenlerAdmin(admin.ModelAdmin):
    list_display = ('siparis', 'urun', 'adet', 'fiyat', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('siparis__siparis_no', 'urun__isim')

@admin.register(Yorum)
class YorumAdmin(admin.ModelAdmin):
    list_display = ('kullanici', 'urun', 'puan', 'aktif', 'is_approved', 'created_at')
    list_filter = ('aktif', 'is_approved', 'created_at')
    search_fields = ('kullanici__username', 'urun__isim', 'yorum')
    list_editable = ('aktif', 'is_approved')

@admin.register(YorumYanit)
class YorumYanitAdmin(admin.ModelAdmin):
    list_display = ('yorum', 'kullanici', 'aktif', 'created_at')
    list_filter = ('aktif', 'created_at')
    search_fields = ('yorum__yorum', 'kullanici__username', 'yanit')

@admin.register(BultenAboneligi)
class BultenAboneligiAdmin(admin.ModelAdmin):
    list_display = ('email', 'aktif', 'created_at')
    list_filter = ('aktif', 'created_at')
    search_fields = ('email',)

@admin.register(IletisimMesaji)
class IletisimMesajiAdmin(admin.ModelAdmin):
    list_display = ('ad', 'email', 'konu', 'okundu', 'created_at')
    list_filter = ('okundu', 'created_at')
    search_fields = ('ad', 'email', 'konu', 'mesaj')
    list_editable = ('okundu',)

@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)

@admin.register(UserPayment)
class UserPaymentAdmin(admin.ModelAdmin):
    list_display = ('app_user', 'payment_bool', 'created_at')
    list_filter = ('payment_bool', 'created_at')
    search_fields = ('app_user__username', 'stripe_checkout_id')

@admin.register(Odeme_Adresi)
class OdemeAdresiAdmin(admin.ModelAdmin):
    list_display = ('Kullanıcı', 'Sokak_Adresi', 'Il', 'Ilce', 'created_at')
    list_filter = ('Il', 'Ilce', 'created_at')
    search_fields = ('Kullanıcı__username', 'Sokak_Adresi', 'Il', 'Ilce')