from django.shortcuts import render, redirect,HttpResponse,HttpResponseRedirect
from .models import *
from .forms import PostJobForm, SellerForm, UserCreationForm, BuyerForm, PostJobForm, ApplyJobForm
import random
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,authenticate, logout
from django.views.generic.edit import DeleteView
from rest_framework.permissions import IsAuthenticated
from django.contrib import messages
import razorpay
from django.db.models import Q
from django.conf import settings
from django.http import JsonResponse
from .filters import JobFilter,alljobfilter
from django.contrib.auth import  update_session_auth_hash
from django.db.models import F
from webpush import send_user_notification
from django.contrib.auth.decorators import user_passes_test
from .decorators import *
from notifications.signals import notify
import json
from notifications.utils import slug2id
from django.shortcuts import get_object_or_404
from swapper import load_model
from django.template import Library
from .ipaddress import get_client_ip
from .task import *
from mainapp.models import User
from mainapp.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from django.contrib.auth.decorators import user_passes_test  
from django.utils import timezone
from django.core.paginator import Paginator ,EmptyPage, PageNotAnInteger
from chat.models import *
import datetime
from django.urls import reverse
register = Library()
Notification = load_model('notifications', 'Notification')

# Create your views here.

"""-----------User Registration view-----------"""

def user_register(request):

    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
    
        password = request.POST['password_original']
        type = request.POST['radio']
        password_confirm = request.POST['password_confirm']
        if password == password_confirm:
            if User.objects.filter(username1 = username).exists() or User.objects.filter(email = email).exists():
     
                error_message=''
                email_error=('','Email is taken.')[User.objects.filter(email = email).exists():]
                username_error=('','Username is taken.')[User.objects.filter(username1 = username).exists():]
                error_message = email_error + username_error
                messages.success(request, error_message)
                return redirect('register')
     
            else:
                if type == 'buyer':
                    user = User.objects.create_user(email = email,username1 =username, password = password)
                    user.is_buyer = True
                    user.save()
                    otp = random.randint(100000, 999999)
                    otpmodel = OTPModel(user=user, otp=otp)
                    otpmodel.save()
                    send_otp_with_celery.delay(email,otp)
                    subject = "OTP Verification From Digibuddies"
                    message = f"Your OTP for Account Verification in Digibuddies is {otp}"
                    send_mail(subject, message, 'tu716599@gmail.com', [email], fail_silently=False)
                    return redirect('verify')
                elif type == 'seller':
                    user = User.objects.create_user(email = email, username1 =username, password = password)
                    user.is_seller = True
                    user.save()
                    otp = random.randint(100000, 999999)
                    otpmodel = OTPModel(user=user, otp=otp)
                    otpmodel.save()
                    send_otp_with_celery.delay(email,otp)
                    subject = "OTP Verification From Digibuddies"
                    message = f"Your OTP for Account Verification in Digibuddies is {otp}"
                    
     
                    send_mail(subject, message, 'tu716599@gmail.com', [email], fail_silently=False)
                    return redirect('verify')
                
                else:
                    pass
                return redirect('register')
        else:
            messages.info(request, 'password is not a match')
            return redirect ('register')
                
                
        
    else:
        # messages.info(request, 'password is not a match')
        return render(request, 'mainapp/signup.html')


@profile_required
def client_home(request):
    user = User.objects.get(pk=request.user.id)
            
    profile_type = 'seller'
    seller = SellerProfileModel.objects.get(user=user.id)
    today=datetime.datetime.now().date()
    
    try:
        posted_jobs = PostjobModel.objects.filter(Q(seller=seller) & Q(deadline__gte = today))
        try:
            completed_jobs=PostjobModel.objects.filter(seller=seller,is_completed=True)
        except:
            completed_jobs=""

    except:
        posted_jobs = None
    page_num = request.GET.get('page1', 1)
    paginator = Paginator(posted_jobs,3)
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.page_num)
    
    try:
        in_progress=BidAmountModel.objects.filter(job__in=posted_jobs,is_accepted=True,job__is_completed=False)
        print(in_progress)
    except:
        in_progress={}
    unassigned={}
    try:
        is_bidded=BidAmountModel.objects.filter(job__in=posted_jobs,is_accepted=True).values('job_id')
        print(is_bidded)
        unassigned=PostjobModel.objects.exclude(id__in=is_bidded).filter(seller=seller)
        print(unassigned)


    except:
        unassigned={}
    
    try: 
        rejected=BidAmountModel.objects.filter(job__in=posted_jobs,is_rejected=True)
    except:
        rejected={}

    return render(request, 'mainapp/client_home.html', {
        'completed_jobs':completed_jobs,
        'in_progress':in_progress,
        'profile_type': profile_type,
        'seller':seller,
        'posted_jobs':posted_jobs,
        'unassigned':unassigned,
        'rejected':rejected,
        'page_obj':page_obj
        }
    )

"""-----------index or home page view-----------"""
def index(request):

    ip=get_client_ip(request)
    print(ip)
    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)
         
        # dashboard for seller or client
        if user.is_seller:
            return redirect("client_home")
            
            # profile_type = 'seller'
            # seller = SellerProfileModel.objects.get(user=user.id)
            
            # try:
            #     posted_jobs = PostjobModel.objects.filter(seller=seller)

            # except:
            #     posted_jobs = None

            # bid_dict = {}
            
            # for data in posted_jobs:
            #     bid_obj = BidAmountModel.objects.filter(job=data)
            #     bid_dict[data] = bid_obj

            # return render(request, 'mainapp/new_index.html', {
            #     'bid_dict': bid_dict, 
            #     'profile_type': profile_type,
            #     'sellerlogo':seller,
            #     }
            # )
        # Dashboard for the buyer or freelancer
        elif user.is_buyer:
            return redirect('home')
        #     category_data,skills_data,jobtype_data=None,None,None

        #     if request.method == "POST":
                
        #         for data in request.POST:

        #             if data == 'csrf':
        #                 break

        #             key=data
        #             value=request.POST[data]

        #         if key=="category":
        #             category_data=JobCategoryModel.objects.filter(category_title__icontains=value).values_list('id')
                    
        #         else:
        #             category_data=None

        #         if key=="job":
        #             jobtype_data=JobTypeModel.objects.filter(job_type_title__icontains=value).values_list('id')

        #         else:
        #             jobtype_data=None

        #         if key=="skills":
        #             skills_data=SkillModel.objects.filter(skill_title__icontains=value).values_list('id')

        #         else:
        #             skills_data=None
                    
            
        #     profile_type = 'buyer'
        #     buyer = BuyerProfileModel.objects.get(user=user)
        #     applied_by_user = ApplyForJobModel.objects.filter(buyer=buyer).values_list('applied_job_id', flat=True)
        #     accepted_jobs=[]
        #     applied_job = PostjobModel.objects.exclude(id__in=applied_by_user) 
            
        #     if category_data:
        #         applied_job=PostjobModel.objects.filter(category_type__in=category_data).exclude(id__in=applied_by_user) 
                

        #     elif jobtype_data:
        #         applied_job=PostjobModel.objects.filter(job_type__in=jobtype_data).exclude(id__in=applied_by_user)

        #     elif skills_data:
        #         applied_job=PostjobModel.objects.filter(skills__in=skills_data).exclude(id__in=applied_by_user)

        #     else:
        #         applied_job = PostjobModel.objects.exclude(id__in=applied_by_user)
        #     #if request.GET;

        #     for accepted_job in PostjobModel.objects.all():

        #         try:
        #             bid=BidAmountModel.objects.get(job=accepted_job)
                
        #             if bid.is_accepted:
        #                 accepted_jobs.append(accepted_job)

        #             else:
        #                 continue

        #         except Exception as e:
        #             pass
                
            
        #     # applied_job = PostjobModel.objects.exclude(id__in=applied_by_user) 
        #     jobs_applied = PostjobModel.objects.filter(id__in=applied_by_user)
        #     sellers = SellerProfileModel.objects.all()
        #     exclude_applied_job_dict = {}
        #     applied_job_dict = {}
          
        #     new_dict={}
        #     for alljob in PostjobModel.objects.all():

        #         try:
        #             job =ApplyForJobModel.objects.get(applied_job=alljob)

        #         except:
        #             job = None

        #         if job and job.buyer==buyer:
        #             new_dict[alljob]='applied'
        #         else:
        #             new_dict[alljob]="not applied"



        #     for data in applied_job:
        #         seller = SellerProfileModel.objects.get(id=data.seller.id)
                
        #         try:
        #             exclude_applied_job_dict[seller].append(data)
        #         except:
        #             exclude_applied_job_dict[seller] = list()
        #             exclude_applied_job_dict[seller].append(data)
            
        #     for data in jobs_applied:
        #         seller = SellerProfileModel.objects.get(id=data.seller.id)
        #         applied_job_dict[seller] = data
        #     myt = PostjobModel.objects.filter()
        #     abc = JobFilter(request.GET,queryset=myt)
        #     prodo =   abc.qs
        #     return render(request, 'home.html',
        #                   {
        #                     'exclude_applied_job': applied_job,
        #                     'accepted_jobs':accepted_jobs,
        #                     'jobs_applied': jobs_applied,
        #                     'profile_type': profile_type,
        #                     'sellers': sellers,
        #                     'applied_job': new_dict,
        #                     'exclude_applied_job_dict': exclude_applied_job_dict,
        #                     'categories': JobCategoryModel.objects.all(),
        #                     'jobtype': JobTypeModel.objects.all(),
        #                     'skills': SkillModel.objects.all(),
        #                     'prodo': prodo,
        #                     'myfilter':abc,
        #                     'applied_by_user':applied_by_user,
        #                     'allofjobs':PostjobModel.objects.all()
                              
        #                   }
        #                 )
            

        else:
            return redirect('profiletype')
    category = []
    categories = JobCategoryModel.objects.all()
    for i in categories:
        print(i)
        post = PostjobModel.objects.filter(category_type = i)
        no_of_jobs = post.count()
        category.append({'cat':i, 'post':no_of_jobs})
    print (category)
    context = {
        'buyer': BuyerProfileModel.objects.all(),
    'seller':SellerProfileModel.objects.all(),
    'categories': categories,
    'category':category,
    'skills' : SkillModel.objects.all(),   
    'jobs' : PostjobModel.objects.all()
    }
    return render(request, 'mainapp/new_index.html', context= context)


"""-----------this function is only for testing if status of page is successful or not-----------"""

def success_func(request):
    # user = User.objects.get()
    return render (request, 'mainapp/success.html')


"""-----------view for sending the otp to the mail and verify it-----------"""

def verify_email(request):
    
    if request.method == 'POST':
        otp = request.POST['otp']
        otpuser = OTPModel.objects.filter(otp=otp).first()
        
        if otpuser is not None:
            user = User.objects.get(pk=otpuser.user.id)
            user.is_verified = True
            user.save()
            otpuser.delete()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            if user.is_seller:
                return redirect('selleradd')
            elif user.is_buyer:
                return redirect('buyeradd')
        else:
            messages.error(request,'OTP is incorrect.')
            return render(request, 'mainapp/otp_verification.html')
    return render(request, 'mainapp/otp_verification.html')


"""-----------view for the user which profile(client or freelancer) he/she wants-----------"""

def profile_type(request):
    
    if request.method == 'POST':
        profiletype = request.POST['profiletype']
        login_user_id = request.user.id
        user = User.objects.get(pk=login_user_id)
        
        if profiletype == 'seller':
            return redirect('selleradd')
        
        elif profiletype == 'buyer':
            return redirect('buyeradd')
        else:
            return render(request, 'mainapp/profiletype.html', {'message': 'something went wrong please try again'})
    return render(request, 'mainapp/profiletype.html')



"""-----------view for the login account-----------"""

def Login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        try:
            user = User.objects.get(username1=username)
        except:
            try:
                user = User.objects.get(email=username)
            except:
                user=None
                
            

            
        # user = authenticate(username=username, password=password)
        
        
        if user is not None:
            if user.check_password(password):
            
                if user.is_verified:
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    if not(user.is_seller or user.is_buyer):
                        return redirect('profiletype')
                    return redirect('/')
                else:
                    userotp = OTPModel.objects.filter(user=user)
                    if userotp:
                        userotp.delete()
                    otp = random.randint(100000, 999999)
                    otpmodel = OTPModel(user=user, otp=otp)
                    otpmodel.save()
                    send_otp_with_celery.delay(username,otp)
                    return redirect('verify')
            else:
                messages.error(request,'Please check your username and password')
        else:
            error = 'Please Check your email/password'
            return render(request, 'mainapp/signin.html', {'error': error})
    # if seller is  None:
    #             return redirect('register')

    return render(request, 'mainapp/signin.html')

def signout(request):
    logout(request)
    return redirect('login')

def forgetpassword(request):

    if request.method=="POST":
        username = request.POST.get("username")
        try:
            user = User.objects.get(email=username)
        except:
            user=""
        if user:
            otp = random.randint(100000, 999999)
            otpmodel = OTPModel(user=user, otp=otp)
            otpmodel.save()
            send_otp_with_celery.delay(username,otp)
            subject = "OTP Verification From Digibuddies"
            message = f"Your OTP for Account Verification in Digibuddies is {otp}"
            send_mail(subject, message, 'tu716599@gmail.com', [username], fail_silently=False)
            print("pass")
            return render(request,'mainapp/verification.html',{'user':user})
    
        else:
            print("fail")
            messages.error(request,"email Doesn't match")
    
    return render(request,'mainapp/forget.html')

def verify_forget_email(request):
    
    if request.method == 'POST':
        otp = request.POST['otp']
        user = request.POST['user']
        otpuser = OTPModel.objects.filter(otp=otp).first()
        print(otpuser)
        
        if otpuser is not None:
            otpuser.delete()
            return render(request,"mainapp/reset-password.html",{'user':user})
        else:
            print("fail")
    return render(request, 'mainapp/verification.html')

def resetnewpassword(request):
    if request.method == 'POST':
        password = request.POST.get("password")
        password1 = request.POST.get("password1")
        user=request.POST.get('user')
        usern=User.objects.get(email=user)
        print(usern)
        if password==password1:
            usern.set_password(password1)
            usern.save()
            return render(request,"mainapp/set-new-password.html")
        else:
            messages.error("password doesn't match")
        
           
    return render(request,'mainapp/reset-password.html',)



"""-----------view for registering the user as a buyer or freelancer-----------"""

@login_required
def buyer_form_view(request):
    # user = User.objects.get(pk=request.user.id)
    # buyer = BuyerProfileModel.objects.get(user=user)
    
    if request.method == 'POST':
        
        if request.user.is_authenticated:
            form = BuyerForm(request.POST, request.FILES)    
            if form.is_valid():
                profile_desc = form.cleaned_data['profile_desc']
                #linkedin_profile = form.cleaned_data['linkedin_profile']
                #github_profile = form.cleaned_data['github_profile']
                profile_picture = form.cleaned_data['profile_picture']
                resume = form.cleaned_data['resume']
                city = form.cleaned_data['city']
                state = form.cleaned_data['state']
                category = form.cleaned_data['category']
                country = form.cleaned_data['country']
                gender = request.POST['gender']
                #skills = request.POST.getlist('skills')
                long_description = form.cleaned_data['long_description']
                user = request.user
                buyer = BuyerProfileModel(user=user, category = category, profile_desc=profile_desc, 
                city=city, state=state, country=country, profile_picture=profile_picture, resume=resume, gender=gender, long_description=long_description)
                buyer.save()
                user_data = User.objects.get(pk=request.user.id)
                #user.is_buyer = True
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                user_data.first_name = first_name
                user_data.last_name = last_name
                user_data.save()
                return redirect('index')
            else:
                print(form.errors)
                    
                

            # if request.POST.get('skill_added'):
            #     form = BuyerForm()
            #     skilladd=SkillModel()
            #     skilltoadd=request.POST.get('skill_added')
            #     if not SkillModel.objects.filter(skill_title=skilltoadd):
            #         skilladd.skill_title=skilltoadd
            #         skilladd.skill_desc=skilltoadd
            #         skilladd.save()
            #     else:
            #         messages.success(request,"Its already Exists")
            #     skill_type = SkillModel.objects.all()
            # context ={
            #     'form': form, 'skills': skill_type
            # }
            
            
    
    else:
        form = BuyerForm()
    return render(request, 'freelancer/freelancer_form.html', {'form': form })

"""-----------view for seller or client for posting a new job-----------"""

#old view post job
@login_required
@seller_role_required
def post_job_view(request):
    user = User.objects.get(pk=request.user.id)
    seller = SellerProfileModel.objects.get(user=user)
    form = PostJobForm(request.POST, request.FILES)
    print(request.POST)
    print(request.FILES)  
    if request.method == 'POST':
        user = User.objects.get(pk=request.user.id)
        seller = SellerProfileModel.objects.get(user=user)
        title=request.POST['job_title']
        short_desc=request.POST['short_desc']
        skill_list=request.POST.getlist('skill_type')
        job_ki_type=request.POST['job_type']
        job = JobTypeModel.objects.get(job_type_title = job_ki_type)
        print(job)
        category_type=request.POST['category_type']
        cat = JobCategoryModel.objects.get(id=category_type)
        print(cat)
        deadline=request.POST['deadline']
        amount=request.POST['askamount']
        amount_2=request.POST['askamount_2']
        long_desc=request.POST['full_desc']
        try:
            file_upload=request.FILES['file_upload']
        except:
            file_upload={}
        
        job = PostjobModel(seller = seller, job_title=title, short_desc=short_desc, job_type=job, 
                        category_type=cat, deadline=deadline, askamount=amount, askamount_2=amount_2,
                        file_upload=file_upload, full_desc=long_desc )
        job.save()
        skill_type_obj = SkillModel.objects.filter(skill_title__in=skill_list)
        job.skills.set(skill_type_obj)
        job.save()
        messages.success(request, "Your Profile has been Updated Successfully.")
        # return to home page 
        # 
        return redirect('index')
       
        
    else:
        form = PostJobForm()
    skill_type = SkillModel.objects.all()
    job_t = JobTypeModel.objects.all()
    return render(request, 'client/Post_A_Job.html', {'form':form, 'skill_type':skill_type, 'job':job_t,
                                                      'seller':seller})      
       
"""------------view for freelancer or buyer for viewing the list of all jobs-----------"""

@login_required
def apply_job_view(request):
    user = User.objects.get(pk=request.user.id)
    buyer = BuyerProfileModel.objects.get(user=user)

    alljob = PostjobModel.objects.all()
    
    
    accepted_jobs = BidAmountModel.objects.filter(is_accepted=True)
    
   
    alljoba = alljob.exclude(id__in=accepted_jobs.values('job_id'))
    
    
    return render(request, 'home.html', {'applied_job': alljoba,'buyer': buyer })


"""------------view for freelancer or buyer for applying a job on apply form-----------"""

@buyer_role_required
def apply_job_form_view(request, id=None,slug=None):
    
    if request.method == 'POST':
    
        if request.user.is_authenticated:
            form = ApplyJobForm(request.POST, request.FILES)
            if form.is_valid():
                pitch = form.cleaned_data['pitch']
                bidamount = form.cleaned_data['bidamount']
                applied_job = PostjobModel.objects.get(slug=slug)
                user = User.objects.get(pk=request.user.id)
                buyer = BuyerProfileModel.objects.get(user=user.id)
                seller = SellerProfileModel.objects.get(pk=applied_job.seller.id)
                job_application = ApplyForJobModel(buyer=buyer, seller=seller, pitch=pitch,
                                                   bidamount=bidamount, applied_job=applied_job)
                job_application.save()
                bid = BidAmountModel(job=applied_job, bidder=buyer, bid_amount=bidamount,pitch=pitch)
                bid.save()

                recipient = request.user
                link = '/client/job_detail/' + applied_job.slug
                
                notify.send(recipient, recipient=seller.user, verb='Applied for your job',description='Someone Applied for your job' ,cta_link=link)
                payload = {"head": "Apply Bid", "body": user.first_name + " applied for your job","url":"/client/job_detail/"+applied_job.slug}

                send_user_notification(user=seller.user, payload=payload, ttl=1000)
                return redirect('index')
            else:
                applied_job = PostjobModel.objects.get(slug=slug)
                skills = SkillModel.objects.all()
                return render(request, 'freelancer/applyjobform.html', {'applied_job': applied_job, 'form': form, 'skills': skills})

    else:
        form = ApplyJobForm()
        applied_job = PostjobModel.objects.get(slug=slug)
        skills = SkillModel.objects.all()
    
    return render(request, 'freelancer/applyjobform.html', {'applied_job': applied_job, 'form': form, 'skills': skills})


"""-----------view for seller for view the profile details of buyer or freelancer-----------"""

@login_required
def buyer_details_view(request, id):
    buyer_detail = BuyerProfileModel.objects.get(pk=id)

    return render(request, 'freelancer/buyerdetail.html', {'buyer_detail': buyer_detail})



"""-----------view for seller to view or display the job he/she has posted-----------"""
"_____client accept perposal______"
def client_page_det(request,id):
    user = User.objects.get(pk=request.user.id)
    seller = SellerProfileModel.objects.get(user=user.id)
    project=PostjobModel.objects.get(id=id)
    bids=BidAmountModel.objects.filter(job=project,is_accepted=False,is_rejected=False)
    
    
    return render(request,'client/client_project_det.html',{'project':project,'bids':bids,
                                                            'seller':seller})

def save_job(request,id):
    accepted=BidAmountModel.objects.get(pk=id)
    accepted.is_accepted=True
    accepted.save()
    return redirect ('client_home')

def reject_job(request,id):
    rejected=BidAmountModel.objects.get(pk=id)
    rejected.is_rejected=True
    rejected.save()
    return redirect ('client_home')

def view_proposal(request,id):
    user = User.objects.get(pk=request.user.id)
    seller = SellerProfileModel.objects.get(user=user.id)
    bids=BidAmountModel.objects.get(id=id)
    return render (request,"client/view-proposal.html",{'bid':bids,
                                                        'seller':seller})


@login_required
def listjobs(request):
    user = User.objects.get(pk=request.user.id)
    seller = SellerProfileModel.objects.get(user=user) 
    try:
        posted_jobs = PostjobModel.objects.filter(seller=seller)
    except:
        posted_jobs = None  
    bid_dict = {}  
    for data in posted_jobs:
        bid_obj = BidAmountModel.objects.filter(job=data)
        bid_dict[data] = bid_obj
    return render(request, 'seller/listjobs.html', {'bid_dict': bid_dict})



"""-----------View for both freelancer(buyer ) and client(seller) for viewing the job details-----------"""

@login_required
def job_detail(request, slug=None):
    posted_job = PostjobModel.objects.get(slug=slug)
    bid_obj = BidAmountModel.objects.filter(job=posted_job)
    return render(request, 'client/jobdetail.html', {'posted_job': posted_job, 'bid_details': bid_obj})

   
    
"""-----------view for the freelancer(buyer) for view all the jobs he/she applied-----------"""

@login_required
def proposals_list(request):
    user = User.objects.get(pk=request.user.id)
    buyer = BuyerProfileModel.objects.get(user=user)
    applied_by_user = ApplyForJobModel.objects.filter(buyer=buyer)
    data_dict = {}
    accepted_jobs=[]

    for data in applied_by_user:
        job = PostjobModel.objects.get(id=data.applied_job.id)

        try:
            accepted=BidAmountModel.objects.get(job=job)

            if accepted.is_accepted:
                accepted_jobs.append(job)        
        except:
            pass
        finally:
            data_dict[job] = ApplyForJobModel.objects.get(buyer=buyer,applied_job=job)
    return render(request, 'freelancer/proposedserviceslist.html', {'applied_by_user': data_dict,'accepted_jobs':accepted_jobs})



"""-----------view for adding the seller (client) profile-----------"""

@login_required
# @profile_required
#rewite seller_form_view with cleaner code and remove commented code
#if request is not post return the form so taht user can fill it
# #if request is post then check if user is authenticated
# #if user is authenticated then get the form data and save it
# #if user is not authenticated then redirect to login page
def seller_form_view(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            user = User.objects.get(pk=request.user.id)
            try:
                seller = SellerProfileModel.objects.get(user=user)
           
                form = SellerForm(request.POST, request.FILES, instance=seller)
            except:
                seller = None
                form = SellerForm(request.POST, request.FILES)
                print(request.POST)
            if form.is_valid():
                ab = form.save(commit=False)
                user.first_name = request.POST.get('first_name')
                user.last_name = request.POST.get('last_name')
                user.save()
                ab.user = user
                ab.save()
                return redirect('index')
        else:
            return redirect('login')
    else:
        form = SellerForm()
    return render(request, 'client/client_form.html', {'form':form})





"""-----------google login redirect view to the profile type-----------"""

def google_user_redirect_view(request):
    
    if request.user.is_authenticated:
        login_user_id = request.user.id
        user = User.objects.get(pk=login_user_id)
        user.is_verified = True
        user.save()
    
        if request.user.is_seller or request.user.is_buyer:
            return redirect('index')
    
        else:
    
            if request.method == 'POST':
                type = request.POST['radio']
    
                if type == 'seller':
                    user.is_seller = True
                    user.save()
                    return redirect('selleradd')
    
                elif type == 'buyer': 
                    user.is_buyer = True
                    user.save()
                    return redirect('buyeradd')
    
                else:
                    return render(request, 'mainapp/type_profile.html', {'message': 'something went wrong please try again'})

    return render(request, 'mainapp/type_profile.html')


"""-----------client(seller) view to edit the job or update it----------"""

@login_required
@seller_role_required
def seller_job_update_form(request,slug):
    job_update_detail=PostjobModel.objects.get(slug=slug)
    if request.method=="POST":
        form = PostJobForm(request.POST, instance=job_update_detail)
        user = User.objects.get(pk=request.user.id)
        seller = SellerProfileModel.objects.get(user=user)


        if request.POST.get('skill_added'):
            form = PostJobForm(instance=job_update_detail)
            skilladd=SkillModel()
            skilltoadd=request.POST.get('skill_added')
            if not SkillModel.objects.filter(skill_title=skilltoadd):
                skilladd.skill_title=skilltoadd
                skilladd.skill_desc=skilltoadd
                skilladd.save()
            else:
                messages.success(request,"Its already Exists")
            job_type = JobTypeModel.objects.all()

            
            category_type = JobCategoryModel.objects.all()
            skill_type = SkillModel.objects.all()
            return render(request, 'client/clientjobupdate.html', {'form': form, 'job_type': job_type, 'category_type': category_type, 'skills': skill_type,'selected_skills':job_update_detail.skills.all,'selected_jobs':job_update_detail.job_type.all,'selected_category':job_update_detail.category_type.all})
    
        if request.POST.get('job_added'):
            form = PostJobForm(instance=job_update_detail)
            jobtypeadd=JobTypeModel()
            jobtoadd=request.POST.get('job_added')
            if not JobTypeModel.objects.filter(job_type_title=jobtoadd):
                jobtypeadd.job_type_title=jobtoadd
                jobtypeadd.job_type_desc=jobtoadd
                jobtypeadd.save()
            else:
                messages.success(request,"Its already Exists")
            job_type = JobTypeModel.objects.all()

            
            category_type = JobCategoryModel.objects.all()
            skill_type = SkillModel.objects.all()
            return render(request, 'client/clientjobupdate.html', {'form': form, 'job_type': job_type, 'category_type': category_type, 'skills': skill_type,'selected_skills':job_update_detail.skills.all,'selected_jobs':job_update_detail.job_type.all,'selected_category':job_update_detail.category_type.all})
    
        if request.POST.get('cat_added'):
            form = PostJobForm(instance=job_update_detail)
            categoryadd=JobCategoryModel()
            cattoadd=request.POST.get('cat_added')
            if not JobCategoryModel.objects.filter(category_title=cattoadd):
                categoryadd.category_title=cattoadd
                categoryadd.category_desc=cattoadd
                categoryadd.save()

            else:
                messages.success(request,"Its already Exists")
            job_type = JobTypeModel.objects.all()

            category_type = JobCategoryModel.objects.all()
            skill_type = SkillModel.objects.all()
            return render(request, 'client/clientjobupdate.html', {'form': form, 'job_type': job_type, 'category_type': category_type, 'skills': skill_type,'selected_skills':job_update_detail.skills.all,'selected_jobs':job_update_detail.job_type.all,'selected_category':job_update_detail.category_type.all})

        if 'update_job_form' in request.POST:
            if form.is_valid():
                job_update_detail.job_title = form.cleaned_data['job_title']
                job_update_detail.short_desc = form.cleaned_data['short_desc']
                job_update_detail.full_desc = form.cleaned_data['full_desc']
                skill_list = request.POST.getlist('skills')
                job_type_list = request.POST.getlist('job_type')
                category_type_list = request.POST.getlist('category_type')
                job_update_detail.deadline = form.cleaned_data['deadline']
                job_update_detail.askamount = form.cleaned_data['askamount']

                job_update_detail.save()

                skill_type_obj = SkillModel.objects.filter(skill_title__in=skill_list)
                job_update_detail.skills.set(skill_type_obj)
                job_update_detail.save()

                job_type_obj = JobTypeModel.objects.filter(job_type_title__in=job_type_list)
                job_update_detail.job_type.set(job_type_obj)
                job_update_detail.save()

                category_type_obj = JobCategoryModel.objects.filter(category_title__in=category_type_list)
                job_update_detail.category_type.set(category_type_obj)
                job_update_detail.save()
                messages.success(request, "Your Job has been Updated.")
                job_type = JobTypeModel.objects.all()

                category_type = JobCategoryModel.objects.all()
                skill_type = SkillModel.objects.all()
                return render(request, 'client/clientjobupdate.html', {'form': form, 'job_type': job_type, 'category_type': category_type, 'skills': skill_type,'selected_skills':job_update_detail.skills.all,'selected_jobs':job_update_detail.job_type.all,'selected_category':job_update_detail.category_type.all})
            else:
                pass
    
    else:
        form = PostJobForm(instance=job_update_detail)
    
    job_type = JobTypeModel.objects.all()

    category_type = JobCategoryModel.objects.all()
    skill_type = SkillModel.objects.all()
    return render(request, 'client/clientjobupdate.html', {'form': form, 'job_type': job_type, 'category_type': category_type, 'skills': skill_type,'selected_skills':job_update_detail.skills.all,'selected_jobs':job_update_detail.job_type.all,'selected_category':job_update_detail.category_type.all})


"""-----------freelancer(buyer) view for updating the bid----------"""

@buyer_role_required
def apply_job_update_view(request,id=None,slug=None):
    applied_bid=ApplyForJobModel.objects.get(pk=id)
    if request.method == 'POST':

        if request.user.is_authenticated:
            form = ApplyJobForm(request.POST, request.FILES,instance=applied_bid)
    
            if form.is_valid():
                applied_bid.pitch = form.cleaned_data['pitch']
                applied_bid.bidamount = form.cleaned_data['bidamount']
                applied_job = PostjobModel.objects.get(slug=slug)
                user = User.objects.get(pk=request.user.id)
                buyer = BuyerProfileModel.objects.get(user=user.id)
                seller = SellerProfileModel.objects.get(pk=applied_job.seller.id)
                applied_bid.save()
                bid = BidAmountModel.objects.get(job=applied_job, bidder=buyer)
                bid.bid_amount=applied_bid.bidamount
                bid.save()
                recipient = request.user
                link = '/client/job_detail/' + applied_job.slug
        
                notify.send(recipient, recipient=seller.user, verb='Updated his applied job',description='This job has been updated by the user' ,cta_link=link)


                payload = {"head": "Bid Updated", "body": user.first_name + " updated his bid","url":'/client/job_detail/' + applied_job.slug}

                send_user_notification(user=seller.user, payload=payload, ttl=1000)
                messages.success(request, "Your Bid has been Updated.")
                form = ApplyJobForm(instance=applied_bid)

                applied_job = PostjobModel.objects.get(slug=slug)
                skills = SkillModel.objects.all()
    
                return render(request, 'freelancer/updatebid.html', {"applied_job": applied_job, 'form': form, 'skills': skills})
                

    else:
        form = ApplyJobForm(instance=applied_bid)

        applied_job = PostjobModel.objects.get(slug=slug)
        skills = SkillModel.objects.all()
    
    return render(request, 'freelancer/updatebid.html', {"applied_job": applied_job, 'form': form, 'skills': skills})


"""-----------view for seller(client ) for deleting a job----------"""

class delete_job(DeleteView):
    model=PostjobModel
    success_url=''
    template_name='client/jobdelete.html'

# Static funtion  
def payment(request,bid_obj):
   
    
    try: 
        abcds = BidAmountModel.objects.filter(id=bid_obj)
        
        total_amount = abcds.values("bid_amount")[0]['bid_amount']
        
    
        client = razorpay.Client(auth=(settings.KEY,settings.SECRET) )
        payment =  client.order.create({'amount': int(total_amount) * 100, 'currency':'INR', "payment_capture":1 })

    except:
        payment = None

    return HttpResponse(json.dumps(payment))

def successd(request):
    if request.method == "POST": 
        data = request.POST
        buyer_id=data['bidder']
        buyer_model=BuyerProfileModel.objects.get(id=buyer_id)
        buyer_name=buyer_model.user
     
        user=request.user
    
        if data['check'] == "success":
            recipient = request.user
            link = '/freelancer/proposals/'
            notify.send(recipient, recipient=buyer_name, verb='payed you',description='Your Job has been accepted and the user payed you ' ,cta_link=link)
            payload = {"head": "Payment to you", "body": user.first_name + " payed you","url":"/freelancer/proposals/"}

            send_user_notification(user=buyer_name, payload=payload, ttl=1000)


        alldata=data.keys()
        if data['check'] == "success":

            payment_credationals = Payment.objects.create(seller_id = SellerProfileModel.objects.get(user=request.user).id,
                                                        bidder_id = int(data['bidder']),
                                                        order_id =str(data['order_id']),
                                                        payment_id = str(data['payement_id']),
                                                        payment_signature = str(data['signarture_id']),
                                                        amount = int(data['amount']),
                                                        job_id = int(data['job']))
            payment_credationals.save()
            return render(request,"client/success.html")
        elif data['check'] == "failed":
            error = request.POST
           
            payment_error = Payment.objects.create(seller_id = SellerProfileModel.objects.get(user=request.user).id,
                                                        bidder_id = int(data['bidder']),
                                                        order_id =str(data['order_id']),
                                                        payment_id = str(data['payement_id']),
                                                        paymentReport = False,
                                                        amount = int(data['amount']),
                                                        job_id = int(data['job']))
            payment_error.save()

            return render(request,"client/error.html")
            
    else:
        return render(request,"client/success.html")


def Error(request):
    return render(request,"client/error.html")


"""-----------seller(client) view for accepting the bid(proposal) make by buyer(freelancer)----------"""

@login_required
def accept_proposal(request,id):
    accepted=BidAmountModel.objects.get(pk=id)
    accepted.is_accepted=True
    accepted.save()
    recipient = request.user
    notify.send(recipient, recipient=accepted.bidder.user, verb='Accepted Your Job proposal',description='Your Proposal is accepted by client' ,cta_link='/buyer/proposals/')
    payload = {"head": "Welcome!", "body": "Your Proposal has been Accepted","url":"/freelancer/proposals/"}

    send_user_notification(user=accepted.bidder.user, payload=payload, ttl=1000)
    return redirect('index')

#exception page
def page_not_found_view(request, exception):
    return render(request, 'mainapp/404.html', status=404)


"""-----------buyer(Freelancer ) view to updating its profile----------"""

@buyer_role_required
def buyer_profile_update_form(request):
    payment_record = Payment.objects.filter(bidder_id = BuyerProfileModel.objects.get(user=request.user))
    
    
    user = User.objects.get(pk=request.user.id)
    buyer = BuyerProfileModel.objects.get(user=user)
    completed_jobs=BidAmountModel.objects.filter(bidder=buyer,is_accepted=True,job__is_completed=True)
    jobs_accepted=BidAmountModel.objects.filter(bidder=buyer,is_accepted=True)
    if request.method == 'POST':
        form = BuyerForm(request.POST, request.FILES, instance=buyer)
        
       
        if 'profile_update' in request.POST:
            if form.is_valid():
                try:
                    buyer.profile_picture = form.cleaned_data['profile_picture']
                except:
                    pass

                try:
                    buyer.resume = form.cleaned_data['resume']
                except:
                    pass

                buyer.address = form.cleaned_data['address']
                buyer.profile_desc = form.cleaned_data['profile_desc']
                buyer.linkedin_profile = form.cleaned_data['linkedin_profile']
                buyer.github_profile = form.cleaned_data['github_profile']
                buyer.city = form.cleaned_data['city']
                buyer.state = form.cleaned_data['state']
                buyer.country = form.cleaned_data['country']
                buyer.gender = request.POST['gender']
                skills_list = request.POST.getlist('skills')
                buyer.long_description = form.cleaned_data['long_description']
                buyer.save()
                buyer_skill_model = SkillModel.objects.filter(skill_title__in=skills_list)
                buyer.skills.set(buyer_skill_model)
                buyer.save()
                buyer.language = request.POST['language']
                buyer.education = request.POST['education']
                buyer.available = request.POST['available']
                buyer.verification = request.POST['verification']
                buyer.age = request.POST['age']
            
                messages.success(request, "Your Profile has been Updated.")
                skills = SkillModel.objects.all()
                return render(request, 'freelancer/user_profile.html', {'form': form, 'profile_picture': buyer.profile_picture,
                                                                        'resume': buyer.resume, 'selected_skills': buyer.skills.all,
                                                                        'skills': buyer.skills, 'language' : buyer.language,
                                                                        'education': buyer.education,'available': buyer.available,
                                                                        'verification': buyer.verification, 'age': buyer.age})

                #return render(request, 'buyer/user_profile.html', {'form': form, 'profile_picture': buyer.profile_picture, 'resume': buyer.resume, 'selected_skills': buyer.skills.all, 'skills': skills})
            else:
                print(form.errors)


        if request.POST.get('skill_added'):
            form = BuyerForm(instance=buyer)
            skilladd=SkillModel()
            skilltoadd=request.POST.get('skill_added')
            if not SkillModel.objects.filter(skill_title=skilltoadd):
                skilladd.skill_title=skilltoadd
                skilladd.skill_desc=skilltoadd
                skilladd.save()
            else:
                messages.success(request,"Its already Exists")
            skills = SkillModel.objects.all()
            return render(request, 'freelancer/user_profile.html', {'user':user,'form': form, 'profile_picture': buyer.profile_picture, 'resume': buyer.resume, 'selected_skills': buyer.skills.all, 'skills': skills})

        if 'pwd_upd' in request.POST:
            form = BuyerForm(instance=buyer)
            if request.POST['password']==request.POST['confirm']:
                u=request.user
                u.set_password(request.POST['password'])
                update_session_auth_hash(request, u)
                u.save()
                messages.success(request,"Your password has been updated")
            else:
                messages.error(request,"Password Doesn't match")
                
    
    else:
        form = BuyerForm(instance=buyer)
    
    skills = SkillModel.objects.all()
    completed_jobs=BidAmountModel.objects.filter(bidder=buyer,is_accepted=True,job__is_completed=True)
    #completed_jobs=BidAmountModel.objects.filter(bidder=buyer,is_accepted=True,job__is_completed=True)
    return render(request, 'freelancer/user_profile.html', {'user':user,'form': form, 'profile_picture': buyer.profile_picture,'resume': buyer.resume, 'selected_skills': buyer.skills.all, 'skills': skills,'payment_record':payment_record,'buyer':buyer,'jobs_accepted':jobs_accepted,'completed_jobs':completed_jobs})

    

"""-----------view for display all the payments----------"""

@seller_role_required
def All_Payments(request):
    data = Payment.objects.filter(seller_id = SellerProfileModel.objects.get(user=request.user))
    try:
        raw = data.values()
        print(raw[0],"---------")
        transfer_amount = sum(i.amount for i in data if i.paymentReport == True)
        return render(request,"client/payment_details.html",{"data":data,"transfer_amount":transfer_amount})
    except:
        return render(request,"client/payment_details.html",{"data":data})
    

"""-----------seller(client) view for updating its profile----------"""


@profile_required
def seller_profile_update_form(request,slug=None):
    # find_user = Payment.objects.filter(seller_id = SellerProfileModel.objects.get(user=request.user))
    # if request.user.is_authenticated:
    user = User.objects.get(pk=request.user.id)
    seller = SellerProfileModel.objects.get(user=user)
    
    if request.method == 'POST':
        if 'profile_update' in request.POST:
            first_name=request.POST['first_name']
            last_name=request.POST['last_name']
            email=request.POST['email']
            country=request.POST['country']
            short_desc=request.POST['short_desc']
            user=request.user
            main_user=User.objects.get(email=user)
            main_user.first_name=first_name
            main_user.last_name=last_name
            main_user.email=email
            main_user.save()
            seller=SellerProfileModel.objects.get(user=main_user)
            seller.country_of_company=country
            seller.company_short_desc=short_desc
            seller.save()
            messages.success(request, "Your Profile has been Updated Successfully.")
            return redirect('seller_update')

  
    


    if request.method == 'POST':

        if 'account_details' in request.POST:
            first_name=request.POST['first_name']
            last_name=request.POST['last_name']
            card_no=request.POST['card_no']
            exp_date=request.POST['exp_date']
            cvv=request.POST['cvv']
            try:
                checkbox=request.POST['checkbox']
                print(checkbox)
            except:
                checkbox="off"
            if  checkbox=="on":
                acdetails.first_name=first_name
                acdetails.last_name=last_name
                acdetails.card_number=card_no
                acdetails.expiry_date=exp_date
                acdetails.cvv=cvv
                acdetails.save()
                messages.success(request, "Your Account Details has been Updated Successfully.")
                return redirect('seller_update')
            else:
                messages.success(request, "Please check the checkbox first.")

        if 'pwd_upd' in request.POST:
            # form = BuyerForm(instance=buyer)
            if request.POST['password']==request.POST['confirm']:
                u=request.user
                u.set_password(request.POST['password'])
                update_session_auth_hash(request, u)
                u.save()
                messages.success(request,"Your password has been Updated Successfully")
            else:
                messages.error(request,"Password Doesn't match")

        else:
            form = SellerForm(instance=seller)
    return render(request, 'client/client_profile.html', {"seller":seller})


"""-----------notifications view for viewing the notifications for both buyer and seller ----------"""
@profile_required
def notifications(request):
    try:
        
        notified = NotificationCTA.objects.filter(notification__recipient=request.user)
    except:
        notified={}
    return render(request,'mainapp/notifications.html',{'notify':notified})

# view for notifications to set them as a read 
def mark_as_read(request, slug=None):
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id)
    notification.mark_as_read()
    return redirect('notifications')

# view for deleting the notifications for both buyer and seller 
def delete_notification(request, slug=None):
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id)
    notification.delete()

    return redirect('notifications')                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                


def onlyfilters(request):
    myt = PostjobModel.objects.filter()
    abc = alljobfilter(request.GET,queryset=myt)
            
    prodo =   abc.qs
    return render(request,'freelancer/jobsfilter.html',{'formfilter':abc,'prodo':prodo})
# ------------------- code by rishi ----------

def custom_admin(request):
    if request.method == "GET":
        
        instance = BuyerProfileModel.objects.all()
        context = {
            "data":instance
        }
        return render(request,"client/custom_admin.html",context)

def Block_Unblock(request):
    """ this function is used to block  and unblock user/client """
    if request.method == "GET":
        raw = request.GET['keyy']
        instance = User.objects.get(id = raw)
        if instance.is_active == True:
            instance.is_active = False
            instance.save()
            send_mail_wiht_celery.delay(instance.email,request.GET['msg'])
        elif instance.is_active == False:
            instance.is_active = True
            instance.save()
            send_mail_wiht_celery.delay(instance.email,request.GET['msg'])
            
            
        return JsonResponse({"status":"success"})
    
def aadmin(request):
    if request.method == "GET":
        instance = BuyerProfileModel.objects.all()
        context = {
            "data":instance
        }
        return render(request,"custom-admin/index.html",context)


@user_passes_test(lambda u: u.is_admin) 
def table(request):
    """ this function return freelancer data """
    if request.method == "GET":
        sid = request.user.id
        instance = User.objects.get(id = sid)
        if instance.is_admin == True:
            client_instance = SellerProfileModel.objects.exclude(user=instance)
            print(client_instance,"------------")
        
        freelancer_instance = BuyerProfileModel.objects.all()
        context = {
            "data":freelancer_instance,
            "client":client_instance
        }
        return render(request,"custom-admin/tables.html",context)
    
def All_jobs(request):
    """ This function show all jobs on  custom-admin page """
    if request.method == "GET":
        instance = PostjobModel.objects.all()
        context = {
            "jobs":instance
            }
        return render(request,"custom-admin/Jobs.html",context)
    
def custom_payment(request):
    """ This function fetch the all payment database """
    if request.method == "GET":
        instance = Payment.objects.all()
        context = {
            'all_payments':instance
        }
        return render(request,"custom-admin/payment.html",context)

def custom_biding_UI(request):
    """ this function return the bidding  """
    if request.method == "GET":
        instance = BidAmountModel.objects.all()
        context = {
            'all_bidings':instance
        }
        return render(request,"custom-admin/biding.html",context)


# def private_chat_home(request):
#     users = User.objects.exclude(email=request.user)
#     return render(request, 'mainapp/chatroom.html', context={'users': users})

# def chatPage(request, username):
#     user_obj = User.objects.get(first_name=username)
#     users = User.objects.exclude(email=request.user.email)
#     if request.method =="POST":
#         img = request.FILES.getlist('files[]',None)
#         fullfile=img[0]
#         strfullfile=str(fullfile)
#         # print(files,"======--------")
#         # img=request.FILES['file_upload']
#         print(strfullfile) 
#         ext = strfullfile.split('.')[-1]
#         a=''
#         if ext == 'jpeg' or ext =='png' or ext == "jpg" or ext =="img" :
#             a='image'
#         elif ext == 'mp4':
#             a='video'
#         else:
#             a='others'
#         print()
#         if request.user.id > user_obj.id:
#             thread_name = f'chat_{request.user.id}-{user_obj.id}'
#         else:
#             thread_name = f'chat_{user_obj.id}-{request.user.id}'
#         image_save=FileUpload(files_upload=img[0])
#         image_save.save()
#         return JsonResponse({'url':image_save.files_upload.url,'msgtype':a})


    
#     if request.user.is_authenticated:

#         if request.user.id > user_obj.id:
#             thread_name = f'chat_{request.user.id}-{user_obj.id}'
#         else:
#             thread_name = f'chat_{user_obj.id}-{request.user.id}'
#         message_objs = ChatModel.objects.filter(thread_name=thread_name)
#         print(message_objs)

#         return render(request, 'mainapp/chat.html', context={'user' : f"{user_obj.id}" ,'users': users, 'messages' : message_objs, 'username' : user_obj, 'count' : len(message_objs)})
#     else:
#         return render(request, 'mainapp/chatroom.html')



"""-----------buyer(Freelancer) view to edit its profile ----------"""

# @buyer_role_required
def buyer_profile_edit_form(request):
    payment_record = Payment.objects.filter(bidder_id = BuyerProfileModel.objects.get(user=request.user))
    
    
    user = User.objects.get(pk=request.user.id)
    buyer = BuyerProfileModel.objects.get(user=user)
    if request.method == 'POST':
        if 'general_details' in request.POST:
            first_name=request.POST['first_name']
            last_name=request.POST['last_name']
            email=request.POST['email']
            Dob=request.POST['Dob']
            country=request.POST['country']
            category=request.POST['category']
            desc=request.POST['headline']
            state=request.POST['state']
            city=request.POST['city']
            available=request.POST['available']
            gender=request.POST['gender']
            # skills=request.POST['skill']
            user=request.user
            main_user=User.objects.get(email=user)
            main_user.first_name=first_name
            main_user.last_name=last_name
            main_user.email=email
            main_user.save()
            cat=JobCategoryModel.objects.get(category_title=category)
            buyer=BuyerProfileModel.objects.get(user=main_user)
            buyer.dob=Dob
            buyer.country=country
            buyer.category=cat
            buyer.profile_desc=desc
            buyer.state=state
            buyer.city=city
            buyer.available=available
            buyer.gender=gender
            # buyer.skills=skills
            buyer.save()
            messages.success(request, "Your Profile has been Updated Successfully.")
            return redirect('edit_profileuser')

        # if 'skill_details' in request.POST:
        #     skills=request.POST['skill']
        #     buyer.skills=skills
        #     buyer.save
        #     messages.success(request, "Your Skills has been Updated Successfully.")
        #     return redirect('edit_buyerprofile')

    
        if 'desc_details' in request.POST:
            long_description=request.POST['details']
            buyer.long_description=long_description
            buyer.save()
            messages.success(request, "Your Profile has been Updated Successfully.")
            return redirect('edit_profileuser')

        if 'socialaccount_details' in request.POST:
            experience=request.POST['experience']
            resume=request.POST['resume']
            linkedin=request.POST['linkedin']
            github=request.POST['github']            
            buyer.experience=experience
            buyer.resume=resume
            buyer.linkedin_profile=linkedin
            buyer.github_profile=github
            buyer.save()
            messages.success(request, "Your Social Account Details has been Updated Successfully.")
            return redirect('edit_profileuser')

        if 'education_details' in request.POST:
            education=request.POST['education']
            buyer.education=education
            buyer.save()
            messages.success(request, "Your Education Details has been Updated Successfully.")
            return redirect('edit_profileuser')

    user = User.objects.get(pk=request.user.id)
    try:
        acdetails = AccountDetailsModel.objects.get(user=user)
    except AccountDetailsModel.DoesNotExist:
        user = None
    if request.method == 'POST':

        if 'account_details' in request.POST:
            first_name=request.POST['first_name']
            last_name=request.POST['last_name']
            card_no=request.POST['card_no']
            exp_date=request.POST['exp_date']
            cvv=request.POST['cvv']
            try:
                checkbox=request.POST['checkbox']
                print(checkbox)
            except:
                checkbox="off"
            if checkbox=="on":
                acdetails.first_name=first_name
                acdetails.last_name=last_name
                acdetails.card_number=card_no
                acdetails.expiry_date=exp_date
                acdetails.cvv=cvv
                acdetails.save()
                messages.success(request, "Your Account Details has been Updated Successfully.")
                return redirect('edit_profileuser')
            else:
                messages.success(request, "Please check the checkbox first.")
        

        if 'pwd_upd' in request.POST:
            # form = BuyerForm(instance=buyer)
            if request.POST['password']==request.POST['confirm']:
                u=request.user
                u.set_password(request.POST['password'])
                update_session_auth_hash(request, u)
                u.save()
                messages.success(request,"Your password has been Updated Successfully")
            else:
                messages.error(request,"Password Doesn't match")
                
    
    else:
        form = BuyerForm(instance=buyer)
    
    skills = SkillModel.objects.all()
    cat= JobCategoryModel.objects.filter()
    return render(request, 'freelancer/edit_profile.html', { 'profile_picture': buyer.profile_picture, 'desc': buyer.profile_desc,
                                                                        'resume': buyer.resume, 'selected_skills': buyer.skills.all,
                                                                        'skills': buyer.skills, 'language' : buyer.language,
                                                                        'education': buyer.education,'available': buyer.available,
                                                                        'verification': buyer.verification, 'experience': buyer.experience,
                                                                        'buyer_linkedin': buyer.linkedin_profile,'username':buyer.user,
                                                                        'long_description': buyer.long_description, 'git_profile': buyer.github_profile ,'buyer':buyer,
                                                                        'category': buyer.category,'dob': buyer.dob, 'country':buyer.country,'desc': buyer.profile_desc,
                                                                        'state':buyer.state,'city':buyer.city,'cat':cat,
                                                                        'gender':buyer.gender,
                                                                        # 'first_name':acdetails.first_name, 
                                                                        # 'last_name':acdetails.last_name,
                                                                        # 'card_no':acdetails.card_number,
                                                                        # 'exp_date':acdetails.expiry_date, 
                                                                        # 'cvv':acdetails.cvv
                                                                        })


"""------------------------API------------------------API------------------------API------------------------"""


"""----------API for USER LOGIN-----------"""

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return{
        'refresh':str(refresh),
        'access':str(refresh.access_token) 
    }

# user login view
class UserLoginView(APIView):

  def post(self, request):
    """
    :return: username and password for login and correct params.
    """
  
    username = request.data.get('email')
    password = request.data.get('password')
    if not username or not password:
      return Response({'msg': 'Invalid parameters'})
      
    
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        checkemail = User.objects.get(email=username)
    except:
        checkemail = None
    if checkemail is None:
        return Response({'msg': 'No user found'}, status=status.HTTP_404_NOT_FOUND)
    user = authenticate(username=username, password=password)
    if user is not None:
    # generate token when user login for authenticating
          token = get_tokens_for_user(user)
          return Response({'token': token, 'msg': 'Login Success'}, status=status.HTTP_200_OK)
    return Response({'msg': 'password incorrect'}, status=status.HTTP_404_NOT_FOUND)


"""----------API for GET USER PROFILE DATA-----------"""

class ProfileApi(APIView):
    def get(self, request):
        if self.request.user.is_authenticated:
            print(self.request.user)
            data=User.objects.filter(email=self.request.user).values('email','first_name','last_name')
            print(data)
            serializer = ProfileApiSerializer(data,many=True)

            return Response({'msg':'user found',"data":serializer.data})



"""----------API for Bid Amount-----------"""

class BidAmountApi(APIView):
    def get(self, request):
        if self.request.user.is_authenticated:
            print(self.request.user)
            data=BidAmountModel.objects.filter(is_accepted=True)
            print(data)
            serializer = CustomBidAmount(data,many=True)

            return Response({'msg':'Bidding Profile List',"data":serializer.data})
        
        return Response({'msg':'Please Login First'})


"""-----------API for Seller Profile List-----------"""

class SellerProfileAPI(APIView):
    def get(self,request):
        if self.request.user.is_authenticated:
            print(self.request.user)
            data=SellerProfileModel.objects.all()
            print(data)
            serializer = SellerProfileSerializer(data,many=True)

            return Response({'msg':'Seller Profile List',"data":serializer.data})

        return Response({'msg':'Please Login First'})


"""-----------API for Seller Profile List by id-----------"""

class SellerProfileIdAPI(APIView):
    def get(self,request,id):
        if self.request.user.is_authenticated:
            print(self.request.user)
            data=SellerProfileModel.objects.get(id=id)
            print(data)
            serializer = SellerProfileSerializer(data)

            return Response({'msg':'Seller Profile User',"data":serializer.data})

        return Response({'msg':'Please Login First'})


"""-----------API for Buyer Profile List-----------"""

class BuyerProfileAPI(APIView):
    def get(self,request):
        if self.request.user.is_authenticated:
            print(self.request.user)
            data=BuyerProfileModel.objects.all()
            print(data)
            serializer = BuyerProfileSerializer(data,many=True)

            return Response({'msg':'Buyer Profile List',"data":serializer.data})

        return Response({'msg':'Please Login First'})


"""-----------API for Buyer Profile List by ID-----------"""

class BuyerProfileIdAPI(APIView):
    def get(self,request,id):
        if self.request.user.is_authenticated:
            print(self.request.user)
            data=BuyerProfileModel.objects.get(id=id)
            print(data)
            serializer = BuyerProfileSerializer(data)

            return Response({'msg':'Buyer Profile User',"data":serializer.data})

        return Response({'msg':'Please Login First'})


"""-----------Project Billing API-----------"""
            
class ProjectBillingAPI(APIView):
    permission_classes = [IsAuthenticated] 
    def post(self,request):
        serilize_data = request.data
        serializer = ProjectBillingSerializer(data=serilize_data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        else:
            return Response({'msg':f'{serializer.errors}'})

    def get(self, request):
        data = ProjectBillingModel.objects.all()
        print(data)
        serializer = ProjectBillingWithoutUserSerializer(data,many=True)
        return Response({'msg': 'Showing Data',"data":serializer.data})

"""-----------Apply Job API-----------"""


class ApplyJobAPI(APIView):
    
    def post(self, request):
        # if self.request.user.is_authenticated:
        serializer = ApplyJobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'msg':'Please fill complete details'}) 

   

"""-----------API for Project Billing all data by USER ID----------"""

class ProjectBill(APIView):
    response = {}
    permission_classes = [IsAuthenticated]
    def get(self, request,id):
        alldata = []
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days = 1)
        start = today - datetime.timedelta(days=today.weekday())
        end = start + datetime.timedelta(days=6)

        today_sec = ProjectBillingModel.objects.filter(user=request.user,project__job_id=id,duration__date=today).aggregate(Sum('seconds'))
        if today_sec['seconds__sum'] == None:
            today_sec['seconds__sum']=0
        yesterday_sec = ProjectBillingModel.objects.filter(user=request.user,project__job_id=id,duration__date=yesterday).aggregate(Sum('seconds'))

        if yesterday_sec['seconds__sum'] == None:
            yesterday_sec['seconds__sum']=0

        week_sec = ProjectBillingModel.objects.filter(user=request.user,project__job_id=id,duration__date__gte=start,duration__date__lte=end).aggregate(Sum('seconds'))
        print(week_sec)
        if week_sec['seconds__sum'] == None:
            week_sec['seconds__sum']=0
        month_sec = ProjectBillingModel.objects.filter(user=request.user,project__job_id=id,duration__month=today.month,duration__year=today.year).aggregate(Sum('seconds'))
        if month_sec['seconds__sum'] == None:
            month_sec['seconds__sum']=0
        total_sec = ProjectBillingModel.objects.filter(user=request.user,project__job_id=id).aggregate(Sum('seconds'))
        if total_sec['seconds__sum'] == None:
            total_sec['seconds__sum']=0
        
        try:
            latest_task = ProjectBillingModel.objects.filter(user=request.user,project__job_id=id).last().task
        except:
            latest_task = None
        try:    
            latest_id = ProjectBillingModel.objects.filter(user=request.user,project__job_id=id).last().id
        except:
            latest_id = None
        user = request.user.id
        alldata.append({'id':latest_id,'user_id':user,'project_id':id, 'today':today_sec["seconds__sum"],'yesterday':yesterday_sec["seconds__sum"],'week':week_sec["seconds__sum"],
                            'month':month_sec["seconds__sum"],'latest_task':latest_task, 'total':total_sec["seconds__sum"] })
        response = alldata
        return Response({'msg': 'Showing Data',"data":response})
    


"""-----------API for Project Billing by ID-----------"""

class ProjectBillingIDAPI(APIView):
    def get(self,request,id):
        if self.request.user.is_authenticated:
            print(self.request.user)
            data = ProjectBillingModel.objects.get(id=id)
            print(data)
            serializer = ProjectBillingSerializer(data)

            return Response({'msg':"Project Billing Data by ID","data":serializer.data})

        return Response({'msg':'Please Login First'})


"""-----------API for showing bidder data of any job id-----------"""

class JobIdData(APIView):
    
    def get(self,request,id):
        raw = {}

        if self.request.user.is_authenticated:
            print(self.request.user)
            obj = PostjobModel.objects.get(id = id)
            print(obj)
            data = BidAmountModel.objects.filter(job_id = id).values()
            print(data,"---")
            raw['data'] = list(data)
        
        return Response(data)
@profile_required
def project_list(request):
    user = User.objects.get(pk=request.user.id)
    buyer = BuyerProfileModel.objects.get(user=user)
    jobs = PostjobModel.objects.filter()
    today = datetime.datetime.now().date()
    if request.method == "GET":
        allproject = BidAmountModel.objects.filter(bidder__user_id=request.user.id,job__deadline__gte=today)
        complete=BidAmountModel.objects.filter(bidder__user_id=request.user.id,job__is_completed=True,is_accepted=True,job__deadline__gte=today)
        in_progress=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_accepted=True,job__is_completed=False,job__deadline__gte=today)
        pending_project=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_accepted=False,job__is_completed=False,is_rejected=False,job__deadline__gte=today)
        rejected=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_rejected=True,job__deadline__gte=today)
        page_num = request.GET.get('page1', 1)
        paginator = Paginator(allproject,3)
        try:
            instance_pagination = paginator.page(page_num)
        except PageNotAnInteger:
            instance_pagination = paginator.page(1)
        except EmptyPage:
            instance_pagination = paginator.page(paginator.page_num)
    return render(request, 'freelancer/alljob.html', {'jobs':jobs,'all_bidings':allproject,'buyer':buyer,
                                                 'complete':complete,'accept':in_progress,
                                                 'not_accept':pending_project,'not_complete':rejected,'instance_pagination':instance_pagination})
    
@profile_required
def product_filters(request):
    user = User.objects.get(pk=request.user.id)
    buyer = BuyerProfileModel.objects.get(user=user)
    today = datetime.datetime.now().date()
    # myt = PostjobModel.objects.filter(is_completed=False)
    complete=BidAmountModel.objects.filter(is_accepted=True).values('job_id')
    print(complete)
    myt=PostjobModel.objects.filter(is_completed=False,deadline__gte=today).exclude(id__in=complete)
    val=PostjobModel.objects.filter(is_completed=False).exclude(id__in=complete).values("id")
    print(val)
    
    page_num = request.GET.get('page', 1)
    paginator = Paginator(myt,4)
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.page_num)
    abc = alljobfilter(request.GET,queryset=myt)
    hours = JobTypeModel.objects.all()
    allskill = SkillModel.objects.all()     
    prodo = abc.qs
    
    return render(request,'freelancer/freelancerhome.html',{'formfilter':myt,'prodo':prodo,
                                                  'abc':abc,
                                                  'hours':hours,'allskill':allskill,
                                                  'buyer':buyer,'complete':complete,
                                                  'page_obj':page_obj})
    




def check_user_bid_func(job, request):
    current_user = request.user
    buyer=BuyerProfileModel.objects.get(user=request.user)
    bid_amount = BidAmountModel.objects.filter(bidder=buyer, job=job)
    if bid_amount.exists():
        return True
    else:
        return False

    

def productdetails(request,id):
    user = User.objects.get(pk=request.user.id)
    buyer = BuyerProfileModel.objects.get(user=user)
    job=PostjobModel.objects.get(id=id)
    alljobs=PostjobModel.objects.exclude(id=job.id)
    bid=BidAmountModel.objects.all()
    comment=Comment.objects.all()

    check_user_bid = check_user_bid_func(job, request)
    # check_user_bid = "dd"
 
    if request.method=="POST":
        buyer=BuyerProfileModel.objects.get(user=request.user)
        bid_amount =request.POST.get("bid_amount")
        points =request.POST.get("points")
        days =request.POST.get("days")
        pitch =request.POST.get("pitch")
        
        obj=BidAmountModel.objects.create(job=job,bid_amount=bid_amount,bidder=buyer,pitch=pitch, days = points+' '+days)
        obj.save()
        applied_job = PostjobModel.objects.get(id=id)
        seller = SellerProfileModel.objects.get(pk=applied_job.seller.id)
        
        recipient = request.user
        link = '/client/job_detail/' + applied_job.slug
        # notify.send(recipient, recipient=seller.user, verb='Applied for your job',description='Someone Applied for your job' ,cta_link=link)
        
    
    
    return render(request,'freelancer/project-detail.html',{'bid':bid,'job':job,
                                                       'alljobs':alljobs,
                                                       'comment':comment,
                                                       'buyer':buyer,
                                                       'check_user_bid':check_user_bid,
                                                       })
@profile_required    
def notificationsbuyer(request):
    user = User.objects.get(pk=request.user.id)
    buyer = BuyerProfileModel.objects.get(user=user)
    try:
        notified = NotificationCTA.objects.filter(notification__recipient=request.user)
    except:
        notified={}
    return render(request,'freelancer/notification.html',{'notifi':notified,
                                                     'buyer':buyer})
def Mark_all_as_read(request, slug=None):
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id)
    notification.mark_as_read()
    return redirect('notification')

@profile_required
def notificationsseller(request):
    user = User.objects.get(pk=request.user.id)
    profile_type = 'seller'
    seller = SellerProfileModel.objects.get(user=user.id)
    try:
        notified = NotificationCTA.objects.filter(notification__recipient=request.user)
        print(notified)
    except:
        notified={}
    return render(request,'client/notification.html',{'notifi':notified,
                                                      'profile_type':profile_type,
                                                      'seller':seller,})
# client project report 
def projectreport(request,id):
    bidamount = BidAmountModel.objects.get(id=id) 
    today = datetime.datetime.now()
    try:
        seller = SellerProfileModel.objects.get(user=request.user.id)
    except:
        seller=""

    timeaccordinguser=ProjectBillingModel.objects.filter(user=bidamount.bidder.user).order_by('duration').distinct()
    print(timeaccordinguser)
    
        
    return render(request ,"client/screenshot.html",{'seller':seller,
                                                     'billing':bidamount,
                                                     'time':timeaccordinguser,'idd':id,
                                                     'today':today})


def projectreportfreelancer(request,id):
    today = datetime.datetime.now()
    bidamount = BidAmountModel.objects.get(id=id)
    try:
        buyer = BuyerProfileModel.objects.get(user=request.user.id)
    except:
        buyer=""
    print(bidamount.bidder.user)
    timeaccordinguser=ProjectBillingModel.objects.filter(user=bidamount.bidder.user).order_by('duration').distinct()
    return render (request,"freelancer/screenshot.html",{'buyer':buyer,'billing':bidamount,
                                                         'time':timeaccordinguser,'idd':id,
                                                          'today':today})
# pagination of freelancer
def allprojectfreelancer(request):
    user = User.objects.get(pk=request.user.id)
    buyer = BuyerProfileModel.objects.get(user=user)
    jobs = PostjobModel.objects.filter()
    today_date = datetime.datetime.now().date()
    if request.method == "GET":
        instance = BidAmountModel.objects.filter(bidder__user_id=request.user.id,job__deadline__gte=today_date)
        complete=BidAmountModel.objects.filter(bidder__user_id=request.user.id,job__is_completed=True,is_accepted=True,job__deadline__gte=today_date)
        accept=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_accepted=True,job__is_completed=False,job__deadline__gte=today_date)
        not_accept=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_accepted=False,job__is_completed=False,is_rejected=False,job__deadline__gte=today_date)
        not_complete=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_rejected=True,job__deadline__gte=today_date)
        page_num = request.GET.get('page1', 1)
        paginator = Paginator(instance,3)
        try:
            instance_pagination = paginator.page(page_num)
        except PageNotAnInteger:
            instance_pagination = paginator.page(1)
        except EmptyPage:
            instance_pagination = paginator.page(paginator.page_num)
        
    return render(request, 'freelancer/allproject.html', {'jobs':jobs,'all_bidings':instance,'buyer':buyer,
                                                      'instance_pagination':instance_pagination,
                                                      'complete':complete,'accept':accept,
                                                 'not_accept':not_accept,'not_complete':not_complete})
def completejob(request):
    user = User.objects.get(pk=request.user.id)
    buyer = BuyerProfileModel.objects.get(user=user)
    jobs = PostjobModel.objects.filter()
    today = datetime.datetime.now().date()
    if request.method == "GET":
        complete=BidAmountModel.objects.filter(bidder__user_id=request.user.id,job__is_completed=True,is_accepted=True,job__deadline__gte=today)
        instance = BidAmountModel.objects.filter(bidder__user_id=request.user.id,job__deadline__gte=today)
        accept=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_accepted=True,job__is_completed=False,job__deadline__gte=today)
        not_accept=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_accepted=False,job__is_completed=False,is_rejected=False,job__deadline__gte=today)
        not_complete=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_rejected=True,job__deadline__gte=today)
        page_num  = request.GET.get('page2', 1)
        paginator = Paginator(complete,3)
        try:
            complete_pagination = paginator.page(page_num)
        except PageNotAnInteger:
            complete_pagination = paginator.page(1)
        except EmptyPage:
            complete_pagination = paginator.page(paginator.page_num)
        complete_count=BidAmountModel.objects.filter(bidder__user_id=request.user.id,job__is_completed=True,is_accepted=True).count()
    return render(request, 'freelancer/completeproject.html', {'jobs':jobs,'buyer':buyer,'complete':complete,
                                                          'complete_pagination':complete_pagination,
                                                          'complete_count':complete_count,'all_bidings':instance,
                                                          'accept':accept,'not_accept':not_accept,'not_complete':not_complete})
def in_progress_project(request):
    user = User.objects.get(pk=request.user.id)
    buyer = BuyerProfileModel.objects.get(user=user)
    jobs = PostjobModel.objects.filter()
    today = datetime.datetime.now().date()
    if request.method =="GET":
        accept=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_accepted=True,job__is_completed=False,is_rejected=False,job__deadline__gte=today)
        instance = BidAmountModel.objects.filter(bidder__user_id=request.user.id,job__deadline__gte=today)
        complete=BidAmountModel.objects.filter(bidder__user_id=request.user.id,job__is_completed=True,is_accepted=True,job__deadline__gte=today)
        not_accept=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_accepted=False,job__is_completed=False,is_rejected=False,job__deadline__gte=today)
        not_complete=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_rejected=True,job__deadline__gte=today)
        page_num = request.GET.get('page3', 1)
        paginator = Paginator(accept,3)
        try:
            accept_pagination = paginator.page(page_num)
        except PageNotAnInteger:
            accept_pagination = paginator.page(1)
        except EmptyPage:
            accept_pagination = paginator.page(paginator.page_num)
        accept_count=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_accepted=True).count()
    return render(request,'freelancer/progressproject.html',{'accept_pagination':accept_pagination,
                                                             'jobs':jobs,'buyer':buyer,'accept_count':accept_count,
                                                             'all_bidings':instance,'complete':complete,'accept':accept,
                                                 'not_accept':not_accept,'not_complete':not_complete})
def pending_project(request):
    user = User.objects.get(pk=request.user.id)
    buyer = BuyerProfileModel.objects.get(user=user)
    jobs = PostjobModel.objects.filter()
    today = datetime.datetime.now().date()
    if request.method =="GET":
        instance = BidAmountModel.objects.filter(bidder__user_id=request.user.id,job__deadline__gte=today)
        complete=BidAmountModel.objects.filter(bidder__user_id=request.user.id,job__is_completed=True,is_accepted=True,job__deadline__gte=today)
        accept=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_accepted=True,job__is_completed=False,job__deadline__gte=today)
        not_accept=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_accepted=False,job__is_completed=False,is_rejected=False,job__deadline__gte=today)
        not_complete=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_rejected=True,job__deadline__gte=today)
        page_num = request.GET.get('page4', 1)
        paginator = Paginator(not_accept,3)
        try:
            not_accept_pagination = paginator.page(page_num)
        except PageNotAnInteger:
            not_accept_pagination = paginator.page(1)
        except EmptyPage:
            not_accept_pagination = paginator.page(paginator.page_num)
        # not_accept_count=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_accepted=False).count()
    return render(request,'freelancer/pendingproject.html',{'jobs':jobs,'buyer':buyer,'not_accept_pagination':not_accept_pagination,
                              'all_bidings':instance,'complete':complete,'accept':accept,
                                                 'not_accept':not_accept,'not_complete':not_complete})
    
def reject_project(request):
    user = User.objects.get(pk=request.user.id)
    buyer = BuyerProfileModel.objects.get(user=user)
    jobs = PostjobModel.objects.filter()
    today = datetime.datetime.now().date()
    if request.method == "GET":
        instance = BidAmountModel.objects.filter(bidder__user_id=request.user.id,job__deadline__gte=today)
        complete=BidAmountModel.objects.filter(bidder__user_id=request.user.id,job__is_completed=True,is_accepted=True,job__deadline__gte=today)
        accept=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_accepted=True,job__is_completed=False,job__deadline__gte=today)
        not_accept=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_accepted=False,job__is_completed=False,is_rejected=False,job__deadline__gte=today)
        not_complete=BidAmountModel.objects.filter(bidder__user_id=request.user.id,is_rejected=True,job__deadline__gte=today)
        page_num = request.GET.get('page5', 1)
        paginator = Paginator(not_complete,3)
        try:
            not_complete_pagination = paginator.page(page_num)
        except PageNotAnInteger:
            not_complete_pagination = paginator.page(1)
        except EmptyPage:
            not_complete_pagination = paginator.page(paginator.page_num)
    return render(request,'freelancer/rejectedproject.html',{'jobs':jobs,'buyer':buyer,
                                                             'not_complete_pagination':not_complete_pagination,
                                                             'complete':complete,'accept':accept,'not_accept':not_accept,'all_bidings':instance,
                                                             'not_complete':not_complete})
# pagination of client 
def clientproject(request):
    user = User.objects.get(pk=request.user.id)
            
    profile_type = 'seller'
    seller = SellerProfileModel.objects.get(user=user.id)
    today = datetime.datetime.now().date()
    
    try:
        posted_jobs = PostjobModel.objects.filter(Q(seller=seller) & Q(deadline__gte = today))
        try:
            completed_jobs=PostjobModel.objects.filter(seller=seller,is_completed=True)
        except:
            completed_jobs=""

    except:
        posted_jobs = None
    page_num = request.GET.get('page1', 1)
    paginator = Paginator(posted_jobs,3)
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.page_num)
        
        
    try:
        completed_jobs=PostjobModel.objects.filter(seller=seller,is_completed=True)
    except:
        completed_jobs=None
    try:
        in_progress=BidAmountModel.objects.filter(job__in=posted_jobs,is_accepted=True,job__is_completed=False)
        print(in_progress)
    except:
        in_progress={}
    unassigned={}
    try:
        is_bidded=BidAmountModel.objects.filter(job__in=posted_jobs,is_accepted=True).values('job_id')
        print(is_bidded)
        unassigned=PostjobModel.objects.exclude(id__in=is_bidded).filter(seller=seller)
        print(unassigned)


    except:
        unassigned={}
    
    try: 
        rejected=BidAmountModel.objects.filter(job__in=posted_jobs,is_rejected=True)
    except:
        rejected={}
    

    return render(request, 'client/allproject.html', {
        'completed_jobs':completed_jobs,
        'in_progress':in_progress,
        'profile_type': profile_type,
        'seller':seller,
        'posted_jobs':posted_jobs,
        'unassigned':unassigned,
        'rejected':rejected,
        'page_obj':page_obj
        }
    )
def clientprojectcomplete(request):
    user = User.objects.get(pk=request.user.id)
    today = datetime.datetime.now().date()
            
    profile_type = 'seller'
    seller = SellerProfileModel.objects.get(user=user.id)
    
    try:
        posted_jobs = PostjobModel.objects.filter(Q(seller=seller) & Q(deadline__gte = today))
        try:
            completed_jobs=PostjobModel.objects.filter(seller=seller,is_completed=True)
        except:
            completed_jobs=""       

    except:
        posted_jobs = None
    page_num = request.GET.get('page2', 1)
    paginator = Paginator(completed_jobs,4)
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.page_num)
    try:
        in_progress=BidAmountModel.objects.filter(job__in=posted_jobs,is_accepted=True,job__is_completed=False)
    except:
        in_progress={}
    unassigned={}
    try:
        is_bidded=BidAmountModel.objects.filter(job__in=posted_jobs,is_accepted=True).values('job_id')
        unassigned=PostjobModel.objects.exclude(id__in=is_bidded).filter(seller=seller)

    except:
        unassigned={}
    
    try: 
        rejected=BidAmountModel.objects.filter(job__in=posted_jobs,is_rejected=True)
    except:
        rejected={}
    

    return render(request, 'client/completeproject.html', {
        'completed_jobs':completed_jobs,
        'in_progress':in_progress,
        'profile_type': profile_type,
        'seller':seller,
        'posted_jobs':posted_jobs,
        'unassigned':unassigned,
        'rejected':rejected,
        'page_obj':page_obj
        }
    )

def clientprojectprogress(request):
    user = User.objects.get(pk=request.user.id)
            
    profile_type = 'seller'
    seller = SellerProfileModel.objects.get(user=user.id)
    today = datetime.datetime.now().date()
    
    try:
        posted_jobs = PostjobModel.objects.filter(Q(seller=seller) & Q(deadline__gte = today))
        try:
            completed_jobs=PostjobModel.objects.filter(seller=seller,is_completed=True)
        except:
            completed_jobs=""       

    except:
        posted_jobs = None
    try:
        in_progress=BidAmountModel.objects.filter(job__in=posted_jobs,is_accepted=True,job__is_completed=False)
        print(in_progress)
    except:
        in_progress={}
    page_num = request.GET.get('page3', 1)
    paginator = Paginator(in_progress,4)
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.page_num)
    unassigned={}
    try:
        is_bidded=BidAmountModel.objects.filter(job__in=posted_jobs,is_accepted=True).values('job_id')
        print(is_bidded)
        unassigned=PostjobModel.objects.exclude(id__in=is_bidded).filter(seller=seller)
        print(unassigned)


    except:
        unassigned={}
    
    try: 
        rejected=BidAmountModel.objects.filter(job__in=posted_jobs,is_rejected=True)
    except:
        rejected={}
    

    return render(request, 'client/progressproject.html', {
        'completed_jobs':completed_jobs,
        'in_progress':in_progress,
        'profile_type': profile_type,
        'seller':seller,
        'posted_jobs':posted_jobs,
        'unassigned':unassigned,
        'rejected':rejected,
        'page_obj':page_obj
        }
    )
def clientprojectarchivedproject(request):
    user = User.objects.get(pk=request.user.id)
            
    profile_type = 'seller'
    seller = SellerProfileModel.objects.get(user=user.id)
    
    try:
        today = datetime.datetime.now().date()
        posted_jobs = PostjobModel.objects.filter(Q(seller=seller) & Q(deadline__gte = today))
        try:
            completed_jobs=PostjobModel.objects.filter(Q(seller=seller) & Q(deadline__gte = today),is_completed=True)
        except:
            completed_jobs=""       

    except:
        posted_jobs = None
    try:
        in_progress=BidAmountModel.objects.filter(job__in=posted_jobs,is_accepted=True,job__is_completed=False)
        print(in_progress)
    except:
        in_progress={}
    unassigned={}
    try:
        is_bidded=BidAmountModel.objects.filter(job__in=posted_jobs,is_accepted=True).values('job_id')
        unassigned=PostjobModel.objects.exclude(id__in=is_bidded).filter(seller=seller)



    except:
        unassigned={}
        

    
    try: 
        rejected=BidAmountModel.objects.filter(job__in=posted_jobs,is_rejected=True)
    except:
        rejected={}
    page_num = request.GET.get('page4', 1)
    paginator = Paginator(rejected,4)
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.page_num)
    

    return render(request, 'client/archivedproject.html', {
        'completed_jobs':completed_jobs,
        'in_progress':in_progress,
        'profile_type': profile_type,
        'seller':seller,
        'posted_jobs':posted_jobs,
        'unassigned':unassigned,
        'rejected':rejected,
        'page_obj':page_obj
        }
    )

def clientprojectunassigned(request):
    user = User.objects.get(pk=request.user.id)
            
    profile_type = 'seller'
    seller = SellerProfileModel.objects.get(user=user.id)
    today = datetime.datetime.now().date()
    
    try:
        
        posted_jobs = PostjobModel.objects.filter(Q(seller=seller) & Q(deadline__gte = today))
        print(posted_jobs,"-----++++")
        try:
            
            completed_jobs=PostjobModel.objects.filter(seller=seller,is_completed=True)
        except:
            completed_jobs=""       

    except:
        posted_jobs = None
    try:
        in_progress=BidAmountModel.objects.filter(job__in=posted_jobs,is_accepted=True,job__is_completed=False)
        print(in_progress)
    except:
        in_progress={}
    unassigned={}
    try:
        is_bidded=BidAmountModel.objects.filter(job__in=posted_jobs,is_accepted=True).values('job_id')
        unassigned=PostjobModel.objects.exclude(id__in=is_bidded).filter(Q(seller=seller) & Q(deadline__gte = today))


    except:
        unassigned={}
    print(unassigned)
    page_num = request.GET.get('page5', 1)
    paginator = Paginator(unassigned,3)
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.page_num)
    
    try: 
        rejected=BidAmountModel.objects.filter(job__in=posted_jobs,is_rejected=True)
    except:
        rejected={}
    

    return render(request, 'client/unassignedproject.html', {
        'completed_jobs':completed_jobs,
        'in_progress':in_progress,
        'profile_type': profile_type,
        'seller':seller,
        'posted_jobs':posted_jobs,
        'unassigned':unassigned,
        'rejected':rejected,
        'page_obj':page_obj
        }
    )

def create_group_name(request,id):
    user =User.objects.get(pk=request.user.id)
    freelancer=BidAmountModel.objects.get(id=id)
    biddr=BuyerProfileModel.objects.get(id=freelancer.bidder.id)
    biddername=User.objects.get(id=biddr.user.id)
    projectname=freelancer.job.seller.user.username1 
    bidder_id =biddername.id
    bidder_name = biddername.username1
    prj_name = projectname.replace("-","_") +"_"+str(bidder_name)
    users_list_data=[]
    users_list_data.append(user)
    users_list_data.append(biddername)
    try:
        freelancer = Room.objects.get(name = prj_name, created_by_id= request.user.id)
        if freelancer:
            url = reverse('project_chat', kwargs={'unique_code': freelancer.unique_code})
            return HttpResponseRedirect(url)
        else:
            print("dddddd--->")
    except Exception as error:
        freelancer=Room.objects.create(name=prj_name,created_by=user,chatType='is_chat')
        freelancer.save()
        freelancer.users.set(users_list_data)
        freelancer.save()
        url = reverse('project_chat', kwargs={'unique_code': freelancer.unique_code})
        return HttpResponseRedirect(url)
    
    # try:
    #     freelancer = Room.objects.get(name = prj_name)
    #     url = reverse('group_chat', kwargs={'id': freelancer.id})
    #     return HttpResponseRedirect(url)
    # except Exception as error:
    #     print(error)
       
    # return redirect("chat-index")

