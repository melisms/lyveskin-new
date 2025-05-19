from django.urls import path
from . import views

app_name = 'item'

urlpatterns = [
    path('browse/', views.browse, name='browse'),
    path('new/', views.create_item, name='new'),
    path('<int:pk>/', views.detail, name='detail'),
    path('items/<int:item_id>/edit/', views.edit_item, name='edit_item'),
    path('compare/', views.compare_items, name='compare_items'),
    path('comparison/', views.comparison_page, name='comparison_page'),
    path('compare/<int:category_id>/', views.compare_items, name='compare_items'),

]