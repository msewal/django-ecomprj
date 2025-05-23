from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    Urun, Yorum, IletisimMesaji, BultenAboneligi,
    Siparis, SiparisEdilenler, Odeme_Adresi, Kategori
)
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget



class UrunForm(forms.ModelForm):
    class Meta:
        model = Urun
        fields = ['kategori', 'isim', 'aciklama', 'fiyat', 'stok', 'resim']
        widgets = {
            'aciklama': forms.Textarea(attrs={'rows': 4}),
            'fiyat': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def clean_fiyat(self):
        fiyat = self.cleaned_data.get('fiyat')
        if fiyat <= 0:
            raise forms.ValidationError('Fiyat 0\'dan büyük olmalıdır.')
        return fiyat

    def clean_stok(self):
        stok = self.cleaned_data.get('stok')
        if stok < 0:
            raise forms.ValidationError('Stok miktarı negatif olamaz.')
        return stok


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Odeme_Adresi
        fields = ['Mahalle', 'Sokak_Adresi', 'Bina_No', 'Daire_No', 'Il', 'Ilce', 'Ülke', 'Posta_Kodu']
        widgets = {
            'Mahalle': forms.TextInput(attrs={'class': 'form-control'}),
            'Sokak_Adresi': forms.TextInput(attrs={'class': 'form-control'}),
            'Bina_No': forms.TextInput(attrs={'class': 'form-control'}),
            'Daire_No': forms.TextInput(attrs={'class': 'form-control'}),
            'Il': forms.TextInput(attrs={'class': 'form-control'}),
            'Ilce': forms.TextInput(attrs={'class': 'form-control'}),
            'Ülke': CountrySelectWidget(attrs={'class': 'form-control'}),
            'Posta_Kodu': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_Posta_Kodu(self):
        posta_kodu = self.cleaned_data.get('Posta_Kodu')
        if not posta_kodu.isdigit():
            raise forms.ValidationError('Posta kodu sadece rakamlardan oluşmalıdır.')
        return posta_kodu


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment', 'rating']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rating': forms.Select(attrs={'class': 'form-control'}),
        }


class CommentReplyForm(forms.ModelForm):
    class Meta:
        model = YorumYanit
        fields = ['yanit']
        widgets = {
            'yanit': forms.Textarea(attrs={'rows': 4}),
        }

class UrunUpdateForm(forms.ModelForm):
    class Meta:
        model = Urun
        fields = ['kategori', 'isim', 'aciklama', 'fiyat', 'stok', 'resim', 'aktif']
        widgets = {
            'aciklama': forms.Textarea(attrs={'rows': 4}),
        }

class AdminCommentForm(forms.ModelForm):
    class Meta:
        model = Yorum
        fields = ['admin_reply']
        widgets = {
            'admin_reply': forms.Textarea(attrs={'rows': 4}),
        }

class UrunAramaFormu(forms.Form):
    query = forms.CharField(label='Arama', required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ürün Ara'}))
    kategori = forms.ModelChoiceField(
        queryset=Kategori.objects.all(),
        label='Kategori',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class YorumForm(forms.ModelForm):
    class Meta:
        model = Yorum
        fields = ['yorum', 'puan']
        widgets = {
            'yorum': forms.Textarea(attrs={'rows': 4}),
        }

class IletisimMesajiForm(forms.ModelForm):
    class Meta:
        model = IletisimMesaji
        fields = ['ad', 'email', 'konu', 'mesaj']
        widgets = {
            'mesaj': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('E-posta adresi gereklidir.')
        return email

class BultenAbonelikForm(forms.ModelForm):
    class Meta:
        model = BultenAboneligi
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if BultenAboneligi.objects.filter(email=email, aktif=True).exists():
            raise forms.ValidationError('Bu e-posta adresi zaten kayıtlı.')
        return email

class SiparisForm(forms.ModelForm):
    class Meta:
        model = Siparis
        fields = ['ad', 'soyad', 'email', 'telefon', 'adres', 'sehir', 'ulke', 'posta_kodu']
        widgets = {
            'adres': forms.Textarea(attrs={'rows': 3}),
        }

class OdemeAdresiForm(forms.ModelForm):
    class Meta:
        model = Odeme_Adresi
        fields = ['Mahalle', 'Sokak_Adresi', 'Bina_No', 'Daire_No', 'Il', 'Ilce', 'Ülke', 'Posta_Kodu']
        widgets = {
            'Sokak_Adresi': forms.Textarea(attrs={'rows': 2}),
            'Ülke': CountrySelectWidget(attrs={'class': 'form-control'}),
        }

class AramaForm(forms.Form):
    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ürün ara...',
            'class': 'form-control'
        })
    )
    kategori = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Tüm Kategoriler"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kategori'].queryset = Kategori.objects.all()