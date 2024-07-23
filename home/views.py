from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.conf import settings
from .models import *
from django.contrib.auth import authenticate,login as auth_login
from django.contrib.auth.models import User
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def add_username_to_context(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        username = 'Guest'
    return {
        'username': username
    }

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        
        if user is not None:
            auth_login(request,user)
            return redirect('home')
        else:
            return  HttpResponse("Username or password is incorrect!!")
    return render(request,'home/login.html')

def Home(req):
    people = User.objects.exclude(id=req.user.id)
    friend_req = FriendRequest.objects.filter(receiver=req.user)
    friendships = Friendship.objects.filter(user1=req.user) | Friendship.objects.filter(user2=req.user)

    friend_ids = set()
    for friendship in friendships:
        friend = friendship.user2.id if friendship.user1 == req.user else friendship.user1.id
        friend_ids.add(friend)
    
    # Exclude these friends from the 'people' queryset
    people = people.exclude(id__in=friend_ids)
    


    return render(req,'home/home.html',{'people':people,'notification':friend_req})

def friendlist(request):
    user = request.user
    friendships = Friendship.objects.filter(user1=user) | Friendship.objects.filter(user2=user)
    
    # Create a set to hold the friend user instances
    friend_channels = []
    for friendship in friendships:
        friend = friendship.user2 if friendship.user1 == user else friendship.user1
        channel_name = get_chat_channel_name(user.id, friend.id)
        friend_channels.append({'friend': friend, 'channel_name': channel_name})
    print(friendships)
    return render(request,'home/friendlist.html',{'friends': friend_channels})

    
    

def get_chat_channel_name(user1_id, user2_id):
    # Sort the user IDs to ensure consistency
    sorted_ids = sorted([user1_id, user2_id])
    # Create a channel name by concatenating the sorted IDs
    channel_name = f"chat_{sorted_ids[0]}-{sorted_ids[1]}"
    return channel_name

def Chat(req,channelname):
    return render(req,'home/index.html')

# Friend request logic

def Friendrequest(request, id):
    if request.user.is_authenticated:
        receiver = User.objects.get(id=id)

        # Combine QuerySets for checking if they are already friends
        friends_already = Friendship.objects.filter(user1=receiver, user2=request.user) | Friendship.objects.filter(user1=request.user, user2=receiver)
        
        # Check if they are friends already or not
        if not friends_already.exists():
            # Ensure that a friend request doesn't already exist
            if not FriendRequest.objects.filter(sender=request.user, receiver=receiver).exists():
                FriendRequest.objects.create(sender=request.user, receiver=receiver)
                return redirect('home')
            else:
                return redirect('home')
        else:
            return redirect('home')
        
    else:
        return HttpResponse('You need to be logged in to send friend requests', status=403)

def friend_req_notify(request):
    friend_req = FriendRequest.objects.filter(receiver=request.user)
    notifications = list(friend_req.values('id', 'sender__username', 'timestamp'))
    return JsonResponse({'notification':notifications})

def friend_req_accept(request,id):
    sender = User.objects.get(id=id)
    friend_req = FriendRequest.objects.filter(sender=sender,receiver=request.user)
    friendship = Friendship.objects.create(user1=sender,user2=request.user)
    friend_req.delete()
    return redirect('home')


def friend_req_reject(request,id):
    sender = User.objects.get(id=id)
    friend_req = FriendRequest.objects.filter(sender=sender,receiver=request.user)
    friend_req.delete()
    return redirect('home')

def MessageChat(request,name):
    group = Channel.objects.filter(name=name).first()
    if group:
        chats=ChatMessage.objects.filter(channel=group).reverse()
        print(chats)
        return render(request,'home/index.html',{'groupname':name,'chats':chats})
    else:
        group = Channel(name=name)
        group.save()
    return render(request,'home/index.html',{'groupname':name})


def send_message_by_creator(request):
    channel_layer = get_channel_layer()
    # Assuming the group name for the creator channel is "creator"
    group_name = 'Creator'
    data='This is a message only for the creator channel. Thank u for joining us.'
    message = {
        'type': 'Creator_message',  # This should match the method name in your consumer
        'message': data,
    }
    channel = Channel.objects.get(name='Creator')
    user = User.objects.get(id=3)

    chat = ChatMessage(content=data,channel=channel,sender=user)
    chat.save()
    # Send message to group
    async_to_sync(channel_layer.group_send)(
        group_name,
        message
    )
    return JsonResponse({'status': 'Message sent to creator successfully'})