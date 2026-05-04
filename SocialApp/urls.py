from django.urls import path
from . import views

urlpatterns = [
    path('register/' , views.register_view , name='register'),
    path('login/' , views.login_view , name='login'),
    path('logout/' , views.logout_view , name='logout'),
    path('' , views.home_required , name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/change-password/', views.change_password_view, name='change_password'),
    path('settings/delete-account/', views.delete_account_view, name='delete_account')

    
]
