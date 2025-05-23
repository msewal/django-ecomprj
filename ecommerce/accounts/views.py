from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from core.models import *
from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

def oturum_ac(request):
    if request.method == "POST":
        kullanici_adi = request.POST.get('kullanici_adi')
        sifre = request.POST.get('sifre')
        user = authenticate(username=kullanici_adi, password=sifre)
        if user:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Oturum açılamadı, lütfen tekrar deneyiniz.")
    return render(request, 'accounts/oturum.html')

def kayit_ol(request):
    if request.method == "POST":
        kullanici_adi = request.POST.get('kullanici_adi')
        email = request.POST.get('email')
        sifre = request.POST.get('sifre')
        sifre_tekrar = request.POST.get('sifre_tekrar')
        tel = request.POST.get('tel_no')

        if sifre != sifre_tekrar:
            messages.error(request, "Şifreler uyuşmuyor!")
            return redirect('kayit_ol')

        if User.objects.filter(username=kullanici_adi).exists():
            messages.error(request, "Bu kullanıcı adı başka bir hesap tarafından kullanılıyor! Lütfen yeni bir tane oluşturunuz.")
            return redirect('kayit_ol')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Bu mail adresi başka bir hesap adına kayıtlı!")
            return redirect('kayit_ol')

        user = User.objects.create_user(username=kullanici_adi, email=email, password=sifre)
        user.save()
        data = Musteri(user=user, tel_no=tel)
        data.save()
        login(request, user)
        return redirect('index')
    return render(request, 'accounts/kayit.html')

def oturum_kapat(request):
    logout(request)
    return redirect('/')
