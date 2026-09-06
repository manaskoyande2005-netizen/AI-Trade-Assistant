from django.urls import path
from . import views

urlpatterns = [
    path ("search/",views.stock_search),
    path("<str:symbol>/", views.stock_detail),
]