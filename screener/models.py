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

    def __str__(self):
        """Return a string representation of the stock."""
        return f"{self.symbol} - {self.name}"

    class Meta:
        """Meta options for the Stock model."""

        db_table = "stock"
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
        indexes = [
            models.Index(fields=["symbol"]),
            models.Index(fields=["isin_code"]),
            models.Index(fields=["nifty_50"]),
            models.Index(fields=["nifty_next_50"]),
            models.Index(fields=["nifty_100"]),
            models.Index(fields=["nifty_200"]),
            models.Index(fields=["nifty_500"]),
        ]


class StockPrice(BaseModel):
    """Model representing the price of a stock at a specific time.

    Attributes:
        stock (ForeignKey): A reference to the Stock model.
        price (Decimal): The price of the stock at the given time.
        timestamp (DateTime): The date and time when the price was recorded.
    """

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="prices")
    date = models.DateField()
    opening_price = models.DecimalField(max_digits=10, decimal_places=2)
    closing_price = models.DecimalField(max_digits=10, decimal_places=2)
    day_high_price = models.DecimalField(max_digits=10, decimal_places=2)
    day_low_price = models.DecimalField(max_digits=10, decimal_places=2)
    previous_closing_price = models.DecimalField(max_digits=10, decimal_places=2)
    last_trade_price = models.DecimalField(max_digits=10, decimal_places=2)
    vwap_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_traded_quantity = models.BigIntegerField()
    total_traded_value = models.DecimalField(max_digits=20, decimal_places=2)
    total_trades = models.IntegerField()
    delivery_quantity = models.BigIntegerField()
    delivery_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        """Return a string representation of the stock price."""
        return f"{self.stock.symbol} - {self.closing_price} at {self.date}"

    class Meta:
        """Meta options for the StockPrice model."""

        db_table = "stock_price"
        unique_together = ["stock", "date"]
        verbose_name = "Stock Price"
        verbose_name_plural = "Stock Prices"
        indexes = [
            models.Index(fields=["stock", "date"]),
            models.Index(fields=["date"]),
        ]


class HammerPattern(BaseModel):
    """Model representing a hammer pattern."""

    stock = models.ForeignKey(
        Stock, on_delete=models.CASCADE, related_name="hammer_patterns"
    )
    date = models.DateField()
    stock_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["stock", "date"]),
        ]


class InvertedHammerPattern(BaseModel):
    """Model representing an inverted hammer pattern."""

    stock = models.ForeignKey(
        Stock, on_delete=models.CASCADE, related_name="inverted_hammer_patterns"
    )
    date = models.DateField()
    stock_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["stock", "date"]),
        ]
