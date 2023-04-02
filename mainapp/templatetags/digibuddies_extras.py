from django import template
from mainapp.models import User
register = template.Library()
from notifications.signals import notify
from mainapp.models import *



@register.filter()
def appliedbyme(idd,reqid):
    user = User.objects.get(pk=reqid)
    buyer = BuyerProfileModel.objects.get(user=user)
    try:
        applied_by_user = ApplyForJobModel.objects.get(buyer=buyer,applied_job_id=idd)
        return True
    except:
        return False
    

@register.filter
def mydata(datee,idd):
    bidamount = BidAmountModel.objects.get(id=idd) 
    return ProjectBillingModel.objects.filter(user=bidamount.bidder.user,duration=datee).order_by('duration')
        
    
@register.filter
def mytime(datee,idd):
    bidamount = BidAmountModel.objects.get(id=idd) 
    return ProjectBillingModel.objects.filter(user=bidamount.bidder.user,duration=datee).order_by('duration')
        


    
