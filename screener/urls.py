from django.urls import path

from .views import StockPriceCreateView

urlpatterns = [
    path("stock-prices/", StockPriceCreateView.as_view(), name="stock-price-create"),
]
