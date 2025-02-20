import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'comments_room'
        self.room_group_name = 'comments_group'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()
    async def disconnect(self,close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        await self.send(text_data=json.dumps({"reply": f"You said: {message}"}))
        
    async def send_comment(self, event):
        """Send message to WebSocket clients"""
        await self.send(text_data=json.dumps({
            "user": event["user"],
            "text": event["text"]
        }))