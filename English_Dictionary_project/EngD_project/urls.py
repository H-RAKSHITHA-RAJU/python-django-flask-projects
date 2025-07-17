from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('word/', views.word, name='word'),
    path('history/', views.history_view, name='history'),
    path('signup/', views.signup_view, name='signup'),
    path('signin/', views.Signin_view, name='signin'),
    path('logout/', views.logout_view, name='logout'),
]
