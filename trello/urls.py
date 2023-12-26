from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (RegionViewAPI, DistrictViewSetAPI, MemberViewSetAPI, CheckUserTelegramIDAPI, TaskViewSetAPI,
                    TodoViewSetAPI, GetTodoByTelegramID, RegionStatsViewSet, DistrictStatsByRegion, DistrictTodoMemberCount,
                    TaskTodoCount, TodoCountView, RegionTodoCountView, DistrictMemberTodoCountView,CreateTodo)



router = DefaultRouter()
router.register('regions', RegionViewAPI)
router.register('district', DistrictViewSetAPI)
router.register('member', MemberViewSetAPI)
router.register('task', TaskViewSetAPI)
router.register('todo', TodoViewSetAPI)


urlpatterns = [
    path('', include(router.urls)),
    path('checkMember/<int:telegram_id>/', CheckUserTelegramIDAPI.as_view()),
    path('getTodo/<int:telegram_id>/', GetTodoByTelegramID.as_view()),
    path('region-stats/', RegionStatsViewSet.as_view({'get': 'list'}), name='region-stat'),
    path('district-stats-by-region/', DistrictStatsByRegion.as_view({'get': 'list'}), name='district-stat-by-region'),
    path('member-count-by-district/', DistrictTodoMemberCount.as_view(), name='district-todo-count'),
    path('task-todo-count/', TaskTodoCount.as_view(), name='task-todo-count'),
    # Task lar kesimida Todos larni olish
    path('todo-count/', TodoCountView.as_view(), name='todo-count'),
    path('region-todo-count-by-task/<int:region_id>/', RegionTodoCountView.as_view(), name='region-todo-count'),
    path('district-member-todo-count/<int:district_id>/', DistrictMemberTodoCountView.as_view(),
         name='district-member-todo-count'),
    path('sardortodo/',CreateTodo.as_view())
]
