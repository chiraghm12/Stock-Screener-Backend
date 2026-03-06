from django.db import models

from StockScreener_Backend.base_model import BaseModel


class Stock(BaseModel):
    """Model representing a stock with its symbol and name.

    Attributes:
        symbol (str): The unique ticker symbol for the stock.
        name (str): The full name of the company or stock.
    """

    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    isin_code = models.CharField(max_length=12, unique=True, null=True, blank=True)
    chart_link = models.URLField(max_length=500, null=True, blank=True)
    nifty_50 = models.BooleanField(default=False)
    nifty_next_50 = models.BooleanField(default=False)
    nifty_100 = models.BooleanField(default=False)
    nifty_200 = models.BooleanField(default=False)
    nifty_500 = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """Override save method to ensure symbol is uppercase."""
        self.chart_link = (
            f"https://www.tradingview.com/chart/?symbol=NSE:{self.symbol.upper()}/"
        )
        super().save(*args, **kwargs)

    def __str__(self):
        """Return a string representation of the stock."""
        return f"{self.symbol} - {self.name}"

    class Meta:
        """Meta options for the Stock model."""

        db_table = "stock"
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
