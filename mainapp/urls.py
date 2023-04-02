from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.urls import re_path

from django.contrib import admin
from mainapp.views import *

count = 0
urlpatterns = [

    path('account/register/',views.user_register,name='register'),
    path('home/',views.product_filters,name="home"),
    path('',views.index,name="index"),
    path('success_url',views.success_func,name="success"),
    path('verification',views.verify_email,name='verify'),
    path('profiletype',views.profile_type,name='profiletype'),
    path('account/login/',views.Login,name='login'),
    path('client_home/',views.client_home,name='client_home'),
    path('account/logout/',views.signout,name='logout'),
    path('information/add/',views.seller_form_view,name='selleradd'),
    path('user/add/',views.buyer_form_view,name='buyeradd'),
    path('create/postjob/',views.post_job_view,name='sellerpostjob'),
    path('user/applyjob/',views.apply_job_view,name='buyerapplyjob'),
    path('user/applyjobform/<slug:slug>/',views.apply_job_form_view,name='buyerapplyjobform'),
    path('alllistjobs/',views.listjobs,name='listjobs'),
    path('job/job_detail/<slug:slug>/',views.job_detail,name='job_detail'),
    path('user/details/<int:id>/',views.buyer_details_view,name='buyerdetails'),
    path('user/proposals/',views.proposals_list,name='proposals'),
    path('accounts/profile/',views.google_user_redirect_view,name='google_seller_buyer'),
    path('job/job_update_form/<slug:slug>',views.seller_job_update_form,name='seller_job_update_form'),
    path('user/bid_update_form/<int:id>/<slug:slug>',views.apply_job_update_view,name='bid_job_update_form'),
    path('delete/<slug:slug>/',views.delete_job.as_view(),name='delete_job'),
    path('successd',views.successd,name="successd"),
    path('error',views.Error,name='error'),
    path('accept_proposal/<int:id>',views.accept_proposal,name='acceptprop'),
    path('user_profile/',views.buyer_profile_update_form,name='profile_update'),
    path('payments/',views.All_Payments,name='pay'),
    path('profile/',views.seller_profile_update_form,name='seller_update'),
    path('notifications',views.notifications,name='notifications'),
    path('paymentfetch/<int:bid_obj>',views.payment,name='paymentfetch'),
    path('notification/markasread/<str:slug>',views.mark_as_read,name='notification_mark_read'),
    path('notification/delete/<str:slug>',views.delete_notification,name='notification_delete'),
    path('jobfilters/',views.onlyfilters,name='jobfilter'),
    path('edit_profileuser/',views.buyer_profile_edit_form,name='edit_profileuser'),
    path('client_project_det/<int:id>/',views.client_page_det,name='client_page_det'),
    path('save/<int:id>',views.save_job,name='savejob'),
    path('reject/<int:id>',views.reject_job,name='rejectjob'),
    path('proposal/<int:id>',views.view_proposal, name='proposal'),
    path('delete/<int:id>',views.reject_job, name='delete'),
    path('forgetpassword/',views.forgetpassword,name='forgetpassword'),
    path('setpassword/',views.resetnewpassword,name='setpassword'),
    path('verifyforget/',views.verify_forget_email,name='verifyforget'),
    path('project/report/<int:id>/',views.projectreport,name='projectreport'),
    path('freelancer/project/report/<int:id>',views.projectreportfreelancer,name="freelancerprojectreport"),
    path("all/project/",views.allprojectfreelancer, name="projectfreelancer"),
    path("complete/project/",views.completejob, name="completeproject"),
    path("progress/project/",views.in_progress_project, name="progressproject"),
    path("pending/project/",views.pending_project, name="pendingproject"),
    path("reject/project/",views.reject_project, name="rejectproject"),
    path("client_all/project/",views.clientproject, name="clientallproject"),
    path("client_complete/project/",views.clientprojectcomplete,name="completeclientproject"),
    path("client_progress/project/",views.clientprojectprogress,name="progressclientproject"),
    path("client_archived/project/",views.clientprojectarchivedproject,name="archivedclientproject"),
    path("client_unassigned/project/",views.clientprojectunassigned,name="unassignedclientproject"),
    path('project/group/<int:id>',views.create_group_name, name="projectgroup"),


####
    path('login/',views.UserLoginView.as_view()),
    path('profileapi/',views.ProfileApi.as_view()),
    path('biddingprofile/',views.BidAmountApi.as_view()),
    path('sellerprofile/',views.SellerProfileAPI.as_view()),
    path('sellerprofileid/<int:id>',views.SellerProfileIdAPI.as_view()),
    path('buyerprofile/',views.BuyerProfileAPI.as_view()),
    path('buyerprofileid/<int:id>',views.BuyerProfileIdAPI.as_view()),
    path('projectbilling/',views.ProjectBillingAPI.as_view()),
    path('projectbill/<int:id>',views.ProjectBill.as_view()),
    path('projectbillingid/<int:id>',views.ProjectBillingIDAPI.as_view()),
    path('jobiddata/<int:id>',views.JobIdData.as_view()),
    # new templates create
    path('alljob/',views.project_list,name='alljob'),
    # path('buyer/home/',views.product_filters,name='homepage'),
    path('productdetail/<int:id>',views.productdetails,name='productdetail'),
    path('notification/',views.notificationsbuyer,name='notification'),
    path('notification/markasread/<str:slug>',views.Mark_all_as_read,name='notification_all_mark_read'),
    path('user/notification/',notificationsseller,name='usernotification'),
   
    
    
   
   
   #django channels
    
    # new code on custom Admin
    path('custom-admin',views.custom_admin,name='admin_page'),
    path('dd',views.Block_Unblock,name='testt'),
    path("test",views.aadmin,name='aadmin'),
    path("tables",views.table,name='tab'),
    path("client-jobs",views.All_jobs,name='jobs'),
    path("payment-page",views.custom_payment,name = 'pay'),
    path("biddings",views.custom_biding_UI,name = 'bid'),
    # path('chat/', views.index_view, name='chat-index'),
    # path('chat/<str:room_name>/', views.room_view, name='chat-room'),
    # path('chat/', views.private_chat_home, name='chat-index'),
    # path('chat/<str:username>/', views.chatPage, name='chat-room'),
    # path('image/send/',views.Image,name='imageupload')
    
    
    # pagination urls
    
    

]


 