from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Ana sayfa
    path('', views.index, name='index'),
    
    # Ürün işlemleri
    path('urunler/', views.product_page, name='urun_listesi'),
    path('urun/<int:pk>/', views.urun_ayrinti, name='urun_ayrinti'),
    path('urun/ekle/', views.urun_ekle, name='urun_ekle'),
    path('urun/guncelle/<int:pk>/', views.urun_guncelle, name='urun_guncelle'),
    
    # Sepet işlemleri
    path('sepet/', views.sepet, name='sepet'),
    path('sepet/ekle/<int:pk>/', views.sepete_ekle, name='sepete_ekle'),
    path('sepet/guncelle/<int:item_id>/', views.sepet_guncelle, name='sepet_guncelle'),
    path('sepet/sil/<int:item_id>/', views.sepet_sil, name='sepet_sil'),
    
    # Sipariş işlemleri
    path('siparis/', views.siparis_listesi, name='siparis_listesi'),
    path('siparis/<int:pk>/', views.siparis_detay, name='siparis_detay'),
    path('siparislerim/', views.siparislerim, name='siparislerim'),
    path('odeme/', views.odeme_kontrol, name='odeme_kontrol'),
    path('odeme/tamam/', views.odeme_tamam, name='odeme_tamam'),
    path('yorum/ekle/<int:urun_id>/', views.yorum_ekle, name='yorum_ekle'),
    
    # İletişim ve bilgi sayfaları
    path('iletisim/', views.iletisim, name='iletisim'),
    path('hakkimizda/', views.about, name='about'),
    path('hizmetlerimiz/', views.hizmet, name='hizmet'),
    path('hizmet-sartlari/', views.hizmet_sartlari, name='hizmet_sartlari'),
    path('gizlilik-politikasi/', views.gizlilik_politikasi, name='gizlilik_politikasi'),
    
    # Form işlemleri
    path('bulten/', views.bulten_abonelik, name='bulten_abonelik'),
    path('mesaj/', views.mesaj, name='mesaj'),
    
    # Admin işlemleri
    path('admin/', views.admin_page, name='admin_page'),
    path('admin/siparisler/', views.admin_orders, name='admin_orders'),
    path('admin/siparis/<int:pk>/', views.admin_order_details, name='admin_order_details'),
    path('admin/yorumlar/', views.admin_yorumlar, name='admin_yorumlar'),
    path('admin/yorum/<int:yorum_id>/', views.admin_yorum_yanit, name='admin_yorum_yanit'),
    
    # Payment URLs
    path('payment/success/', views.payment_successful, name='payment_successful'),
    path('payment/cancelled/', views.payment_cancelled, name='payment_cancelled'),
    path('payment/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('payment/create-checkout-session/<int:order_id>/', views.create_checkout_session, name='create_checkout_session'),
]


