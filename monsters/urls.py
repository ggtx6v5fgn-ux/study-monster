from django.urls import path
from . import views

urlpatterns = [
    path('', views.MonsterListView.as_view(), name='monster_list'),
    path('monster/<int:pk>/', views.MonsterDetailView.as_view(), name='monster_detail'),
    path('create/', views.MonsterCreateView.as_view(), name='monster_create'),
    path('monster/<int:pk>/battle/', views.battle_monster, name='battle_monster'),
    path('monster/<int:pk>/update/', views.MonsterUpdateView.as_view(), name='monster_update'),
    path('monster/<int:pk>/delete/', views.MonsterDeleteView.as_view(), name='monster_delete'),
    path('register/', views.register, name='register'),
]
