from datetime import datetime
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import (
    UrunForm, CheckoutForm, YorumForm, AdminCommentForm,
    IletisimMesajiForm, BultenAbonelikForm, SiparisForm,
    OdemeAdresiForm, UrunAramaFormu, YorumYanitForm
)
from .models import (
    Urun, SiparisEdilenler, Siparis, Odeme_Adresi, UserPayment,
    Musteri, Kategori, Yorum, YorumYanit, BultenAboneligi,
    IletisimMesaji, AppUser
)

from django.contrib.admin.views.decorators import staff_member_required
from .models import Siparis, Urun, Musteri, Comment
from .forms import UrunForm, CommentReplyForm, CommentForm

from .models import Kategori, Musteri
from .forms import UrunUpdateForm, AdminCommentForm
from django.core.exceptions import ObjectDoesNotExist
from .forms import NewsletterSubscriptionForm, ContactMessageForm

from django.http import JsonResponse
from django.views.decorators.http import require_POST

import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from django.contrib.auth.decorators import user_passes_test

from django.db.models import Q
from .forms import UrunAramaFormu
from django.core.paginator import Paginator

stripe.api_key = settings.STRIPE_SECRET_KEY


# Ana sayfa ve ürünlerin listelendiği sayfa
def index(request):
    try:
        kategoriler = Kategori.objects.all()
        urunler = Urun.objects.filter(aktif=True).order_by('-created_at')[:8]
        context = {
            'kategoriler': kategoriler,
            'urunler': urunler,
        }
        return render(request, 'core/index.html', context)
    except Exception as e:
        messages.error(request, f"Bir hata oluştu: {str(e)}")
        return render(request, 'core/index.html', {})

# Ürün ekleme sayfası
def urun_ekle(request):
    if request.method == 'POST':
        form = UrunForm(request.POST, request.FILES)
        if form.is_valid():
            title = request.POST.get('title')
            product = form.save(commit=False)
            product.user = request.user
            product.save()            
            messages.success(request, 'Ürün başarıyla eklendi!')
            return redirect('index')  # Adjust the redirect as necessary
        else:
            messages.error(request, 'Form hatalı, lütfen tekrar deneyin.')
    else:
        form = UrunForm()
    return render(request, 'core/urun_ekle.html', {'form': form})


# Sepete ürün ekleme
@login_required
@csrf_protect
def sepete_ekle(request, pk):
    """Add item to cart with proper error handling"""
    try:
        urun = get_object_or_404(Urun, pk=pk, aktif=True)
        if urun.mevcut_urun_sayisi <= 0:
            messages.error(request, "Bu ürün stokta yok.")
            return redirect('urun_ayrinti', pk=pk)
        
        order_item, created = SiparisEdilenler.objects.get_or_create(
            urun=urun,
            user=request.user,
            ordered=False
        )
        order_qs = Siparis.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.items.filter(urun__pk=urun.pk).exists():
                order_item.quantity += 1
                order_item.save()
                urun.mevcut_urun_sayisi -= 1
                urun.save()
                messages.success(request, "Ürün miktarı artırıldı.")
            else:
                order.items.add(order_item)
                urun.mevcut_urun_sayisi -= 1
                urun.save()
                messages.success(request, "Ürün sepete eklendi.")
        else:
            order_date = timezone.now()
            order = Siparis.objects.create(user=request.user, ordered_date=order_date)
            order.items.add(order_item)
            urun.mevcut_urun_sayisi -= 1
            urun.save()
            messages.success(request, "Ürün sepete eklendi.")
        return redirect('urun_ayrinti', pk=pk)
    except Exception as e:
        messages.error(request, f"Ürün sepete eklenirken bir hata oluştu: {str(e)}")
        return redirect('product_page')


# Sipariş listesi sayfası
@login_required
@csrf_protect
def siparis_listesi(request):
    """Display order list with proper error handling"""
    try:
        orders = Siparis.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'core/siparis_listesi.html', {'orders': orders})
    except Exception as e:
        messages.error(request, f"Siparişler yüklenirken bir hata oluştu: {str(e)}")
        return render(request, 'core/siparis_listesi.html', {'orders': []})

# Sepetten ürün çıkarma
@login_required
def nesneyi_sil(request, pk):
    urun = get_object_or_404(Urun, pk=pk)
    order_qs = Siparis.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs.first()  # ilk siparişi almak için first() metodunu kullanmak daha semantik
        order_item_qs = order.items.filter(urun=urun, ordered=False)
        if order_item_qs.exists():
            order_item = order_item_qs.first()
            order_item.delete()
            messages.error(request, "Ürün sepetten çıkarıldı.")
        else:
            messages.error(request, "Bu ürün sepetinizde bulunmamaktadır.")
    else:
        messages.error(request, "Aktif bir siparişiniz bulunmamaktadır.")
    return redirect('siparis_listesi')

@login_required
def nesneyi_azalt(request, pk):
    urun = get_object_or_404(Urun, pk=pk)
    order_qs = Siparis.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs.first()
        order_item_qs = SiparisEdilenler.objects.filter(
            urun=urun,
            user=request.user,
            ordered=False
        )
        
        if order_item_qs.exists():
            order_item = order_item_qs.first()
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.success(request, "Ürün miktarı azaltıldı.")
            else:
                order.items.remove(order_item)
                order_item.delete()
                messages.success(request, "Ürün sepetten çıkarıldı.")
        else:
            messages.info(request, "Bu ürün sepetinizde bulunmamaktadır.")
    else:
        messages.info(request, "Aktif bir siparişiniz bulunmamaktadır.")

    return redirect('siparis_listesi')

@login_required
def nesne_ekle(request, pk):
    urun = get_object_or_404(Urun, pk=pk)
    order_qs = Siparis.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs.first()
    else:
        order = Siparis.objects.create(user=request.user, ordered_date=timezone.now())

    order_item, created = SiparisEdilenler.objects.get_or_create(
        urun=urun,
        user=request.user,
        ordered=False
    )
    if created:
        order.items.add(order_item)
        messages.success(request, "Ürün sepete eklendi.")
    else:
        order_item.quantity += 1
        order_item.save()
        messages.success(request, "Ürün miktarı artırıldı.")

    return redirect('siparis_listesi')

@csrf_protect
def product_page(request):
    """Display all products with proper error handling"""
    try:
        products = Urun.objects.all().order_by('-created_at')
        return render(request, 'core/product_page.html', {'products': products})
    except Exception as e:
        messages.error(request, f"Ürünler yüklenirken bir hata oluştu: {str(e)}")
        return render(request, 'core/product_page.html', {'products': []})

def create_checkout_session(request, order_id):
    order = get_object_or_404(Siparis, id=order_id)
    total_price = order.get_total_price() * 100  # Convert to cents
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Order {}'.format(order_id),
                },
                'unit_amount': total_price,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('payment_successful')),
        cancel_url=request.build_absolute_uri(reverse('payment_cancelled')),
    )
    order.stripe_checkout_id = session['id']
    order.save()
    return redirect(session.url, code=303)


@login_required
def payment_successful(request):
    """Handle successful payment with proper error handling"""
    try:
        # Mevcut siparişi bul
        siparisler = Siparis.objects.filter(user=request.user, ordered=False)
        if siparisler.exists():
            siparis = siparisler.first()
            siparis.ordered = True
            siparis.ordered_date = timezone.now()  # Sipariş tarihini güncelle
            siparis.save()
            
            # Stok miktarını güncelle
            for item in siparis.items.all():
                urun = item.urun
                urun.mevcut_urun_sayisi -= item.quantity
                urun.save()
            
            # Sepeti sıfırla
            siparis.items.clear()
            
            messages.success(request, "Ödeme tamamlandı! Siparişiniz başarıyla oluşturuldu.")
            return redirect('siparislerim')
        else:
            messages.error(request, "Sipariş bulunamadı.")
            return redirect('index')
        return render(request, 'core/payment_successful.html')
    except Exception as e:
        messages.error(request, f"Sayfa yüklenirken bir hata oluştu: {str(e)}")
        return redirect('index')

@login_required
def payment_cancelled(request):
    """Handle cancelled payment with proper error handling"""
    try:
        messages.error(request, "Ödeme iptal edildi!")
        return render(request, 'core/payment_cancelled.html')
    except Exception as e:
        messages.error(request, f"Sayfa yüklenirken bir hata oluştu: {str(e)}")
        return redirect('index')



@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhooks with proper error handling"""
    try:
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            return HttpResponse(status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            handle_payment_intent_succeeded(session)

        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(status=400)


# Siparişin tamamlandığını belirten fonksiyon
def handle_payment_intent_succeeded(session):
    order_id = session.get('client_reference_id')
    order = Siparis.objects.get(stripe_checkout_id=session['id'])
    order.ordered = True
    order.save()

    # Sepeti sıfırla
    Siparis.objects.filter(user=order.user, ordered=True).delete()

@login_required
def odeme_tamam(request):
    # Mevcut siparişi bul
    siparisler = Siparis.objects.filter(user=request.user, ordered=False)
    if siparisler.exists():
        siparis = siparisler.first()
        siparis.ordered = True
        siparis.ordered_date = timezone.now()  # Sipariş tarihini güncelle
        siparis.save()
        
        # Stok miktarını güncelle
        for item in siparis.items.all():
            urun = item.urun
            urun.mevcut_urun_sayisi -= item.quantity
            urun.save()
        
        # Sepeti sıfırla
        siparis.items.clear()
        
        messages.success(request, "Ödeme tamamlandı! Siparişiniz başarıyla oluşturuldu.")
        return redirect('siparislerim')
    else:
        messages.error(request, "Sipariş bulunamadı.")
        return redirect('index')
    
@login_required
def siparis_detay(request, pk):
    siparis = get_object_or_404(Siparis, id=pk, user=request.user)
    return render(request, 'core/siparis_detay.html', {'siparis': siparis})

@login_required
def siparislerim(request):
    siparisler = Siparis.objects.filter(user=request.user, ordered=True, order_delivered=True).order_by('-ordered_date')
    onayBekleyen = Siparis.objects.filter(user=request.user, ordered=True, order_delivered=False).order_by('-ordered_date')

    return render(request, 'core/siparislerim.html', {
        'siparisler': siparisler,
        'onayBekleyen': onayBekleyen
        })

def portfolio(request):
    kategoriler = Kategori.objects.all()
    urunler = Urun.objects.all()
    return render(request, 'core/index.html', {'kategoriler': kategoriler, 'urunler': urunler})

def about(request):
    """About page with proper error handling"""
    try:
        return render(
            request,
            'core/about.html',
            {
                'title':'PETROLİST Hakkında',
                'message':'',
                'year':datetime.now().year,
            }
        )
    except Exception as e:
        messages.error(request, f"Sayfa yüklenirken bir hata oluştu: {str(e)}")
        return redirect('index')

def hizmet(request):
    """Services page with proper error handling"""
    try:
        return render(
            request,
            'core/hizmet.html',
            {
                'title':'PETROLİST Olarak Verdiğimiz Diğer Hizmetler',
                'message':'',
                'year':datetime.now().year,
            }
        )
    except Exception as e:
        messages.error(request, f"Sayfa yüklenirken bir hata oluştu: {str(e)}")
        return redirect('index')
def hizmet_sartlari(request):
    """Terms of service page with proper error handling"""
    try:
        return render(
            request,
            'core/hizmet_sartlari.html',
            {
                'title':'PETROLİST - Hizmet Şartları',
                'message':'',
                'year':datetime.now().year,
            }
        )
    except Exception as e:
        messages.error(request, f"Sayfa yüklenirken bir hata oluştu: {str(e)}")
        return redirect('index')
def gizlilik_politikasi(request):
    """Privacy policy page with proper error handling"""
    try:
        return render(
            request,
            'core/gizlilik_politikasi.html',
            {
                'title':'PETROLİST - Gizlilik Politikamız',
                'message':'',
                'year':datetime.now().year,
            }
        )
    except Exception as e:
        messages.error(request, f"Sayfa yüklenirken bir hata oluştu: {str(e)}")
        return redirect('index')
# views.py

@csrf_protect
def subscribe_newsletter(request):
    """Handle newsletter subscription with proper error handling"""
    try:
        if request.method == 'POST':
            form = BultenAbonelikForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Abone olduğunuz için teşekkür ederiz!")
                return redirect('index')
            else:
                messages.error(request, "Bu e-posta zaten kayıtlı.")
        else:
            form = BultenAbonelikForm()
        
        return render(request, 'core/subscribe.html', {'form': form})
    except Exception as e:
        messages.error(request, f"Abonelik işlemi sırasında bir hata oluştu: {str(e)}")
        return redirect('index')



@csrf_protect
def mesaj(request):
    """Handle contact form submission with proper error handling"""
    try:
        form = IletisimMesajiForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.success(request, "Mesajınız gönderildi. Teşekkürler!")
                return redirect('iletisim')
            else:
                messages.error(request, "Formu gönderirken bir hata oluştu. Lütfen tekrar deneyin.")
        else:
            form = IletisimMesajiForm()

        return render(request, 'core/mesaj.html', {'form': form})
    except Exception as e:
        messages.error(request, f"Mesaj gönderilirken bir hata oluştu: {str(e)}")
        return redirect('iletisim')


@csrf_protect
def urun_ayrinti(request, pk):
    """Display product details with proper error handling"""
    try:
        urun = get_object_or_404(Urun, pk=pk, aktif=True)
        comments = urun.comments.all()
        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user
                comment.urun = urun
                comment.save()
                messages.success(request, 'Yorumunuz gönderildi!')
                return redirect('urun_ayrinti', pk=pk)
        else:
            form = CommentForm()
        return render(request, 'core/urun_ayrinti.html', {'urun': urun, 'comments': comments, 'form': form})
    except Exception as e:
        messages.error(request, f"Ürün detayları yüklenirken bir hata oluştu: {str(e)}")
        return redirect('product_page')

@csrf_protect
def admin_comments(request):
    """Admin comment management with proper error handling"""
    try:
        comments = Comment.objects.all().order_by('-created_at')
        return render(request, 'core/admin_comments.html', {'comments': comments})
    except Exception as e:
        messages.error(request, f"Yorumlar yüklenirken bir hata oluştu: {str(e)}")
        return redirect('admin_page')

#####
@csrf_protect
def odeme_kontrol(request):
    try:
        form = CheckoutForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                new_address = form.save(commit=False)
                new_address.Kullanıcı = request.user
                new_address.save()
                order = Siparis.objects.filter(user=request.user, ordered=False).first()
                return redirect('create_checkout_session', order_id=order.id)
            else:
                messages.error(request, "Form Geçersiz!")
                return render(request, 'core/odeme_kontrol.html', {'form': form})
        else:
            form = CheckoutForm()
            order = Siparis.objects.filter(user=request.user, ordered=False).first()
            return render(request, 'core/odeme_kontrol.html', {'form': form, 'stripe_public_key': settings.STRIPE_PUBLIC_KEY, 'order': order})
    except Exception as e:
        messages.error(request, f"Bir hata oluştu: {str(e)}")
        return redirect('sepet')

@require_POST
def create_checkout_session(request, order_id):
    order = get_object_or_404(Siparis, id=order_id)
    domain_url = request.build_absolute_uri('/')
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Order {}'.format(order.id),
                        },
                        'unit_amount': int(order.get_total_price() * 100),  # Convert price to cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=domain_url + 'payment_successful/',
            cancel_url=domain_url + 'payment_cancelled/',
        )
        return JsonResponse({
            'id': checkout_session.id
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        })

    ####

def is_superuser(user):
    return user.is_superuser



#@user_passes_test(is_superuser)

@staff_member_required
def admin_page(request):
    """Admin dashboard with proper error handling"""
    try:
        urunler = Urun.objects.all()
        musteriler = Musteri.objects.all()
        yorumlar = Comment.objects.all()
        siparisler = Siparis.objects.filter(ordered=True).order_by('-ordered_date')
        total_orders = Siparis.objects.count()
        total_products = Urun.objects.count()
        recent_orders = Siparis.objects.order_by('-created_at')[:5]
        return render(request, 'core/admin_page.html', {
            'urunler': urunler,
            'musteriler': musteriler,
            'yorumlar': yorumlar,
            'siparisler': siparisler,
            'total_orders': total_orders,
            'total_products': total_products,
            'recent_orders': recent_orders
        })
    except Exception as e:
        messages.error(request, f"Admin paneli yüklenirken bir hata oluştu: {str(e)}")
        return redirect('index')

@staff_member_required
def admin_orders(request):
    """Admin order management with proper error handling"""
    try:
        siparisler = Siparis.objects.filter(ordered=True).order_by('-ordered_date')
        return render(request, 'core/admin_orders.html', {'siparisler': siparisler})
    except Exception as e:
        messages.error(request, f"Siparişler yüklenirken bir hata oluştu: {str(e)}")
        return redirect('admin_page')

@staff_member_required
def admin_order_details(request, pk):
    siparis = get_object_or_404(Siparis, pk=pk)
    return render(request, 'core/admin_order_details.html', {'siparis': siparis})

@staff_member_required
def urun_guncelle(request, pk):
    urun = get_object_or_404(Urun, pk=pk)
    if request.method == 'POST':
        form = UrunForm(request.POST, request.FILES, instance=urun)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ürün başarıyla güncellendi!')
            return redirect('admin_page')
    else:
        form = UrunForm(instance=urun)
    return render(request, 'core/urun_guncelle.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_comment_reply(request, comment_id):
    """Admin comment reply with proper error handling"""
    try:
        comment = get_object_or_404(Comment, id=comment_id)
        if request.method == 'POST':
            reply = request.POST.get('reply')
            comment.reply = reply
            comment.replied_at = timezone.now()
            comment.save()
            messages.success(request, "Yanıt başarıyla kaydedildi")
            return redirect('admin_comments')
        return render(request, 'core/admin_comment_reply.html', {'comment': comment})
    except Exception as e:
        messages.error(request, f"Yanıt kaydedilirken bir hata oluştu: {str(e)}")
        return redirect('admin_comments')
######



##############################################


@staff_member_required
def admin_page(request):
    urunler = Urun.objects.all()
    musteriler = Musteri.objects.all()
    yorumlar = Comment.objects.all()
    return render(request, 'core/admin_page.html', {
        'urunler': urunler,
        'musteriler': musteriler,
        'yorumlar': yorumlar,
    })
def admin(request):
    return render(request, 'admin.html')
                  
@staff_member_required
def admin_orders(request):
    siparisler = Siparis.objects.filter(ordered=True).order_by('-ordered_date')
    return render(request, 'core/admin_orders.html', {'siparisler': siparisler})

@staff_member_required
def admin_order_details(request, pk):
    siparis = get_object_or_404(Siparis, pk=pk)
    return render(request, 'core/admin_order_details.html', {'siparis': siparis})

@staff_member_required
def urun_guncelle(request, pk):
    urun = get_object_or_404(Urun, pk=pk)
    if request.method == 'POST':
        form = UrunForm(request.POST, request.FILES, instance=urun)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ürün başarıyla güncellendi!')
            return redirect('admin_page')
    else:
        form = UrunForm(instance=urun)
    return render(request, 'core/urun_guncelle.html', {'form': form})

@login_required
def sepet(request):
    """Display shopping cart with proper error handling"""
    try:
        order = Siparis.objects.filter(user=request.user, ordered=False).first()
        if order:
            items = order.items.all()
            total = sum(item.urun.fiyat * item.adet for item in items)
            return render(request, 'core/sepet.html', {
                'items': items,
                'total': total,
                'order': order
            })
        return render(request, 'core/sepet.html', {'items': [], 'total': 0})
    except Exception as e:
        messages.error(request, f"Sepet yüklenirken bir hata oluştu: {str(e)}")
        return render(request, 'core/sepet.html', {'items': [], 'total': 0})

@login_required
@require_POST
def sepet_guncelle(request, item_id):
    """Update cart item quantity with proper error handling"""
    try:
        item = get_object_or_404(SiparisEdilenler, id=item_id, user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            item.adet = quantity
            item.save()
            messages.success(request, "Ürün miktarı güncellendi.")
        else:
            item.delete()
            messages.success(request, "Ürün sepetten kaldırıldı.")
            
        return redirect('sepet')
    except Exception as e:
        messages.error(request, f"Sepet güncellenirken bir hata oluştu: {str(e)}")
        return redirect('sepet')

@login_required
@require_POST
def sepet_sil(request, item_id):
    """Remove item from cart with proper error handling"""
    try:
        item = get_object_or_404(SiparisEdilenler, id=item_id, user=request.user)
        item.delete()
        messages.success(request, "Ürün sepetten kaldırıldı.")
        return redirect('sepet')
    except Exception as e:
        messages.error(request, f"Ürün sepetten kaldırılırken bir hata oluştu: {str(e)}")
        return redirect('sepet')

@csrf_protect
def iletisim(request):
    """Contact page with proper error handling"""
    try:
        if request.method == 'POST':
            form = ContactMessageForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Mesajınız başarıyla gönderildi!")
                return redirect('iletisim')
            else:
                messages.error(request, "Lütfen formu doğru şekilde doldurun.")
        else:
            form = ContactMessageForm()
            
        return render(request, 'core/iletisim.html', {
            'form': form,
            'title': 'İletişim',
            'year': datetime.now().year,
        })
    except Exception as e:
        messages.error(request, f"Sayfa yüklenirken bir hata oluştu: {str(e)}")
        return redirect('index')

@login_required
def yorum_ekle(request, urun_id):
    urun = get_object_or_404(Urun, id=urun_id)
    if request.method == 'POST':
        form = YorumForm(request.POST)
        if form.is_valid():
            yorum = form.save(commit=False)
            yorum.kullanici = request.user
            yorum.urun = urun
            yorum.save()
            messages.success(request, 'Yorumunuz başarıyla eklendi.')
            return redirect('urun_ayrinti', urun_id=urun.id)
    else:
        form = YorumForm()
    return render(request, 'core/urun_ayrinti.html', {'urun': urun, 'form': form})

@staff_member_required
def admin_yorumlar(request):
    yorumlar = Yorum.objects.all().order_by('-created_at')
    return render(request, 'core/admin_yorumlar.html', {'yorumlar': yorumlar})

@staff_member_required
def admin_yorum_yanit(request, yorum_id):
    yorum = get_object_or_404(Yorum, id=yorum_id)
    if request.method == 'POST':
        form = AdminCommentForm(request.POST, instance=yorum)
        if form.is_valid():
            form.save()
            messages.success(request, 'Yanıt başarıyla eklendi.')
            return redirect('admin_yorumlar')
    else:
        form = AdminCommentForm(instance=yorum)
    return render(request, 'core/admin_yorum_yanit.html', {'yorum': yorum, 'form': form})

def bulten_abonelik(request):
    if request.method == 'POST':
        form = BultenAbonelikForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bülten aboneliğiniz başarıyla oluşturuldu.')
            return redirect('anasayfa')
    else:
        form = BultenAbonelikForm()
    return render(request, 'core/bulten_abonelik.html', {'form': form})


