from django.urls import path
from . import views
urlpatterns = [
    path('chat/', views.private_chat_home, name='chat-index'),
    path('chat/<str:username>/', views.chatPage, name='chat-room'),
    path('group_chat/<str:unique_code>', views.group_chat_seller, name='group_chat'),
    path('project_chat/<str:unique_code>', views.project_chat_seller, name='project_chat'),
    path('group_chat_page/', views.group_chat_page, name='group_chat_page'),
    path('project_chat_page/', views.project_chat_page, name='project_chat_page'),
    path('image/send',views.Imagesend,name='imagesend'),
    path('image/send1',views.Imagesend1,name='imagesend1'),      
    path('create_group/',views.create_group,name='create_group'), 
    # path('chating/',views.buyer_chat_home,name='chat-buyer'),
]
