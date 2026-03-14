from django.urls import path

from .views import (
    BearishEngulfingPatternListView,
    BullishEngulfingPatternListView,
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
    path(
        "patterns/bullish-engulfing/",
        BullishEngulfingPatternListView.as_view(),
        name="bullish-engulfing-pattern-list",
    ),
    path(
        "patterns/bearish-engulfing/",
        BearishEngulfingPatternListView.as_view(),
        name="bearish-engulfing-pattern-list",
    ),
]
