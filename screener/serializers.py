from rest_framework import serializers

from .models import HammerPattern, InvertedHammerPattern, Stock, StockPrice


class StockSerializer(serializers.ModelSerializer):
    """Serializer for full stock details."""

    class Meta:
        model = Stock
        fields = [
            "id",
            "symbol",
            "name",
            "isin_code",
            "chart_link",
            "nifty_50",
            "nifty_next_50",
            "nifty_100",
            "nifty_200",
            "nifty_500",
        ]


class StockPriceSerializer(serializers.ModelSerializer):
    """Serializer for full stock price details."""

    percentage_change = serializers.SerializerMethodField()
    amount_change = serializers.SerializerMethodField()

    class Meta:
        model = StockPrice
        fields = [
            "id",
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
            "percentage_change",
            "amount_change",
        ]

    def get_percentage_change(self, obj):
        """Return percentage change from previous close to current close."""
        prev = obj.previous_closing_price
        close = obj.closing_price
        if prev in (None, 0) or prev == 0:
            return None
        try:
            return ((close - prev) / prev) * 100
        except Exception:
            return None

    def get_amount_change(self, obj):
        """Return absolute amount change from previous close to current close."""
        prev = obj.previous_closing_price
        close = obj.closing_price
        if prev is None or close is None:
            return None
        try:
            return close - prev
        except Exception:
            return None


class HammerPatternSerializer(serializers.ModelSerializer):
    """Serializer for hammer pattern data."""

    stock = StockSerializer(read_only=True)
    stock_price_details = serializers.SerializerMethodField()

    class Meta:
        model = HammerPattern
        fields = [
            "id",
            "stock",
            "date",
            "stock_price",
            "stock_price_details",
        ]

    def get_stock_price_details(self, obj):
        price = StockPrice.objects.filter(stock=obj.stock, date=obj.date).first()
        if not price:
            return None
        return StockPriceSerializer(price).data


class InvertedHammerPatternSerializer(serializers.ModelSerializer):
    """Serializer for inverted hammer pattern data."""

    stock = StockSerializer(read_only=True)
    stock_price_details = serializers.SerializerMethodField()

    class Meta:
        model = InvertedHammerPattern
        fields = [
            "id",
            "stock",
            "date",
            "stock_price",
            "stock_price_details",
        ]

    def get_stock_price_details(self, obj):
        price = StockPrice.objects.filter(stock=obj.stock, date=obj.date).first()
        if not price:
            return None
        return StockPriceSerializer(price).data
