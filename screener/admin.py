from django.contrib import admin

from .models import HammerPattern, InvertedHammerPattern, Stock, StockPrice


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """Admin interface for managing Stock instances.

    This class customizes the display and search functionality for the Stock model
    in the Django admin site.
    """

    list_display = (
        "id",
        "symbol",
        "name",
        "isin_code",
        "nifty_50",
        "nifty_next_50",
        "nifty_100",
        "nifty_200",
        "nifty_500",
        "chart_link",
    )
    search_fields = ("symbol", "name", "isin_code")
    list_filter = ("nifty_50", "nifty_next_50", "nifty_100", "nifty_200", "nifty_500")


@admin.register(StockPrice)
class StockPriceAdmin(admin.ModelAdmin):
    """Admin interface for managing StockPrice instances.

    This class customizes the display and search functionality for the StockPrice model
    in the Django admin site.
    """

    list_display = (
        "id",
        "stock",
        "date",
        "opening_price",
        "closing_price",
        "day_high_price",
        "day_low_price",
        "previous_closing_price",
        "last_trade_price",
        "vwap_price",
        "total_traded_quantity",
        "total_traded_value",
        "total_trades",
        "delivery_quantity",
        "delivery_percentage",
    )
    search_fields = ("stock__symbol", "stock__name")
    list_filter = ("date",)


@admin.register(HammerPattern)
class HammerPatternAdmin(admin.ModelAdmin):
    """Admin interface for managing HammerPattern instances."""

    list_display = ("id", "stock", "date", "stock_price")
    search_fields = ("stock__symbol", "stock__name")
    list_filter = ("date",)


@admin.register(InvertedHammerPattern)
class InvertedHammerPatternAdmin(admin.ModelAdmin):
    """Admin interface for managing InvertedHammerPattern instances."""

    list_display = ("id", "stock", "date", "stock_price")
    search_fields = ("stock__symbol", "stock__name")
    list_filter = ("date",)
