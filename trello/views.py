from rest_framework import generics, status, viewsets
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


class RegionStatsViewSet(viewsets.GenericViewSet):
    serializer_class = RegionSerializer
    queryset = Region.objects.all()

    def get(self, request, *args, **kwargs):
        # Filterlarni olish
        period = request.query_params.get('period', 'today')
        daily_plan = int(request.query_params.get('daily_plan', 1))

        # Regionlar ro'yxati
        regions = Region.objects.annotate(
            count_district=Count('district', distinct=True),
            member_count=Count('member', distinct=True)
        )

        # Har bir Region uchun count_per_interval va todo_countlar
        result = []
        total_results = {
            'region': 'Total',
            'count_district': 0,
            'member_count': 0,
            'count_per_interval': 0,
            'todo_count': 0,
            'percentage': 0,
            'difference': 0,
        }
        for region in regions:
            # Datelarni olish
            today_date = datetime.now().date()
            yesterday_date = today_date - timedelta(days=1)
            this_week_date = today_date - timedelta(days=datetime.now().weekday())
            this_month_date = today_date.replace(day=1)

            # Filterlarni tayyorlash
            period_filters = {
                'today': Q(created_at__date=today_date),
                'yesterday': Q(created_at__date=yesterday_date),
                'this_week': Q(created_at__date__gte=this_week_date),
                'this_month': Q(created_at__date__gte=this_month_date),
            }

            # Har bir period uchun this_week_days ni aniqlash
            if period == 'today':
                this_week_days = 1
            elif period == 'yesterday':
                this_week_days = 1
            elif period == 'this_week':
                this_week_days = (today_date - this_week_date).days + 1
            elif period == 'this_month':
                this_week_days = (today_date - this_month_date).days + 1

            count_per_interval = daily_plan * region.member_count * this_week_days

            # Todolarni sanash
            todo_count = Todo.objects.filter(
                Q(member__district__region=region) & period_filters[period]
            ).count()

            # Foizlar va farqlar
            percentage = (todo_count / count_per_interval) * 100 if count_per_interval > 0 else 0
            difference = todo_count - count_per_interval

            total_results['count_district'] += region.count_district
            total_results['member_count'] += region.member_count
            total_results['count_per_interval'] += count_per_interval
            total_results['todo_count'] += todo_count
            total_results['difference'] += difference

            result.append({
                'region': region.name,
                'count_district': region.count_district,
                'member_count': region.member_count,
                'count_per_interval': count_per_interval,
                'todo_count': todo_count,
                'percentage': f"{round(percentage, 1)}%",
                'difference': difference,
            })

        result.append(total_results)
        return Response(result)



class DistrictStatsByRegion(viewsets.GenericViewSet):
    serializer_class = RegionSerializer
    queryset = Region.objects.all()

    def list(self, request, *args, **kwargs):
        # Filterlarni olish
        period = request.query_params.get('period', 'today')
        daily_plan = int(request.query_params.get('daily_plan', 1))
        region_id = kwargs.get('region_id')  # Region ID ni olish

        try:
            # Regionlarni aniqlash
            region = Region.objects.get(id=region_id)
        except Region.DoesNotExist:
            return Response({'error': 'Region not found'}, status=status.HTTP_404_NOT_FOUND)

        # Har bir period uchun this_week_days ni aniqlash
        if period == 'today':
            this_week_days = 1
            today_date = datetime.now().date()
            yesterday_date = today_date - timedelta(days=1)
            this_week_date = today_date
            this_month_date = today_date.replace(day=1)
        elif period == 'yesterday':
            this_week_days = 1
            today_date = datetime.now().date()
            yesterday_date = today_date - timedelta(days=1)
            this_week_date = today_date
            this_month_date = today_date.replace(day=1)
        elif period == 'this_week':
            this_week_days = datetime.now().weekday() + 1
            today_date = datetime.now().date()
            yesterday_date = today_date - timedelta(days=1)
            this_week_date = today_date - timedelta(days=datetime.now().weekday())
            this_month_date = today_date.replace(day=1)
        elif period == 'this_month':
            this_week_days = (datetime.now().date() - datetime.now().replace(day=1).date()).days + 1
            today_date = datetime.now().date()
            yesterday_date = today_date - timedelta(days=1)
            this_week_date = today_date - timedelta(days=datetime.now().weekday())
            this_month_date = today_date.replace(day=1)

        # Districtlar ro'yxati
        districts = region.district_set.annotate(
            member_count=Count('member', distinct=True)
        )

        # Har bir District uchun count_per_interval va todo_countlar
        result = []
        total_results = {
            'region': region.name,
            'count_district': 0,
            'member_count': 0,
            'count_per_interval': 0,
            'todo_count': 0,
            'percentage': 0,
            'difference': 0,
        }
        for district in districts:
            # Filterlarni tayyorlash
            period_filters = {
                'today': Q(created_at__date=today_date),
                'yesterday': Q(created_at__date=yesterday_date),
                'this_week': Q(created_at__date__gte=this_week_date),
                'this_month': Q(created_at__date__gte=this_month_date),
            }

            count_per_interval = daily_plan * district.member_count * this_week_days

            # Todolarni sanash
            todo_count = Todo.objects.filter(
                Q(member__district=district) & period_filters[period]
            ).count()

            # Foizlar va farqlar
            percentage = (todo_count / count_per_interval) * 100 if count_per_interval > 0 else 0
            difference = todo_count - count_per_interval

            total_results['count_district'] += 1
            total_results['member_count'] += district.member_count
            total_results['count_per_interval'] += count_per_interval
            total_results['todo_count'] += todo_count
            total_results['difference'] += difference

            result.append({
                'district': district.name,
                'member_count': district.member_count,
                'count_per_interval': count_per_interval,
                'todo_count': todo_count,
                'percentage': f"{round(percentage, 1)}%",
                'difference': difference,
            })

        result.append(total_results)
        return Response(result)


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


