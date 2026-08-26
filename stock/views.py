from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .services import get_stock_data
from .serializers import StockSerializer


@api_view(["GET"])
def stock_detail(request, symbol):
    try:
        stock = get_stock_data(symbol)
        serializer = StockSerializer(stock)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )