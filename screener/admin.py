from django.contrib import admin

from .models import Stock


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """Admin interface for managing Stock instances.

    This class customizes the display and search functionality for the Stock model
    in the Django admin site.
    """

    list_display = (
        "symbol",
        "name",
        "isin_code",
        "nifty_50",
        "nifty_next_50",
        "nifty_100",
        "nifty_200",
        "nifty_500",
    )
    search_fields = ("symbol", "name", "isin_code")
    list_filter = ("nifty_50", "nifty_next_50", "nifty_100", "nifty_200", "nifty_500")
