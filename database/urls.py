from django.urls import path
from . import views

urlpatterns = [
    path('user/', views.user_login, name='user_login'),
    path('signup/',views.signup,name='signup'),
    path('checking/',views.checking,name='checking'),
]
