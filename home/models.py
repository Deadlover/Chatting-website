from django.conf import settings
from django.db import models

# Model to represent a direct message channel or a group chat channel
class Channel(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Unique name for the channel

    def __str__(self):
        return self.name

# Model for chat messages (supports both direct messages and group messages)
class ChatMessage(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.CharField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)
    channel = models.ForeignKey('Channel', related_name='messages', on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Message by {self.sender} in {self.channel}"

# Model for chat groups (only for friends, essentially a wrapper around the Channel model for group chats)
class ChatGroup(models.Model):
    channel = models.OneToOneField('Channel', on_delete=models.CASCADE, related_name='chat_group')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat Group: {self.channel.name}"


# Model to represent friend requests
class FriendRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_friend_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_friend_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = (('sender', 'receiver'),)

    def __str__(self):
        return f"Friend request from {self.sender} to {self.receiver}"

# Model to represent friendships between users
class Friendship(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user1', 'user2'], name='unique_friendship'),
            models.CheckConstraint(check=~models.Q(user1=models.F('user2')), name='users_are_different')
        ]

    def __str__(self):
        return f"{self.user1} and {self.user2} are friends"
