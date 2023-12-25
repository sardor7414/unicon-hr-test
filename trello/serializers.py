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
    member = MemberSerializer()
    task_name = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()

    class Meta:
        model = Todo
        fields = ('id', 'created_at', 'member', 'organization', 'task_name', 'district_name', 'location', 'photo')

    def get_task_name(self, instance):
        # Fetch 'name' directly from the associated Task object
        return instance.task.name if instance.task else None

    def get_district_name(self, instance):
        # Fetch 'name' directly from the associated District object in Member
        return instance.member.district.name if instance.member and instance.member.district else None

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Fetch 'full_name' directly from the associated Member object
        member_full_name = instance.member.full_name if instance.member else None
        representation['member']['full_name'] = member_full_name

        return representation

