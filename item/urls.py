from django.urls import path
from . import views

app_name = 'item'

urlpatterns = [
    path('browse/', views.browse, name='browse'),
    path('new/', views.create_item, name='new'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/favorite/', views.add_to_favorites, name='add_to_favorites'),
    path('<int:pk>/remove_favorite/', views.remove_from_favorites, name='remove_from_favorites'),
    path('items/<int:item_id>/edit/', views.edit_item, name='edit_item'),
    path('compare/', views.compare_items, name='compare_items'),
    path('comparison/<int:item_id1>/<int:item_id2>/', views.comparison_page, name='comparison_page'),
    path('compare/<int:category_id>/', views.compare_items, name='compare_items'),
    path('<int:pk>/delete/', views.remove_item, name='remove_item'),
]