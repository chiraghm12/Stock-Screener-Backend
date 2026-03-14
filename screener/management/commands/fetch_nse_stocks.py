import time

import requests
from django.core.management.base import BaseCommand

from screener.models import Stock


class Command(BaseCommand):
    help = "Fetch NSE stock data and update index flags"

    def handle(self, *args, **kwargs):

        BASE_URL = "https://www.nseindia.com"
        INDEX_API = "https://www.nseindia.com/api/equity-stockIndices?index="

        INDICES = [
            "NIFTY 500",
            "NIFTY 200",
            "NIFTY 100",
            "NIFTY NEXT 50",
            "NIFTY 50",
        ]

        HEADERS = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*",
            "Referer": "https://www.nseindia.com/",
        }

        session = requests.Session()
        session.headers.update(HEADERS)

        # Generate NSE cookies
        session.get(BASE_URL)

        Stock.objects.update(
            nifty_50=False,
            nifty_next_50=False,
            nifty_100=False,
            nifty_200=False,
            nifty_500=False,
        )

        # Load existing stocks
        existing_stocks = {s.symbol: s for s in Stock.objects.all()}

        stocks_to_create = []
        stocks_to_update = []

        for index in INDICES:

            self.stdout.write(f"Processing index: {index}")

            response = session.get(INDEX_API + index)
            data = response.json()

            if "data" not in data:
                self.stdout.write(f"No data found for index: {index}")
                continue

            for stock_data in data["data"]:

                if stock_data.get("priority") != 0:
                    continue

                symbol = stock_data.get("symbol")
                name = stock_data.get("meta").get("companyName")
                isin = stock_data.get("meta").get("isin")
                chart_link = (
                    f"https://www.tradingview.com/chart/?symbol=NSE:{symbol.upper()}"
                )

                if symbol in existing_stocks:
                    stock = existing_stocks[symbol]

                    stock.name = name
                    stock.isin_code = isin
                    stock.chart_link = chart_link

                    if index == "NIFTY 50":
                        stock.nifty_50 = True

                    elif index == "NIFTY NEXT 50":
                        stock.nifty_next_50 = True

                    elif index == "NIFTY 100":
                        stock.nifty_100 = True

                    elif index == "NIFTY 200":
                        stock.nifty_200 = True

                    elif index == "NIFTY 500":
                        stock.nifty_500 = True

                    stocks_to_update.append(stock)
                else:
                    stock = Stock(
                        symbol=symbol,
                        name=name,
                        isin_code=isin,
                        chart_link=chart_link,
                        nifty_50=index == "NIFTY 50",
                        nifty_next_50=index == "NIFTY NEXT 50",
                        nifty_100=index == "NIFTY 100",
                        nifty_200=index == "NIFTY 200",
                        nifty_500=index == "NIFTY 500",
                    )

                    stocks_to_create.append(stock)

                    existing_stocks[symbol] = stock

            time.sleep(1)  # Prevent NSE blocking

        # Bulk create new stocks
        if stocks_to_create:
            Stock.objects.bulk_create(stocks_to_create, batch_size=500)

        # Bulk update existing stocks
        if stocks_to_update:
            Stock.objects.bulk_update(
                stocks_to_update,
                [
                    "name",
                    "isin_code",
                    "chart_link",
                    "nifty_50",
                    "nifty_next_50",
                    "nifty_100",
                    "nifty_200",
                    "nifty_500",
                ],
                batch_size=500,
            )

        self.stdout.write(self.style.SUCCESS("Stock data updated successfully"))
