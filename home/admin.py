from django.contrib import admin
from .models import *

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display=['id','name']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display=['id','sender','content','timestamp']
    
@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display=['id','channel','created_at']

@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display=['id','sender','receiver','is_accepted','timestamp']

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display=['id','user1','user2','created_at']