from django.urls import path

from .views import (
    HammerPatternListView,
    InvertedHammerPatternListView,
    StockPriceCreateView,
)

urlpatterns = [
    path(
        "create-stock-prices/",
        StockPriceCreateView.as_view(),
        name="stock-price-create",
    ),
    path(
        "patterns/hammer/",
        HammerPatternListView.as_view(),
        name="hammer-pattern-list",
    ),
    path(
        "patterns/inverted-hammer/",
        InvertedHammerPatternListView.as_view(),
        name="inverted-hammer-pattern-list",
    ),
]
