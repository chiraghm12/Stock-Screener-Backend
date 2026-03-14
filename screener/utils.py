import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict

import requests
from django.db import transaction

from .models import (
    BearishEngulfingPattern,
    BearishKickerPattern,
    BullishEngulfingPattern,
    BullishKickerPattern,
    DojiPattern,
    HammerPattern,
    InvertedHammerPattern,
    ProGapNegativePattern,
    ProGapPositivePattern,
    Stock,
    StockPrice,
)

logger = logging.getLogger("stock_screener_logger")


def fetch_and_store_nse_stock_price_data(days: int = 45) -> int:
    """Fetch historical stock price data from NSE and store it in the database.

    Args:
        days: Number of days of historical data to fetch (default: 45).

    Returns:
        The total number of `StockPrice` records created.
    """
    try:
        base_url = "https://www.nseindia.com"
        api_url = (
            "https://www.nseindia.com/api/"
            "historicalOR/generateSecurityWiseHistoricalData"
        )

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*",
            "Referer": "https://www.nseindia.com/",
        }

        session = requests.Session()
        session.headers.update(headers)

        # Generate cookies
        session.get(base_url)

        today = datetime.today()
        from_date = today - timedelta(days=days)

        from_date_str = from_date.strftime("%d-%m-%Y")
        to_date_str = today.strftime("%d-%m-%Y")

        stocks = Stock.objects.all()

        price_objects = []

        for stock in stocks:
            params = {
                "from": from_date_str,
                "to": to_date_str,
                "symbol": stock.symbol,
                "type": "priceVolumeDeliverable",
                "series": "EQ",
            }

            response = session.get(api_url, params=params)

            if response.status_code != 200:
                logger.error(
                    "Failed to fetch data for stock %s: %s",
                    stock.symbol,
                    response.status_code,
                )
                continue

            data = response.json()

            if "data" not in data:
                logger.warning("No data found for stock %s", stock.symbol)
                continue

            for item in data["data"]:
                price_objects.append(
                    StockPrice(
                        stock=stock,
                        date=datetime.strptime(
                            item["mTIMESTAMP"],
                            "%d-%b-%Y",
                        ).date(),
                        opening_price=item["CH_OPENING_PRICE"],
                        closing_price=item["CH_CLOSING_PRICE"],
                        day_high_price=item["CH_TRADE_HIGH_PRICE"],
                        day_low_price=item["CH_TRADE_LOW_PRICE"],
                        previous_closing_price=item["CH_PREVIOUS_CLS_PRICE"],
                        last_trade_price=item["CH_LAST_TRADED_PRICE"],
                        vwap_price=item["VWAP"],
                        total_traded_quantity=item["CH_TOT_TRADED_QTY"],
                        total_traded_value=item["CH_TOT_TRADED_VAL"],
                        total_trades=item["CH_TOTAL_TRADES"],
                        delivery_quantity=item["COP_DELIV_QTY"],
                        delivery_percentage=item["COP_DELIV_PERC"],
                    )
                )

            logger.info(
                "Fetched data for stock %s: %s records",
                stock.symbol,
                len(data["data"]),
            )
            # Small delay to reduce chance of NSE blocking
            # time.sleep(0.2)

        created_count = 0
        if price_objects:
            cutoff_date = from_date.date()
            with transaction.atomic():
                # Insert / update recent data (ignore duplicates on stock+date)
                StockPrice.objects.bulk_create(
                    price_objects,
                    batch_size=1000,
                    ignore_conflicts=True,
                )
                created_count = len(price_objects)
                logger.info(
                    "Stock price data saved successfully for %s records",
                    created_count,
                )

                # Remove data older than the requested window
                deleted_count, _ = StockPrice.objects.filter(
                    date__lt=cutoff_date,
                ).delete()
                logger.info(
                    "Old stock price data deleted: %s records before %s",
                    deleted_count,
                    cutoff_date,
                )

        return created_count
    except Exception as e:
        logger.exception(
            "Unexpected error while fetching NSE stock price data: %s",
            e,
        )
        return 0


def add_pattern_data() -> Dict[str, Any]:
    """Detect hammer and inverted hammer patterns for the latest date.

    Uses the most recent `StockPrice.date` for all stocks, classifies each
    candle as hammer / inverted hammer using a simple heuristic, stores the
    results in `HammerPattern` and `InvertedHammerPattern`, and returns a
    summary dictionary.

    Returns:
        A dict containing:
            - "date": the latest date used (or None)
            - "hammer_count": number of hammer patterns created
            - "inverted_hammer_count": number of inverted hammer patterns created
    """
    try:
        dates = (
            StockPrice.objects.values_list("date", flat=True)
            .distinct()
            .order_by("-date")[:2]
        )
        date_list = list(dates)

        if not date_list:
            logger.info("No stock price data available for pattern detection")
            return {
                "date": None,
                "hammer_count": 0,
                "inverted_hammer_count": 0,
                "bullish_engulfing_count": 0,
                "bearish_engulfing_count": 0,
                "doji_count": 0,
                "bullish_kicker_count": 0,
                "bearish_kicker_count": 0,
                "pro_gap_positive_count": 0,
                "pro_gap_negative_count": 0,
            }

        latest_date = date_list[0]
        prev_date = date_list[1] if len(date_list) > 1 else None

        prices = (
            StockPrice.objects.filter(date=latest_date)
            .select_related("stock")
            .order_by("stock__symbol")
        )

        prev_prices_dict = {}
        if prev_date:
            prev_prices = StockPrice.objects.filter(date=prev_date)
            for p in prev_prices:
                prev_prices_dict[p.stock_id] = p

        hammer_objects = []
        inverted_hammer_objects = []
        bullish_engulfing_objects = []
        bearish_engulfing_objects = []
        doji_objects = []
        bullish_kicker_objects = []
        bearish_kicker_objects = []
        pro_gap_positive_objects = []
        pro_gap_negative_objects = []

        # Clean existing patterns for that date to avoid duplicates
        HammerPattern.objects.all().delete()
        InvertedHammerPattern.objects.all().delete()
        BullishEngulfingPattern.objects.all().delete()
        BearishEngulfingPattern.objects.all().delete()
        DojiPattern.objects.all().delete()
        BullishKickerPattern.objects.all().delete()
        BearishKickerPattern.objects.all().delete()
        ProGapPositivePattern.objects.all().delete()
        ProGapNegativePattern.objects.all().delete()

        for price in prices:
            open_price = Decimal(price.opening_price)
            close_price = Decimal(price.closing_price)
            high_price = Decimal(price.day_high_price)
            low_price = Decimal(price.day_low_price)

            body = abs(close_price - open_price)
            upper = high_price - max(open_price, close_price)
            lower = min(open_price, close_price) - low_price

            # Doji: open and close are very close
            if high_price > low_price and body <= (high_price - low_price) * Decimal(
                "0.1"
            ):
                doji_objects.append(
                    DojiPattern(
                        stock=price.stock,
                        date=latest_date,
                        stock_price=price.closing_price,
                    )
                )

            # Avoid division / comparison issues when body is extremely small
            if body <= Decimal("0.01"):
                continue

            # Simple heuristics:
            # Hammer: long lower wick, small upper wick
            is_hammer = lower >= body * 2 and upper <= body

            # Inverted hammer: long upper wick, small lower wick
            is_inverted_hammer = upper >= body * 2 and lower <= body

            if is_hammer:
                hammer_objects.append(
                    HammerPattern(
                        stock=price.stock,
                        date=latest_date,
                        stock_price=price.closing_price,
                    )
                )

            if is_inverted_hammer:
                inverted_hammer_objects.append(
                    InvertedHammerPattern(
                        stock=price.stock,
                        date=latest_date,
                        stock_price=price.closing_price,
                    )
                )

            # Engulfing patterns
            prev_price = prev_prices_dict.get(price.stock_id)
            if prev_price:
                prev_open = Decimal(prev_price.opening_price)
                prev_close = Decimal(prev_price.closing_price)

                is_prev_bearish = prev_close < prev_open
                is_curr_bullish = close_price > open_price
                engulfs_bullish = open_price <= prev_close and close_price >= prev_open

                if is_prev_bearish and is_curr_bullish and engulfs_bullish:
                    bullish_engulfing_objects.append(
                        BullishEngulfingPattern(
                            stock=price.stock,
                            date=latest_date,
                            stock_price=price.closing_price,
                        )
                    )

                is_prev_bullish = prev_close > prev_open
                is_curr_bearish = close_price < open_price
                engulfs_bearish = open_price >= prev_close and close_price <= prev_open

                if is_prev_bullish and is_curr_bearish and engulfs_bearish:
                    bearish_engulfing_objects.append(
                        BearishEngulfingPattern(
                            stock=price.stock,
                            date=latest_date,
                            stock_price=price.closing_price,
                        )
                    )

                # Bullish Kicker: prev bearish, curr bullish, gaps up (open >= prev_open)
                if is_prev_bearish and is_curr_bullish and open_price >= prev_open:
                    bullish_kicker_objects.append(
                        BullishKickerPattern(
                            stock=price.stock,
                            date=latest_date,
                            stock_price=price.closing_price,
                        )
                    )

                # Bearish Kicker: prev bullish, curr bearish, gaps down (open <= prev_open)
                if is_prev_bullish and is_curr_bearish and open_price <= prev_open:
                    bearish_kicker_objects.append(
                        BearishKickerPattern(
                            stock=price.stock,
                            date=latest_date,
                            stock_price=price.closing_price,
                        )
                    )

                # Pro Gap Positive: prev bearish, curr bullish, open > prev_close
                if is_prev_bearish and is_curr_bullish and open_price > prev_close:
                    pro_gap_positive_objects.append(
                        ProGapPositivePattern(
                            stock=price.stock,
                            date=latest_date,
                            stock_price=price.closing_price,
                        )
                    )

                # Pro Gap Negative: prev bullish, curr bearish, open < prev_close
                if is_prev_bullish and is_curr_bearish and open_price < prev_close:
                    pro_gap_negative_objects.append(
                        ProGapNegativePattern(
                            stock=price.stock,
                            date=latest_date,
                            stock_price=price.closing_price,
                        )
                    )

        hammer_count = 0
        inverted_hammer_count = 0
        bullish_engulfing_count = 0
        bearish_engulfing_count = 0
        doji_count = 0
        bullish_kicker_count = 0
        bearish_kicker_count = 0
        pro_gap_positive_count = 0
        pro_gap_negative_count = 0

        if hammer_objects:
            HammerPattern.objects.bulk_create(hammer_objects, batch_size=500)
            hammer_count = len(hammer_objects)

        if inverted_hammer_objects:
            InvertedHammerPattern.objects.bulk_create(
                inverted_hammer_objects,
                batch_size=500,
            )
            inverted_hammer_count = len(inverted_hammer_objects)

        if bullish_engulfing_objects:
            BullishEngulfingPattern.objects.bulk_create(
                bullish_engulfing_objects,
                batch_size=500,
            )
            bullish_engulfing_count = len(bullish_engulfing_objects)

        if bearish_engulfing_objects:
            BearishEngulfingPattern.objects.bulk_create(
                bearish_engulfing_objects,
                batch_size=500,
            )
            bearish_engulfing_count = len(bearish_engulfing_objects)

        if doji_objects:
            DojiPattern.objects.bulk_create(
                doji_objects,
                batch_size=500,
            )
            doji_count = len(doji_objects)

        if bullish_kicker_objects:
            BullishKickerPattern.objects.bulk_create(
                bullish_kicker_objects,
                batch_size=500,
            )
            bullish_kicker_count = len(bullish_kicker_objects)

        if bearish_kicker_objects:
            BearishKickerPattern.objects.bulk_create(
                bearish_kicker_objects,
                batch_size=500,
            )
            bearish_kicker_count = len(bearish_kicker_objects)

        if pro_gap_positive_objects:
            ProGapPositivePattern.objects.bulk_create(
                pro_gap_positive_objects,
                batch_size=500,
            )
            pro_gap_positive_count = len(pro_gap_positive_objects)

        if pro_gap_negative_objects:
            ProGapNegativePattern.objects.bulk_create(
                pro_gap_negative_objects,
                batch_size=500,
            )
            pro_gap_negative_count = len(pro_gap_negative_objects)

        logger.info(
            "Pattern detection for %s completed: %s hammer, "
            "%s inverted hammer, %s bullish engulfing, %s bearish engulfing, "
            "%s doji, %s bullish kicker, %s bearish kicker, "
            "%s pro gap positive, %s pro gap negative",
            latest_date,
            hammer_count,
            inverted_hammer_count,
            bullish_engulfing_count,
            bearish_engulfing_count,
            doji_count,
            bullish_kicker_count,
            bearish_kicker_count,
            pro_gap_positive_count,
            pro_gap_negative_count,
        )

        return {
            "date": latest_date,
            "hammer_count": hammer_count,
            "inverted_hammer_count": inverted_hammer_count,
            "bullish_engulfing_count": bullish_engulfing_count,
            "bearish_engulfing_count": bearish_engulfing_count,
            "doji_count": doji_count,
            "bullish_kicker_count": bullish_kicker_count,
            "bearish_kicker_count": bearish_kicker_count,
            "pro_gap_positive_count": pro_gap_positive_count,
            "pro_gap_negative_count": pro_gap_negative_count,
        }
    except Exception as e:
        logger.exception(
            "Unexpected error while detecting candlestick patterns: %s",
            e,
        )
        return {
            "date": None,
            "hammer_count": 0,
            "inverted_hammer_count": 0,
            "bullish_engulfing_count": 0,
            "bearish_engulfing_count": 0,
            "doji_count": 0,
            "bullish_kicker_count": 0,
            "bearish_kicker_count": 0,
            "pro_gap_positive_count": 0,
            "pro_gap_negative_count": 0,
        }
