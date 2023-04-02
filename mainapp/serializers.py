from rest_framework import serializers
from mainapp.models import *




# class userserializer(serializers.ModelSerializer):
#     class Meta:
#         model= User
#         fields=['email','first_name','last_name','is_active','is_admin','is_seller','is_buyer','is_verified','is_online']


class UserLoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField()
    class Meta:
        model=User
        fields = ('email','password')

class ProfileApiSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = ('email','first_name','last_name')

class BidAmountSearializer(serializers.ModelSerializer):
    class Meta:
        model=BidAmountModel
        fields = ('job','bidder','bid_amount','is_accepted','pitch')
        depth = 1


# ------------ create nested serializer for seller ------------
# class CustomUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields=['first_name']

# class CustomSellerProfileSerializer(serializers.ModelSerializer):
#     user = CustomUserSerializer()
#     class Meta:
#         model=SellerProfileModel
#         fields = ['user']

# class CustomPostJobModels(serializers.ModelSerializer):
#     seller = CustomSellerProfileSerializer()
#     class Meta:
#         model = PostjobModel
#         fields = ['seller']

# class CustomBidAmount(serializers.ModelSerializer):
#     # job = CustomPostJobModels()
#     class Meta:
#         model=BidAmountModel
#         fields = ['job','bidder','bid_amount','is_accepted','pitch']



class SellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=SellerProfileModel
        fields = '__all__'
        depth = 1


class MycustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = ['first_name']

class MyCusotomSellerProfileSerializer(serializers.ModelSerializer):
    user = MycustomUserSerializer()
    class Meta:
        model=SellerProfileModel
        fields = ['user']

class MyCusotomPost_Job_model(serializers.ModelSerializer):
    seller = MyCusotomSellerProfileSerializer()
    class Meta:
        model=PostjobModel
        fields = ['id','seller','job_title']

class CustomBidAmount(serializers.ModelSerializer):
    job = MyCusotomPost_Job_model()

    class Meta:
        model=BidAmountModel
        fields = ['job']


class BuyerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=BuyerProfileModel
        fields = '__all__'
        depth = 1

class ApplyJobSerializer(serializers.ModelSerializer):
    class Meta:
        model=ApplyForJobModel
        fields = '__all__'

class ProjectBillingSerializer(serializers.ModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),required=True)
    
    project = serializers.PrimaryKeyRelatedField(queryset=BidAmountModel.objects.all(),required=True)
    class Meta:
        model=ProjectBillingModel
        fields = '__all__'
        

class ProjectBillingWithoutUserSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=BidAmountModel.objects.all(),required=True)
    class Meta:
        model=ProjectBillingModel   
        exclude = ['user']
        depth =1

class PostjobSerializer(serializers.ModelSerializer):
    seller = serializers.PrimaryKeyRelatedField(queryset=SellerProfileModel.objects.all,required=True)
    class Meta:
        model=PostjobModel
        fields = ['seller']
        depth = 1

