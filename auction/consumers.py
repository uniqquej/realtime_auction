import json

from channels.db import database_sync_to_async
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer import model_observer
from djangochannelsrestframework.observer.generics import ObserverModelInstanceMixin, action

from .models import Chatter, Auction, User
from .serializers import ChatterSerializer, RoomSerializer, UserSerializer


class RoomConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    queryset = Auction.objects.all()
    serializer_class = RoomSerializer
    lookup_field = "pk"

    async def disconnect(self, code):
        if hasattr(self, "auction_subscribe"):
            await self.remove_user_from_auction(self.auction_subscribe)
            await self.notify_users()
        await super().disconnect(code)

    @action()
    async def join_auction(self, pk, **kwargs):
        self.auction_subscribe = pk
        await self.add_user_to_auction(pk)
        await self.notify_users()

    @action()
    async def leave_auction(self, pk, **kwargs):
        await self.remove_user_from_auction(pk)

    @action()
    async def create_chat(self, chat, **kwargs):
        auction: Auction = await self.get_auction(pk=self.auction_subscribe)
        await database_sync_to_async(Chatter.objects.create)(
            auction=auction,
            user=self.scope["user"],
            offer_price=chat
        )

    @action()
    async def subscribe_to_messages_in_room(self, pk, request_id, **kwargs):
        await self.message_activity.subscribe(auction=pk, request_id=request_id)

    @model_observer(Chatter)
    async def message_activity(
        self,
        message,
        observer=None,
        subscribing_request_ids = [],
        **kwargs
    ):
        """
        This is evaluated once for each subscribed consumer.
        The result of `@message_activity.serializer` is provided here as the message.
        """
        # since we provide the request_id when subscribing we can just loop over them here.
        for request_id in subscribing_request_ids:
            message_body = dict(request_id=request_id)
            message_body.update(message)
            await self.send_json(message_body)

    @message_activity.groups_for_signal
    def message_activity(self, instance: Chatter, **kwargs):
        yield 'auction__{instance.auction_id}'
        yield f'pk__{instance.pk}'

    @message_activity.groups_for_consumer
    def message_activity(self, auction=None, **kwargs):
        if auction is not None:
            yield f'auction__{auction}'

    @message_activity.serializer
    def message_activity(self, instance:Chatter, action, **kwargs):
        """
        This is evaluated before the update is sent
        out to all the subscribing consumers.
        """
        return dict(data=ChatterSerializer(instance).data, action=action.value, pk=instance.pk)

    async def notify_users(self):
        auction: Auction = await self.get_auction(self.auction_subscribe)
        for group in self.groups:
            await self.channel_layer.group_send(
                group,
                {
                    'type':'update_users',
                    'usuarios':await self.current_users(auction)
                }
            )

    async def update_users(self, event: dict):
        await self.send(text_data=json.dumps({'usuarios': event["usuarios"]}))

    @database_sync_to_async
    def get_auction(self, pk: int) -> Auction:
        return Auction.objects.get(pk=pk)

    @database_sync_to_async
    def current_users(self, auction: Auction):
        return [UserSerializer(user).data for user in auction.current_users.all()]

    @database_sync_to_async
    def remove_user_from_room(self, auction):
        user: User = self.scope["user"]
        user.current_auctions.remove(auction)

    @database_sync_to_async
    def add_user_to_auction(self, pk):
        user: User = self.scope["user"]
        if not user.current_auctions.filter(pk=self.auction_subscribe).exists():
            user.current_auctions.add(Auction.objects.get(pk=pk))