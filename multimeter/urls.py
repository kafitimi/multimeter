from django.urls import path
from django.contrib.auth.views import logout_then_login

from multimeter import views

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('logout/', logout_then_login, name='logout'),
    path('', views.index_page, name='index'),
    path('account/', views.account_page, name='account'),
    path('password/', views.password_page, name='password'),

    path('contest/list/', views.contest_list, name='contest_list'),
    path('contest/add/', views.contest_edit, name='contest_add'),
    path('contest/edit/<int:contest_id>/', views.contest_edit, name='contest_edit'),

    path('problem/list/', views.problem_list, name='problem_list'),
    path('problem/add/', views.problem_edit, name='problem_add'),
    path('problem/edit/<int:problem_id>/', views.problem_edit, name='problem_edit'),
]
