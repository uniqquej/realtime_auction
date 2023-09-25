from django.db import models
from django.utils import timezone
from user.models import User
from product.models import Products


"""
auction_users : 경매 물건을 파는 사람 == 채팅방 주인
auction_chat_name : 경매 채팅방 이름(경매 제품 이름) // 제품 당 1개의 채팅방만 생성가능(1:1)
auction_chat_open_at : 경매 시작 시간
auction_chat_close_at : 경매 마감 시간(user가 경매를 종료 했을 경우 마감 시간이 설정 됨)
"""


class Auction(models.Model):
    auction_users = models.ForeignKey(User, on_delete=models.CASCADE)
    auction_chat_name = models.OneToOneField(Products, on_delete=models.CASCADE)
    auction_chat_open_at = models.DateTimeField(blank=False)
    auction_chat_close_at = models.DateTimeField(blank=True, null=True)

    def close_auction(self):
        """
        판매자가 경매를 마감한 시간을 경매 마감시간으로 설정합니다.
        """
        self.auction_chat_close_at = timezone.now()
        self.save()

    class Meta:
        ordering = ["-auction_chat_open_at"]