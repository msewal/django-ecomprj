from django.urls import path
from accounts import views
urlpatterns = [
    path('oturum_ac',views.oturum_ac,name="oturum_ac"),
    path('kayit_ol',views.kayit_ol,name="kayit_ol"),
    path('oturum_kapat',views.oturum_kapat,name="oturum_kapat"),

]