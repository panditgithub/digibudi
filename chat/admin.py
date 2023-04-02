from django.contrib import admin

from .models import ChatModel,Message,Room,FileModel,FileUpload
# Register your models here.
@admin.register(ChatModel)
class ChatModelAdmin(admin.ModelAdmin):
    list_display=['sender']

@admin.register(Message)
class MessageModelAdmin(admin.ModelAdmin):
    list_display=['user']

@admin.register(Room)
class RoomModelAdmin(admin.ModelAdmin):
    list_display=['name']
admin.site.register(FileUpload)
admin.site.register(FileModel)