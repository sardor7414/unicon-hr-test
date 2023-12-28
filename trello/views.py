from rest_framework import generics, status, viewsets
from .models import Region, District, Member, Task, Todo
from rest_framework.viewsets import ModelViewSet
from .serializers import RegionSerializer, DistrictSerializer, MemberSerializer, TaskSerializer, TodoSerializer,TodoNewSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from datetime import date, datetime, timedelta
from django.db.models import Q


# Create your views here.

class RegionViewAPI(ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


class DistrictViewSetAPI(ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer

    def get_queryset(self):
        queryset = self.queryset
        region_id = self.request.query_params.get('region_id', None)

        if region_id is not None:
            queryset = queryset.filter(region_id=region_id)
        return queryset


class MemberViewSetAPI(ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

    def get_queryset(self):
        queryset = self.queryset
        district_id = self.request.query_params.get('district_id', None)

        if district_id is not None:
            queryset = queryset.filter(district_id=district_id)
        return queryset


    def partial_update(self, request, *args, **kwargs):
        data = request.data
        member = self.get_object()
        member.full_name = data.get('full_name', member.full_name)
        member.phone = data.get('phone', member.phone)
        member.telegram_id = data.get('telegram_id', member.telegram_id)
        member.district = data.get('district', member.district)
        member.save()
        serializer = MemberSerializer(member)
        return Response(serializer.data)


class CheckUserTelegramIDAPI(APIView):
    def get(self, request, telegram_id, *args, **kwargs):
        member = Member.objects.filter(telegram_id=telegram_id).first()
        if not member:
            return Response({"is_registered": False})
        return Response({"is_registered": True,
                         "member_id": member.id})


class TaskViewSetAPI(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
import json
class CreateTodo(APIView):
    def post(self,request):
        task = request.data.get('task')
        photo = request.data.get('photo')
        organization = request.data.get('organization')
        latitude  = request.data.get('latitude')
        longitude = request.data.get('longitude')
        member =request.data.get('member')
        try:
            member_id = Member.objects.get(id =int(member))
            try:
                task_id = Task.objects.get(id =int(task))
                todo = Todo.objects.create(photo=photo,task=task_id,member=member_id,organization=organization,latitude=latitude,longitude=longitude)
                serializer = TodoSerializer(todo,partial=True)
                return Response(serializer.data)
            except Task.DoesNotExist:
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Member.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)
class TodoViewSetAPI(ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoNewSerializer 
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Modify the response data to include 'full_name' directly under 'member'
        data = serializer.data
        created_at = instance.created_at
        data['created_at'] = created_at

        member_full_name = instance.member.full_name
        data['member'] = member_full_name

        return Response(data)


class GetTodoByTelegramID(APIView):
    serializer_class = TodoSerializer

    def get(self, request, telegram_id, *args, **kwargs):
        # Siz bu qismni o'zgartirib, kerakli filtratsiyani qo'shishingiz mumkin
        member_todos = Todo.objects.filter(member__telegram_id=telegram_id).order_by('-id')[:5]
        serializer = TodoSerializer(member_todos, many=True)
        return Response(serializer.data)


class RegionStatsViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def list(self, request, *args, **kwargs):
        regions = self.get_queryset()
        region_data = []

        for region in regions:
            region_dict = {'region_name': region.name}

            region_dict['region_id'] = region.id

            # 'region' ga tegishli 'district'lar soni
            region_dict['district_count'] = region.district_set.count()

            # 'region'ga tegishli 'member'lar soni
            region_dict['member_count'] = region.member_set.count()

            # 'region' ga tegishli kunlik reja
            daily_plan = request.GET.get('daily_plan', 5)
            region_dict['seminar_plan'] = int(daily_plan) * region_dict['member_count']

            # 'region' da bajarilgan ishlar soni today uchun
            today = date.today()
            region_dict['tasks_done_today'] = Todo.objects.filter(
                member__region=region,
                created_at__year=today.year,
                created_at__month=today.month,
                created_at__day=today.day
            ).count()

            # 'region' da bajarilgan ishlar soni yesterday uchun
            yesterday = today - timedelta(days=1)
            region_dict['tasks_done_yesterday'] = Todo.objects.filter(
                member__region=region,
                created_at__year=yesterday.year,
                created_at__month=yesterday.month,
                created_at__day=yesterday.day
            ).count()

            # 'region' da bajarilgan ishlar soni this_week uchun
            start_of_week = today - timedelta(days=today.weekday())
            region_dict['tasks_done_this_week'] = Todo.objects.filter(
                member__region=region,
                created_at__gte=start_of_week
            ).count()

            # 'region' da bajarilgan ishlar sonining 'region' ga tegishli kunlik reja nisbatan farqi
            region_dict['seminar_plan_difference'] = f"{round((region_dict['tasks_done_today'] / region_dict['seminar_plan']) * 100, 1)}%" \
                if region_dict['seminar_plan'] != 0 else 0

            # 'region' da bajarilgan ishlar soni yesterday uchun va today uchun farqi
            region_dict['tasks_done_difference'] = region_dict['tasks_done_today'] - region_dict['tasks_done_yesterday']

            region_data.append(region_dict)

        return Response(region_data)



class DistrictStatsByRegion(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def list(self, request, *args, **kwargs):
        # 'region_id' ni requestdan olish
        region_id = request.GET.get('region_id', None)

        # Agar 'region_id' berilgan bo'lsa, buni o'rnating, aks holda barcha 'districtlar'ni olish
        if region_id:
            districts = District.objects.filter(region_id=region_id)
        else:
            districts = District.objects.all()

        district_data = []

        for district in districts:
            district_dict = {'district_name': district.name, 'district_id': district.id}

            # 'district' ga tegishli 'member'lar soni
            district_dict['member_count'] = Member.objects.filter(district=district).count()

            # 'district' ga tegishli kunlik reja
            daily_plan = request.GET.get('daily_plan', 5)
            district_dict['seminar_plan'] = int(daily_plan) * district_dict['member_count']

            # 'district' da bajarilgan ishlar soni today uchun
            today = date.today()
            district_dict['tasks_done_today'] = Todo.objects.filter(
                member__district=district,
                created_at__year=today.year,
                created_at__month=today.month,
                created_at__day=today.day
            ).count()

            # 'district' da bajarilgan ishlar soni yesterday uchun
            yesterday = today - timedelta(days=1)
            district_dict['tasks_done_yesterday'] = Todo.objects.filter(
                member__district=district,
                created_at__year=yesterday.year,
                created_at__month=yesterday.month,
                created_at__day=yesterday.day
            ).count()

            # 'district' da bajarilgan ishlar soni this_week uchun
            start_of_week = today - timedelta(days=today.weekday())
            district_dict['tasks_done_this_week'] = Todo.objects.filter(
                member__district=district,
                created_at__gte=start_of_week
            ).count()

            # 'district' da bajarilgan ishlar sonining 'district' ga tegishli kunlik reja nisbatan farqi
            district_dict['seminar_plan_difference'] = f"{round((district_dict['tasks_done_today'] / district_dict['seminar_plan']) * 100, 1)}%" if district_dict['seminar_plan'] != 0 else 0

            # 'district' da bajarilgan ishlar soni yesterday uchun va today uchun farqi
            district_dict['tasks_done_difference'] = district_dict['tasks_done_today'] - district_dict[
                'tasks_done_yesterday']

            district_data.append(district_dict)

        return Response(district_data)


def get_todo_counts_by_period_for_district(district_id, period):
    today = datetime.now().date()
    this_week_start = today - timedelta(days=today.weekday())
    this_month_start = today.replace(day=1)

    member_todo_counts = Member.objects.filter(district_id=district_id).annotate(
        todo_count=Count('todo', filter=Q(todo__created_at__date=today))
        if period == 'today' else
        Count('todo', filter=Q(todo__created_at__date__gte=this_week_start))
        if period == 'this_week' else
        Count('todo', filter=Q(todo__created_at__date__gte=this_month_start))
    )

    result = [
        {'member': member.full_name, 'todo_count': member.todo_count}
        for member in member_todo_counts
    ]

    return result


class DistrictTodoMemberCount(APIView):
    def get(self, request, *args, **kwargs):
        district_id = self.request.query_params.get('district_id', None)
        period = self.request.query_params.get('period', None)

        if not district_id or not period or period not in ['today', 'this_week', 'this_month']:
            return Response({'error': 'Invalid parameters'})

        result = get_todo_counts_by_period_for_district(district_id, period)
        return Response(result)



def get_todo_counts_by_period_for_task(period):
    today = datetime.now().date()
    this_week_start = today - timedelta(days=today.weekday())
    this_month_start = today.replace(day=1)

    task_todo_counts = Task.objects.annotate(
        todo_count=Count('todo', filter=Q(todo__created_at__date=today))
        if period == 'today' else
        Count('todo', filter=Q(todo__created_at__date__gte=this_week_start))
        if period == 'this_week' else
        Count('todo', filter=Q(todo__created_at__date__gte=this_month_start))
    )

    result = [
        {'task': task.name, 'todo_count': task.todo_count}
        for task in task_todo_counts
    ]

    return result


class TaskTodoCount(APIView):
    def get(self, request, *args, **kwargs):
        period = self.request.query_params.get('period', None)

        if not period or period not in ['today', 'this_week', 'this_month']:
            return Response({'error': 'Invalid parameters'})
        result = get_todo_counts_by_period_for_task(period)
        return Response(result)



#
#Region Todo Count By task

class TodoCountView(APIView):
    def get(self, request):
        today = date.today()
        this_week_start = today - timedelta(days=today.weekday())
        this_month_start = today.replace(day=1)

        filter_param = request.GET.get('filter_param', 'today')  # Default to 'today'

        regions = Region.objects.all()
        result = []

        for region in regions:
            region_data = {'region_id': region.id,'region': region.name, 'counts': {}}

            tasks = Task.objects.all()
            for task in tasks:
                if filter_param == 'today':
                    todo_count = Todo.objects.filter(
                        member__region=region, task=task, created_at__date=today
                    ).count()
                elif filter_param == 'this_week':
                    todo_count = Todo.objects.filter(
                        member__region=region, task=task, created_at__gte=this_week_start
                    ).count()
                elif filter_param == 'this_month':
                    todo_count = Todo.objects.filter(
                        member__region=region, task=task, created_at__gte=this_month_start
                    ).count()
                else:
                    todo_count = 0  # Unknown filter_param value, handle accordingly
                region_data['counts'][task.name] = todo_count
            result.append(region_data)
        return Response(result)


#District Todos Count By task By Region

class RegionTodoCountView(APIView):
    def get(self, request, region_id):
        today = date.today()
        this_week_start = today - timedelta(days=today.weekday())
        this_month_start = today.replace(day=1)

        filter_param = request.GET.get('filter_param', 'today')  # Default to 'today'

        try:
            region = Region.objects.get(id=region_id)
        except Region.DoesNotExist:
            return Response({'error': 'Region not found'}, status=404)

        districts = District.objects.filter(region=region)
        result = {'region': region.name, 'districts': []}

        for district in districts:
            district_data = {'district_id': district.id, 'district': district.name, 'counts': {}}

            tasks = Task.objects.all()
            for task in tasks:
                if filter_param == 'today':
                    todo_count = Todo.objects.filter(
                        member__district=district, task=task, created_at__date=today
                    ).count()
                elif filter_param == 'this_week':
                    todo_count = Todo.objects.filter(
                        member__district=district, task=task, created_at__gte=this_week_start
                    ).count()
                elif filter_param == 'this_month':
                    todo_count = Todo.objects.filter(
                        member__district=district, task=task, created_at__gte=this_month_start
                    ).count()
                else:
                    todo_count = 0  # Unknown filter_param value, handle accordingly

                district_data['counts'][task.name] = todo_count

            result['districts'].append(district_data)

        return Response(result)



# Member Task Todos Count By District
class DistrictMemberTodoCountView(APIView):
    def get(self, request, district_id):
        today = date.today()
        this_week_start = today - timedelta(days=today.weekday())
        this_month_start = today.replace(day=1)

        filter_param = request.GET.get('filter_param', 'today')  # Default to 'today'

        try:
            members = Member.objects.filter(district_id=district_id)
            district_name = District.objects.get(id=district_id).name
        except Member.DoesNotExist:
            return Response({'error': 'District not found'}, status=404)

        result = {'district_id': district_id, 'district_name': district_name, 'members': []}

        for member in members:
            member_data = {'member_id': member.id, 'full_name': member.full_name, 'counts': {}}

            tasks = Task.objects.all()
            for task in tasks:
                if filter_param == 'today':
                    todo_count = Todo.objects.filter(
                        member=member, task=task, created_at__date=today
                    ).count()
                elif filter_param == 'this_week':
                    todo_count = Todo.objects.filter(
                        member=member, task=task, created_at__gte=this_week_start
                    ).count()
                elif filter_param == 'this_month':
                    todo_count = Todo.objects.filter(
                        member=member, task=task, created_at__gte=this_month_start
                    ).count()
                else:
                    todo_count = 0  # Unknown filter_param value, handle accordingly
                member_data['counts'][task.name] = todo_count
            result['members'].append(member_data)
        return Response(result)


