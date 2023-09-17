from rest_framework import serializers

from auction.models import Auction, Chatter
from user.models import User
from user.serializers import UserSerializer

class ChatterSerializer(serializers.ModelSerializer):
    created_at_formatted = serializers.SerializerMethodField()
    user = UserSerializer()
    
    class Meta:
        model = Chatter
        exclude = []
        depth = 1
    
    def get_created_at_formatted(self, obj:Chatter):
        return obj.created_at.strftime("%d-%m-%Y %H:%M:%S")

class RoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    chat = ChatterSerializer(many=True, read_only=True)

    class Meta:
        model = Auction
        fields = '__all__'
        depth = 1
        read_only_fields = ["chat", "last_message"]
    
    def get_last_message(self, obj:Auction):
        return ChatterSerializer(obj.chat.order_by('created_at').last()).data