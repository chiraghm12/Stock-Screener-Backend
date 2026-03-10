import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .utils import add_pattern_data, fetch_and_store_nse_stock_price_data

logger = logging.getLogger("stock_screener_logger")


class StockPriceCreateView(APIView):
    """API view to create stock price entries.

    This view handles POST requests to create new stock price records in the database.
    It expects a JSON payload containing the stock symbol and its price details.
    """

    def post(self, request):
        """Handle POST requests to create a new stock price entry."""
        try:
            created_count = fetch_and_store_nse_stock_price_data()
            logger.info(
                "Stock price data workflow completed, %s records created",
                created_count,
            )
            pattern_summary = add_pattern_data()

            return Response(
                {
                    "message": "Stock price data saved successfully",
                    "records_created": created_count,
                    "pattern_summary": pattern_summary,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
