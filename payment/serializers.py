from rest_framework import serializers
from .models import Payments


class WinningBidListSerializer(serializers.ModelSerializer):
    buyer = serializers.CharField(source="buyer.username", read_only=True)
    product_name = serializers.CharField(
        source="product_name.product_name", read_only=True
    )
    total_price = serializers.CharField(
        source="total_price.auction_final_price", read_only=True
    )

    class Meta:
        model = Payments
        fields = "__all__"


class KakaoPayReadySerializer(serializers.Serializer):
    buyer = serializers.CharField(source="buyer.username", read_only=True)
    product_name = serializers.CharField(
        source="product_name.product_name", read_only=True
    )
    total_price = serializers.CharField(
        source="total_price.auction_final_price", read_only=True
    )
    url = serializers.URLField(source="kakao_pay_url", read_only=True)


class KakaoPayApprovalSerializer(serializers.ModelSerializer):
    buyer = serializers.CharField(source="buyer.username", read_only=True)
    product_name = serializers.CharField(
        source="product_name.product_name", read_only=True
    )
    total_price = serializers.CharField(
        source="total_price.auction_final_price", read_only=True
    )

    class Meta:
        model = Payments
        fields = "__all__"


class KakaoCancelSerializer(serializers.Serializer):
    message = serializers.CharField()


class KakaoFailSerializer(serializers.Serializer):
    message = serializers.CharField()
