# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async
from .models import Message
from .models import Room

@database_sync_to_async
def get_user(token_key):
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()

@database_sync_to_async
def create_message(author, text, room):
    return Message.objects.create(author=author, text=text, room_id=int(room))

# WEBSOCKETS - The consumer is like the view for websockets.
# It is registered in the app routing.py
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # print('CONNECTION RECEIVED')
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = 'chat_{0}'.format(self.room_id)
        # print("ROOM GROUP NAME " + self.room_group_name)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self):
        # print('CONNECTION LOST')
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def init_chat(self, data):
        user = await get_user(data['token'])
        content = {
            'command': 'INIT_CHAT'
        }
        content['success'] = 'Chatting success with username: ' + str(user)
        self.send_message(content)

    async def fetch_messages(self, data):
        messages = Message.last_50_messages(self.room_id)
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)

    async def new_message(self, data):
        # print('NEW_MESSAGE command received')

        text = data['text']
        user = await get_user(data['token'])
        # print("GOT USER: " + str(user))
        # # print("SELF SCOPE IS: " + str(self.scope))
        message = await create_message(user, text, self.room_id)
        
        content = {
            'command': 'NEW_MESSAGE',
            'message': self.message_to_json(message)
        }
        await self.send_chat_message(content)

    commands = {
        'INIT_CHAT': init_chat,
        'FETCH_MESSAGES': fetch_messages,
        'NEW_MESSAGE': new_message
    }

    async def receive(self, text_data):
        # print('IN RECEIVE WITH TEXT DATA ' + text_data)
        data = json.loads(text_data)
        await self.commands[data['command']](self, data)


    async def send_chat_message(self, message):
        # Send message to room group
        print('GROUP SENDING MESSAGE ' + str(message))
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def message_to_json(self, message):
        messageJson = {
            'id': str(message.id),
            'author': str(message.author),
            'text': message.text,
            'timestamp': str(message.timestamp)
        }
        return messageJson

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps(message))



