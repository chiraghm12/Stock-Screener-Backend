import django_filters

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
)


class HammerPatternFilter(django_filters.FilterSet):
    """FilterSet for hammer patterns with index-based filtering."""

    index = django_filters.CharFilter(method="filter_index")

    class Meta:
        model = HammerPattern
        fields = ["date", "index"]

    def filter_index(self, queryset, name, value):
        value = (value or "").lower()
        if value == "nifty_50":
            return queryset.filter(stock__nifty_50=True)
        if value == "nifty_next_50":
            return queryset.filter(stock__nifty_next_50=True)
        if value == "nifty_100":
            return queryset.filter(stock__nifty_100=True)
        if value == "nifty_200":
            return queryset.filter(stock__nifty_200=True)
        if value == "nifty_500":
            return queryset.filter(stock__nifty_500=True)
        return queryset


class InvertedHammerPatternFilter(django_filters.FilterSet):
    """FilterSet for inverted hammer patterns with index-based filtering."""

    index = django_filters.CharFilter(method="filter_index")

    class Meta:
        model = InvertedHammerPattern
        fields = ["date", "index"]

    def filter_index(self, queryset, name, value):
        value = (value or "").lower()
        if value == "nifty_50":
            return queryset.filter(stock__nifty_50=True)
        if value == "nifty_next_50":
            return queryset.filter(stock__nifty_next_50=True)
        if value == "nifty_100":
            return queryset.filter(stock__nifty_100=True)
        if value == "nifty_200":
            return queryset.filter(stock__nifty_200=True)
        if value == "nifty_500":
            return queryset.filter(stock__nifty_500=True)
        return queryset


class BullishEngulfingPatternFilter(django_filters.FilterSet):
    """FilterSet for bullish engulfing patterns with index-based filtering."""

    index = django_filters.CharFilter(method="filter_index")

    class Meta:
        model = BullishEngulfingPattern
        fields = ["date", "index"]

    def filter_index(self, queryset, name, value):
        value = (value or "").lower()
        if value == "nifty_50":
            return queryset.filter(stock__nifty_50=True)
        if value == "nifty_next_50":
            return queryset.filter(stock__nifty_next_50=True)
        if value == "nifty_100":
            return queryset.filter(stock__nifty_100=True)
        if value == "nifty_200":
            return queryset.filter(stock__nifty_200=True)
        if value == "nifty_500":
            return queryset.filter(stock__nifty_500=True)
        return queryset


class BearishEngulfingPatternFilter(django_filters.FilterSet):
    """FilterSet for bearish engulfing patterns with index-based filtering."""

    index = django_filters.CharFilter(method="filter_index")

    class Meta:
        model = BearishEngulfingPattern
        fields = ["date", "index"]

    def filter_index(self, queryset, name, value):
        value = (value or "").lower()
        if value == "nifty_50":
            return queryset.filter(stock__nifty_50=True)
        if value == "nifty_next_50":
            return queryset.filter(stock__nifty_next_50=True)
        if value == "nifty_100":
            return queryset.filter(stock__nifty_100=True)
        if value == "nifty_200":
            return queryset.filter(stock__nifty_200=True)
        if value == "nifty_500":
            return queryset.filter(stock__nifty_500=True)
        return queryset


class DojiPatternFilter(django_filters.FilterSet):
    """FilterSet for doji patterns with index-based filtering."""

    index = django_filters.CharFilter(method="filter_index")

    class Meta:
        model = DojiPattern
        fields = ["date", "index"]

    def filter_index(self, queryset, name, value):
        value = (value or "").lower()
        if value == "nifty_50":
            return queryset.filter(stock__nifty_50=True)
        if value == "nifty_next_50":
            return queryset.filter(stock__nifty_next_50=True)
        if value == "nifty_100":
            return queryset.filter(stock__nifty_100=True)
        if value == "nifty_200":
            return queryset.filter(stock__nifty_200=True)
        if value == "nifty_500":
            return queryset.filter(stock__nifty_500=True)
        return queryset


class BullishKickerPatternFilter(django_filters.FilterSet):
    """FilterSet for bullish kicker patterns with index-based filtering."""

    index = django_filters.CharFilter(method="filter_index")

    class Meta:
        model = BullishKickerPattern
        fields = ["date", "index"]

    def filter_index(self, queryset, name, value):
        value = (value or "").lower()
        if value == "nifty_50":
            return queryset.filter(stock__nifty_50=True)
        if value == "nifty_next_50":
            return queryset.filter(stock__nifty_next_50=True)
        if value == "nifty_100":
            return queryset.filter(stock__nifty_100=True)
        if value == "nifty_200":
            return queryset.filter(stock__nifty_200=True)
        if value == "nifty_500":
            return queryset.filter(stock__nifty_500=True)
        return queryset


class BearishKickerPatternFilter(django_filters.FilterSet):
    """FilterSet for bearish kicker patterns with index-based filtering."""

    index = django_filters.CharFilter(method="filter_index")

    class Meta:
        model = BearishKickerPattern
        fields = ["date", "index"]

    def filter_index(self, queryset, name, value):
        value = (value or "").lower()
        if value == "nifty_50":
            return queryset.filter(stock__nifty_50=True)
        if value == "nifty_next_50":
            return queryset.filter(stock__nifty_next_50=True)
        if value == "nifty_100":
            return queryset.filter(stock__nifty_100=True)
        if value == "nifty_200":
            return queryset.filter(stock__nifty_200=True)
        if value == "nifty_500":
            return queryset.filter(stock__nifty_500=True)
        return queryset


class ProGapPositivePatternFilter(django_filters.FilterSet):
    """FilterSet for pro gap positive patterns with index-based filtering."""

    index = django_filters.CharFilter(method="filter_index")

    class Meta:
        model = ProGapPositivePattern
        fields = ["date", "index"]

    def filter_index(self, queryset, name, value):
        value = (value or "").lower()
        if value == "nifty_50":
            return queryset.filter(stock__nifty_50=True)
        if value == "nifty_next_50":
            return queryset.filter(stock__nifty_next_50=True)
        if value == "nifty_100":
            return queryset.filter(stock__nifty_100=True)
        if value == "nifty_200":
            return queryset.filter(stock__nifty_200=True)
        if value == "nifty_500":
            return queryset.filter(stock__nifty_500=True)
        return queryset


class ProGapNegativePatternFilter(django_filters.FilterSet):
    """FilterSet for pro gap negative patterns with index-based filtering."""

    index = django_filters.CharFilter(method="filter_index")

    class Meta:
        model = ProGapNegativePattern
        fields = ["date", "index"]

    def filter_index(self, queryset, name, value):
        value = (value or "").lower()
        if value == "nifty_50":
            return queryset.filter(stock__nifty_50=True)
        if value == "nifty_next_50":
            return queryset.filter(stock__nifty_next_50=True)
        if value == "nifty_100":
            return queryset.filter(stock__nifty_100=True)
        if value == "nifty_200":
            return queryset.filter(stock__nifty_200=True)
        if value == "nifty_500":
            return queryset.filter(stock__nifty_500=True)
        return queryset
