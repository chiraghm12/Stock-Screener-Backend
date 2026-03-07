import logging
import time
from datetime import datetime, timedelta

import requests
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Stock, StockPrice

logger = logging.getLogger("stock_screener_logger")


class StockPriceCreateView(APIView):
    """API view to create stock price entries.

    This view handles POST requests to create new stock price records in the database.
    It expects a JSON payload containing the stock symbol and its price details.
    """

    def post(self, request):
        """Handle POST requests to create a new stock price entry."""
        try:
            BASE_URL = "https://www.nseindia.com"
            API_URL = "https://www.nseindia.com/api/historicalOR/generateSecurityWiseHistoricalData"

            HEADERS = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "*/*",
                "Referer": "https://www.nseindia.com/",
            }

            session = requests.Session()
            session.headers.update(HEADERS)

            # Generate cookies
            session.get(BASE_URL)

            today = datetime.today()
            from_date = today - timedelta(days=45)

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

                response = session.get(API_URL, params=params)

                if response.status_code != 200:
                    logger.error(
                        f"Failed to fetch data for stock {stock.symbol}: {response.status_code}"
                    )
                    continue

                data = response.json()

                if "data" not in data:
                    logger.warning(f"No data found for stock {stock.symbol}")
                    continue

                for item in data["data"]:
                    price_objects.append(
                        StockPrice(
                            stock=stock,
                            date=datetime.strptime(
                                item["mTIMESTAMP"], "%d-%b-%Y"
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
                    f"Fetched data for stock {stock.symbol}: {len(data['data'])} records"
                )
                time.sleep(0.5)  # prevent NSE blocking

            with transaction.atomic():
                StockPrice.objects.bulk_create(price_objects, batch_size=1000)

            return Response(
                {"message": "Stock price data saved successfully"},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
