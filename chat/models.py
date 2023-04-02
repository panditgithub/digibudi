from django.db import models
from django.contrib.humanize.templatetags import humanize
from mainapp.models import User
from django.template.defaultfilters import slugify
# Create your models here.
import random

def UniqueGenerator(length=10):
    source = 'abcdefghijklmnopqrstuvwxyz1234567890@#$&_-+='
    result = ''
    for _ in range(length):
        result += source[random.randint(0, length)]
    return result

class ChatModel(models.Model):
    sender = models.CharField(max_length=100, default=None,null=True,blank=True)
    message = models.TextField(null=True, blank=True)
    thread_name = models.CharField(null=True, blank=True, max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(null=True,blank=True,max_length=10)
    
    
    
    def get_date(self):
        return humanize.naturaltime(self.timestamp)

        
    
class FileUpload(models.Model):
    files_upload=models.FileField(null=True,upload_to='messagefiles',blank=True)




class Room(models.Model):
    name = models.SlugField(max_length=128)
    created_by =models.ForeignKey(User,on_delete=models.CASCADE,related_name="created",null=True)
    unique_code = models.CharField(max_length=10, default=UniqueGenerator)
    users=models.ManyToManyField(to=User)
    chatType=models.CharField(max_length=100,default='is_chat',choices=(('is_chat','is_chat'),('is_group','is_group')))
  

    def save(self, *args, **kwargs):
        self.name = slugify(self.name)
        super(Room, self).save(*args, **kwargs)

class Message(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE,null=True,blank=True)
    content = models.CharField(max_length=512)
    file_type = models.CharField(max_length=252,null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    


    def __str__(self):
        return f'{self.user.first_name}: {self.content} [{self.timestamp}]'

class FileModel(models.Model):
    doc = models.FileField(null=True,upload_to='messagefiles',blank=True)     