from django.shortcuts import render
from mainapp.models import User
from .models import FileUpload,ChatModel,Room,Message,FileModel
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from mainapp.models import *
from django.db.models import Q

from mainapp.decorators import *
# Create your views here.
@profile_required
def private_chat_home(request):
    allusers=Message.objects.filter(user_id=request.user.id)
    user = User.objects.get(pk=request.user.id)
    joined_rooms=Room.objects.filter(users=user)
    try:
        seller = SellerProfileModel.objects.get(user=user)
    except:
        seller=""
    users = User.objects.exclude(email=request.user)
    return render(request, 'home_chat.html', context={
                                                      'seller':seller,
                                                      'joined_rooms':joined_rooms,
                                                      'allusers':allusers,
                                                      'users':users})

def chatPage(request, username):
    user = User.objects.get(pk=request.user.id)
    try:
        client_chat=BidAmountModel.objects.get(user=user)
    except Exception:
        client_chat=""
    try:
        seller = SellerProfileModel.objects.get(user=user)
    except Exception:
        seller=""
    user_obj = User.objects.get(first_name=username)
    users = User.objects.exclude(email=request.user.email)
    if request.method =="POST":
        img = request.FILES.getlist('files[]',None)
        fullfile=img[0]
        strfullfile=str(fullfile)
        print(strfullfile)
        ext = strfullfile.split('.')[-1]
        a=''
        if ext == 'jpeg' or ext =='png' or ext == "jpg" or ext =="img":
            a='image'
        elif ext == 'mp4':
            a='video'
        else:
            a='others'
        print()
        if request.user.id > user_obj.id:
            thread_name = f'chat_{request.user.id}-{user_obj.id}'
        else:
            thread_name = f'chat_{user_obj.id}-{request.user.id}'
        image_save=FileUpload(files_upload=img[0])
        image_save.save()
        return JsonResponse({'url':image_save.files_upload.url,'msgtype':a})


    
    if request.user.is_authenticated:

        if request.user.id > user_obj.id:
            thread_name = f'chat_{request.user.id}-{user_obj.id}'
        else:
            thread_name = f'chat_{user_obj.id}-{request.user.id}'
        message_objs = ChatModel.objects.filter(thread_name=thread_name)
        print(message_objs)

        return render(request, 'message.html', context={'user' : f"{user_obj.id}" ,'users': users, 'messages' : message_objs, 
                                                                                      'username' : user_obj, 
                                                                                      'count' : len(message_objs),
                                                                                      'seller':seller,"client_chat":client_chat,
                                                                                      })
    else:
        return render(request, 'home_chat.html')
    
    
@csrf_exempt
def Imagesend1(request):
    if request.method == "POST":
        img = request.FILES.getlist('files[]',None)
        fullfil = img[0]
        print(fullfil," #######----")
        strfile = str(fullfil)
        extention = strfile.split(".")[-1]
        a=''
        if extention == 'jpeg' or extention =='png' or extention == "jpg" or extention =="img"  or extention=="JPG":
            a='image'
        elif extention == 'mp4':
            a='video'
        else:
            a='others'
        
        image_save=FileUpload(files_upload=img[0])
        image_save.save()
        print(image_save.files_upload.url,"---9***d99")
        return JsonResponse({'url':image_save.files_upload.url,'msgtype':a})


def group_chat_seller(request,unique_code):
    users=User.objects.filter()
    user=request.user
    user= User.objects.get(pk=request.user.id)
    allusers=Message.objects.filter(user_id=request.user.id)
    # usered = User.objects.exclude(email=user)
    try:
        seller = SellerProfileModel.objects.get(user=user)
    except:
        seller=""
    users = User.objects.exclude(email=user)
    joined_rooms=Room.objects.filter(users=user,chatType='is_group')
    message=Room.objects.get(unique_code=unique_code)
    # current_user=Room.objects.exclude(users=message)
    li=[]
    for data in message.users.all():
        
        li.append(data.id)
    new_pepole=User.objects.exclude(id__in=li)
    room=Room.objects.get(unique_code=unique_code)
    messages=Message.objects.filter(room=room)
    if request.method=="POST":
        all_users=User.objects.filter(id__in=li)
        users_email=[]
        for da in all_users:
            users_email.append(da.email)
            
        users_list=request.POST.getlist("new_pepole")
        all_list=users_list+users_email
        users_list_data=User.objects.filter(email__in=all_list)
        message.users.set(users_list_data)
        message.save()
        return redirect("create_group")
    try:
        buyer = BuyerProfileModel.objects.get(user=user)
    except:
        buyer=""
    try:
        seller = SellerProfileModel.objects.get(user=user)
    except:
        seller=""
    return render(request, 'group_Chat_seller.html',{"course":room,"message":messages,'joined_rooms':joined_rooms,
                                                     'buyer':buyer,
                                                     'seller':seller,'new_pepole':new_pepole,'allusers':allusers,
                                                     })  



def group_chat_page(request):
    user=request.user
    room=Room.objects.filter(users=user,chatType='is_group')
    try:
        buyer = BuyerProfileModel.objects.get(user=user)
    except:
        buyer=""
    try:
        seller = SellerProfileModel.objects.get(user=user)
    except:
        seller=""
    return render(request, 'groups.html',{"data":room,
                                          'buyer':buyer,'seller':seller})  
def project_chat_page(request):
    user=request.user
    room=Room.objects.filter(users=user,chatType='is_chat')
    try:
        buyer = BuyerProfileModel.objects.get(user=user)
    except:
        buyer=""
    try:
        seller = SellerProfileModel.objects.get(user=user)
    except:
        seller=""
    return render(request, 'project_group.html',{"data":room,
                                          'buyer':buyer,'seller':seller})

@csrf_exempt
def Imagesend(request):
    user_obj=Message.objects.filter(user_id =  request.user.id).last()
    print(user_obj,"---rishi----")
    if request.method == "POST":
        img = request.FILES.getlist('files[]',None)
        fullfil = img[0]
        print(fullfil," #######----")
        strfile = str(fullfil)
        extention = strfile.split(".")[-1]
        a=''
        if extention == 'jpeg' or extention =='png' or extention == "jpg" or extention =="img"  or extention=="JPG":
            a='image'
        elif extention == 'mp4':
            a='video'
        else:
            a='others'
        print()
        
        image_save=FileModel(doc=img[0])
        image_save.save()
        print(image_save.doc.url,"---9***d99")
        return JsonResponse({'url':image_save.doc.url,'msgtype':a})

def create_group(request):
    users=User.objects.filter()
    user=request.user
    selfroom=Room.objects.filter(users=user)
    if request.method=="POST":
        group_name=request.POST.get("group")
        users_list=request.POST.getlist("users")
        print(users_list)
        users_list.append(user)
        group_data=Room(name=group_name,created_by=user,chatType='is_group')
        # group_data.save()
        group_data.save()
        group_data = Room.objects.get(id=group_data.id)
        users_list_data=User.objects.filter(email__in=users_list)
        
        group_data.users.set(users_list_data)
        group_data.save()
        return redirect("create_group")
    return render(request,'create_group.html',{'users':users,'room':selfroom})

def project_chat_seller(request,unique_code):
    users=User.objects.filter()
    user=request.user
    user= User.objects.get(pk=request.user.id)
    allusers=Message.objects.filter(user_id=request.user.id)
    # usered = User.objects.exclude(email=user)
    try:
        seller = SellerProfileModel.objects.get(user=user)
    except:
        seller=""
    users = User.objects.exclude(email=user)
    joined_rooms=Room.objects.filter(users=user,chatType='is_chat')
    message=Room.objects.get(unique_code=unique_code)
    # current_user=Room.objects.exclude(users=message)
    li=[]
    for data in message.users.all():
        
        li.append(data.id)
    new_pepole=User.objects.exclude(id__in=li)
    room=Room.objects.get(unique_code=unique_code)
    messages=Message.objects.filter(room=room)
    if request.method=="POST":
        all_users=User.objects.filter(id__in=li)
        users_email=[]
        for da in all_users:
            users_email.append(da.email)
            
        users_list=request.POST.getlist("new_pepole")
        all_list=users_list+users_email
        users_list_data=User.objects.filter(email__in=all_list)
        message.users.set(users_list_data)
        message.save()
        return redirect("create_group")
    try:
        buyer = BuyerProfileModel.objects.get(user=user)
    except:
        buyer=""
    try:
        seller = SellerProfileModel.objects.get(user=user)
    except:
        seller=""
    return render(request, 'group_project_gp.html',{"course":room,"message":messages,'joined_rooms':joined_rooms,
                                                     'buyer':buyer,
                                                     'seller':seller,'new_pepole':new_pepole,'allusers':allusers,
                                                     })  


