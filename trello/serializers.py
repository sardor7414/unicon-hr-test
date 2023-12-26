from rest_framework import serializers
from .models import Region, District, Member, Task, Todo
class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'name')
class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ('id', 'region', 'name', 'user')
class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('id', 'district', 'full_name', 'phone', 'user', 'telegram_id')
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'name')
class TodoSerializer(serializers.ModelSerializer):
   class Meta:
       model = Todo
       fields = '__all__'
class TodoNewSerializer(serializers.ModelSerializer):
   task = TaskSerializer()
   member  = MemberSerializer()
   class Meta:
       model = Todo
       fields = ['created_at','updated_at','organization','photo','task','member','latitude','longitude']