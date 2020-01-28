from django.urls import path
from spotfind_api import views

urlpatterns = [
    path('lots/', views.LotList.as_view()),
    path('lot/<int:pk>/', views.LotDetail.as_view()),
    path('spots/', views.SpotList.as_view()),
    path('spot/<int:pk>/', views.SpotDetail.as_view()),
    path('lot/<int:pk>/spots/', views.LotSpots.as_view()),
]