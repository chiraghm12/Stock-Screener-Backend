import logging

from django.db.models import Avg, Max, OuterRef, Subquery
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import (
    BearishEngulfingPatternFilter,
    BearishKickerPatternFilter,
    BullishEngulfingPatternFilter,
    BullishKickerPatternFilter,
    DojiPatternFilter,
    HammerPatternFilter,
    InvertedHammerPatternFilter,
    ProGapNegativePatternFilter,
    ProGapPositivePatternFilter,
)
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
from .serializers import (
    BearishEngulfingPatternSerializer,
    BearishKickerPatternSerializer,
    BullishEngulfingPatternSerializer,
    BullishKickerPatternSerializer,
    DojiPatternSerializer,
    HammerPatternSerializer,
    InvertedHammerPatternSerializer,
    ProGapNegativePatternSerializer,
    ProGapPositivePatternSerializer,
)
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


class HammerPatternListView(generics.ListAPIView):
    """List API view for hammer patterns with optional index/date filtering."""

    queryset = HammerPattern.objects.all().select_related("stock")
    serializer_class = HammerPatternSerializer
    filterset_class = HammerPatternFilter


class InvertedHammerPatternListView(generics.ListAPIView):
    """List API view for inverted hammer patterns with optional index/date filtering."""

    queryset = InvertedHammerPattern.objects.all().select_related("stock")
    serializer_class = InvertedHammerPatternSerializer
    filterset_class = InvertedHammerPatternFilter


class BullishEngulfingPatternListView(generics.ListAPIView):
    """List API view for bullish engulfing patterns with optional index/date filtering."""

    queryset = BullishEngulfingPattern.objects.all().select_related("stock")
    serializer_class = BullishEngulfingPatternSerializer
    filterset_class = BullishEngulfingPatternFilter


class BearishEngulfingPatternListView(generics.ListAPIView):
    """List API view for bearish engulfing patterns with optional index/date filtering."""

    queryset = BearishEngulfingPattern.objects.all().select_related("stock")
    serializer_class = BearishEngulfingPatternSerializer
    filterset_class = BearishEngulfingPatternFilter


class DojiPatternListView(generics.ListAPIView):
    """List API view for doji patterns with optional index/date filtering."""

    queryset = DojiPattern.objects.all().select_related("stock")
    serializer_class = DojiPatternSerializer
    filterset_class = DojiPatternFilter


class BullishKickerPatternListView(generics.ListAPIView):
    """List API view for bullish kicker patterns with optional index/date filtering."""

    queryset = BullishKickerPattern.objects.all().select_related("stock")
    serializer_class = BullishKickerPatternSerializer
    filterset_class = BullishKickerPatternFilter


class BearishKickerPatternListView(generics.ListAPIView):
    """List API view for bearish kicker patterns with optional index/date filtering."""

    queryset = BearishKickerPattern.objects.all().select_related("stock")
    serializer_class = BearishKickerPatternSerializer
    filterset_class = BearishKickerPatternFilter


class ProGapPositivePatternListView(generics.ListAPIView):
    """List API view for pro gap positive patterns with optional index/date filtering."""

    queryset = ProGapPositivePattern.objects.all().select_related("stock")
    serializer_class = ProGapPositivePatternSerializer
    filterset_class = ProGapPositivePatternFilter


class ProGapNegativePatternListView(generics.ListAPIView):
    """List API view for pro gap negative patterns with optional index/date filtering."""

    queryset = ProGapNegativePattern.objects.all().select_related("stock")
    serializer_class = ProGapNegativePatternSerializer
    filterset_class = ProGapNegativePatternFilter


class DeliveryDataView(APIView):
    """API view to get latest delivery percentage vs average."""

    def get(self, request):
        index = request.query_params.get("index", "").lower()
        only_greater = request.query_params.get("only_greater", "").lower() == "true"

        latest_date_dict = StockPrice.objects.aggregate(latest_date=Max("date"))
        latest_date = latest_date_dict.get("latest_date")

        if not latest_date:
            return Response([], status=status.HTTP_200_OK)

        latest_delivery_subquery = StockPrice.objects.filter(
            stock=OuterRef("pk"), date=latest_date
        ).values("delivery_percentage")[:1]

        stocks = Stock.objects.annotate(
            latest_delivery_percentage=Subquery(latest_delivery_subquery),
            average_delivery_percentage=Avg("prices__delivery_percentage"),
        ).filter(latest_delivery_percentage__isnull=False)

        if index == "nifty_50":
            stocks = stocks.filter(nifty_50=True)
        elif index == "nifty_next_50":
            stocks = stocks.filter(nifty_next_50=True)
        elif index == "nifty_100":
            stocks = stocks.filter(nifty_100=True)
        elif index == "nifty_200":
            stocks = stocks.filter(nifty_200=True)
        elif index == "nifty_500":
            stocks = stocks.filter(nifty_500=True)

        data = []
        for stock in stocks:
            avg_dp = stock.average_delivery_percentage
            latest_dp = stock.latest_delivery_percentage
            is_greater = False

            if avg_dp is not None and latest_dp is not None:
                is_greater = float(latest_dp) > float(avg_dp)

            if only_greater and not is_greater:
                continue

            data.append(
                {
                    "stock_id": stock.id,
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "latest_delivery_percentage": (
                        float(latest_dp) if latest_dp is not None else None
                    ),
                    "average_delivery_percentage": (
                        round(float(avg_dp), 2) if avg_dp is not None else None
                    ),
                    "is_greater_than_avg": is_greater,
                    "nifty_50": stock.nifty_50,
                    "nifty_next_50": stock.nifty_next_50,
                    "nifty_100": stock.nifty_100,
                    "nifty_200": stock.nifty_200,
                    "nifty_500": stock.nifty_500,
                }
            )

        return Response(data, status=status.HTTP_200_OK)
