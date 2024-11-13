from django.urls import path
from accounts.views import login_view 

urlpatterns = [
    path('login-app/', login_view, name = 'login-app'),
]