from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/pubparameter", views.apiPubParameter, name="parameter"),
    path("api/createPrivateKey", views.createPrivateKey),
    path("api/encode", views.encode),
    path("api/decode", views.decode),
    path("api/PPS", views.PPS),
    path('api/sign_key', views.sign_key),
    path('api/check_sign', views.check_sign), 
    path('api/abc', views.abc), 
]