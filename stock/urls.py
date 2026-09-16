from django.urls import path
from . import views

urlpatterns = [
    path ("search/",views.stock_search),
    path ("<str:symbol>/history/",views.stock_history ),
    path("<str:symbol>/sma/", views.stock_sma),
    path("<str:symbol>/ema/", views.stock_ema),
    path("<str:symbol>/rsi/", views.stock_rsi),
    path("<str:symbol>/macd/",views.stock_macd),
    path("<str:symbol>/bollinger/",views.stock_bollinger_bands),
    path("<str:symbol>/", views.stock_detail),
]