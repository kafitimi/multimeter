""" Multimeter urls """
from django.urls import path
from django.contrib.auth.views import logout_then_login

from . import views

urlpatterns = [  # pylint: disable=invalid-name
    path('login/', views.login_page, name='login'),
    path('logout/', logout_then_login, name='logout'),
    path('signup/', views.SignupFormView.as_view(), name="signup"),
    path('', views.index_page, name='index'),
    path('account/', views.account_page, name='account'),
    path('password/', views.password_page, name='password'),

    path('contest/list/', views.ContestList.as_view(), name='contest_list'),
    path('contest/create/', views.ContestCreate.as_view(), name='contest_create'),
    path('contest/update/<int:pk>/', views.ContestUpdate.as_view(), name='contest_update'),
    path('contest/delete/<int:pk>/', views.ContestDelete.as_view(), name='contest_delete'),
    path('contest/<int:contest_pk>/join/', views.contest_join_page, name='contest_join'),

    path('problem/list/', views.problem_list_page, name='problem_list'),
    path('problem/create/', views.problem_edit_page, name='problem_create'),
    path('problem/update/<int:problem_id>/', views.problem_edit_page, name='problem_update'),
    path('problem/delete/<int:pk>/', views.ProblemDelete.as_view(), name='problem_delete'),
    path('problem/import/', views.problem_import, name='problem_import'),
    path('problem/update/<int:pk>/statements/<str:lang>',
         views.problem_statements_form_page, name='problem_statements'),
    path('problem/update/<int:pk>/statements/<str:lang>/delete',
         views.problem_statements_delete_page, name='problem_statements_delete'),

    path('subtask/create/<int:problem_id>/', views.SubTaskCreate.as_view(), name='subtask_create'),
    path('subtask/update/<int:pk>/', views.SubTaskUpdate.as_view(), name='subtask_update'),
    path('subtask/delete/<int:pk>/', views.SubTaskDelete.as_view(), name='subtask_delete'),
]
