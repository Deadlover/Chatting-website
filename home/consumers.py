from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import *
from channels.db import database_sync_to_async
from django.contrib.auth.models import User

class MyAsyncJsonWebsocketConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        
        # print(dir(self))  # See all attributes and methods

        print("websocket connected...")
        
        print("## Channel Layer...", self.channel_layer)    # get default channel layer from a project
        print("## Channel Name...", self.channel_name)    # get channel Name

        print(self.scope['url_route']['kwargs']['groupname'])  # scope is similar to request in views
        print("Group Name ....",self.scope['url_route']['kwargs']['groupname']) # extracting groupname from url

        self.group_name = self.scope['url_route']['kwargs']['groupname']

        await self.channel_layer.group_add(self.group_name,self.channel_name)  # Creating group name group_add('<group_name>',self.channel_name)

        await self.accept()


    async def receive_json(self, content,**kwargs):
        print("message received from client...",content)
        print("Type of Message Received form Client...",type(content))  # checking type 

        channel = await database_sync_to_async(Channel.objects.get)(name=self.group_name)
        user = await database_sync_to_async(User.objects.get)(id=content['user'])

        chat = await database_sync_to_async(ChatMessage)(content=content['msg'],channel=channel,sender=user)
        await database_sync_to_async(chat.save)()

        await self.channel_layer.group_send(self.group_name,{
            'type':'chat.message',  #it is a event , need to make handler
            'message':{
            'msg': content['msg'],
            'user': content['user']
        }
        })



    async def chat_message(self,event):
        print("# Event...",event)
        print("# Actual Data...",event['message'])
        print("# Type of Actual Data...",type(event['message']))
        data = event['message']
        print(data)
        # sending msg to client
        await self.send_json(
           {'msg':data}
        )
    
    async def Creator_message(self,event):
        print("# Event...",event)
        print("# Actual Data...",event['message'])
        print("# Type of Actual Data...",type(event['message']))
        # sending msg to client
        await self.send_json(
           {'msg':{'msg':event['message']}}
        )


    async def disconnect(self, close_code):
        print("websocket disconnected...",close_code)
        print("## Channel Layer...", self.channel_layer)  
        print("## Channel Name...", self.channel_name)

        # Group Discard code
        await self.channel_layer.group_discard(self.group_name,self.channel_name)
      
    