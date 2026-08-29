from rest_framework import serializers
from .models import Stock


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = [
            "symbol",
            "company_name",
            "price",
            "currency",
            "volume",
            "market_cap",
            "updated_at",
        ]