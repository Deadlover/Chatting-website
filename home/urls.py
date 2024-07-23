from django.urls import path
from home import views 

urlpatterns = [
    path('', views.login,name='login'),
    path('home', views.Home,name='home'),
    path('list', views.friendlist,name='friendlist'),
    path('chat', views.Chat,name='chat'),
    path('send/<int:id>', views.Friendrequest,name='friendrequest'),
    path('notification/', views.friend_req_notify,name='notify'),
    path('accept/<int:id>', views.friend_req_accept,name='accept'),
    path('reject/<int:id>', views.friend_req_reject,name='reject'),
    path('chat/<str:name>',views.MessageChat,name='chatmessage'),
    path('send_by_creator/',views.send_message_by_creator,name='sendbycreator')
]