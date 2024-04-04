from channels.generic.websocket import AsyncJsonWebsocketConsumer,WebsocketConsumer
import json
from asgiref.sync import async_to_sync
class ChaatRoomConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name,self.channel_name)

        await self.accept()

    async def disconnect(self,close_code):
        #Leave room group
        await self.channel_layer.group_discard(self.room_group_name,self.channel_name)

    #Receive message from websocket
    async def receive(self,text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        #Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,{"type":"chat.message","message":message}
        )

    #Receive message from room group
    async def chat_message(self,event):
        message = event["message"]

        #send message to websocket
        await self.send(text_data=json.dumps({"message":message}))

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        # self.accept()
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,self.channel_name
        )


    def receive(self,text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # self.send(text_data=json.dumps({"message":message}))
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type":"chat.message",
                "message":message
            }
        )       

    def chat_message(self,event):
        message = event["message"]

        self.send(text_data=json.dumps({"message":message}))

