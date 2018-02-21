""" Multimeter urls """
from django.urls import path
from django.contrib.auth.views import logout_then_login

from . import views

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('logout/', logout_then_login, name='logout'),
    path('', views.index_page, name='index'),
    path('account/', views.account_page, name='account'),
    path('password/', views.password_page, name='password'),

    path('contest/list/', views.ContestList.as_view(), name='contest_list'),
    path('contest/create/', views.ContestCreate.as_view(), name='contest_create'),
    path('contest/update/<int:pk>/', views.ContestUpdate.as_view(), name='contest_update'),
    path('contest/delete/<int:pk>/', views.ContestDelete.as_view(), name='contest_delete'),

    path('problem/list/', views.ProblemList.as_view(), name='problem_list'),
    path('problem/create/', views.ProblemCreate.as_view(), name='problem_create'),
    path('problem/update/<int:pk>/', views.ProblemUpdate.as_view(), name='problem_update'),
    path('problem/delete/<int:pk>/', views.ProblemDelete.as_view(), name='problem_delete'),

    path('subtask/create/<int:task_id>/', views.SubTaskCreate.as_view(), name='subtask_create'),
    path('subtask/update/<int:pk>/', views.SubTaskUpdate.as_view(), name='subtask_update'),
    path('subtask/delete/<int:pk>/', views.SubTaskDelete.as_view(), name='subtask_delete'),
]
