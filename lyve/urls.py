from django.contrib import admin
from django.urls import path
from django.urls import path, include
from . import views
from .views import test_mail




urlpatterns = [
    path('about/', views.about, name='about'),
    path('', views.home, name='home'),  # Home view at root path
    path('products/', views.products, name='products'),
    path('ingredient/', views.ingredients, name='ingredient'),
    path('labeling/', views.labeling, name='labeling'),
    path('items/', include('item.urls')),
    path('skintype/',views.skintype, name='skintype'),
    path('skincareroutine',views.skincareroutine, name='skincareroutine'),
    path('ingredient/<str:letter>/', views.ingredients_view, name='ingredients'),
    path('ask/', views.ask_ollama, name='ask_ollama'),
    path('test-mail/', test_mail, name='test_mail'),
]


