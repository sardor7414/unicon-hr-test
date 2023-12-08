from rest_framework import generics, status
from .models import Region, District, Member, Task, Todo
from rest_framework.viewsets import ModelViewSet
from .serializers import RegionSerializer, DistrictSerializer, MemberSerializer, TaskSerializer, TodoSerializer
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


class TodoViewSetAPI(ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer


class GetTodoByTelegramID(APIView):
    serializer_class = TodoSerializer

    def get(self, request, telegram_id, *args, **kwargs):
        # Siz bu qismni o'zgartirib, kerakli filtratsiyani qo'shishingiz mumkin
        member_todos = Todo.objects.filter(member__telegram_id=telegram_id).order_by('-id')[:3]
        serializer = TodoSerializer(member_todos, many=True)
        return Response(serializer.data)


# Regionlar bo'yicha bajarilgan ishlar uchu filter
def get_todo_counts_by_period(period):
    today = datetime.now().date()
    this_week_start = today - timedelta(days=today.weekday())
    this_month_start = today.replace(day=1)

    region_todo_counts = Region.objects.annotate(
        todo_count=Count('district__member__todo', filter=Q(district__member__todo__created_at__date=today))
        if period == 'today' else
        Count('district__member__todo', filter=Q(district__member__todo__created_at__date__gte=this_week_start))
        if period == 'this_week' else
        Count('district__member__todo', filter=Q(district__member__todo__created_at__date__gte=this_month_start))
    )

    result = [
        {'region': region.name, 'todo_count': region.todo_count}
        for region in region_todo_counts
    ]
    return result


# Regionlar bo'yicha bajarilgan ishlar
class RegionTodoCount(APIView):
    def get(self, request, *args, **kwargs):
        period = request.query_params.get('period', None)
        if period not in ['today', 'this_week', 'this_month']:
            return Response({'error': 'Invalid period'})

        result = get_todo_counts_by_period(period)
        return Response(result)



# Bitta Regionga tegishli tumanlar hisoboti ushun filter
def get_todo_counts_by_period_for_region(region_id, period):
    today = datetime.now().date()
    this_week_start = today - timedelta(days=today.weekday())
    this_month_start = today.replace(day=1)

    district_todo_counts = District.objects.filter(region_id=region_id).annotate(
        todo_count=Count('member__todo', filter=Q(member__todo__created_at__date=today))
        if period == 'today' else
        Count('member__todo', filter=Q(member__todo__created_at__date__gte=this_week_start))
        if period == 'this_week' else
        Count('member__todo', filter=Q(member__todo__created_at__date__gte=this_month_start))
    )

    result = [
        {'district': district.name, 'todo_count': district.todo_count}
        for district in district_todo_counts
    ]

    return result

# Bitta Regionga tegishli tumanlar hisoboti
class RegionTodoDistrictCount(APIView):
    def get(self, request, *args, **kwargs):
        region_id = self.request.query_params.get('region_id', None)
        period = self.request.query_params.get('period', None)

        if not region_id or not period or period not in ['today', 'this_week', 'this_month']:
            return Response({'error': 'Invalid parameters'})

        result = get_todo_counts_by_period_for_region(region_id, period)
        return Response(result)

# Bitta tumandagi xodimlar hisoboti uchun filter
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
            region_data = {'region': region.name, 'counts': {}}

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
            district_data = {'district': district.name, 'counts': {}}

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
        except Member.DoesNotExist:
            return Response({'error': 'District not found'}, status=404)

        result = {'district_id': district_id, 'members': []}

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


