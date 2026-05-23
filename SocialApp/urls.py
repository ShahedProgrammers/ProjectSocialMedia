from django.urls import path
from . import views

urlpatterns = [
    path('register/' , views.register_view , name='register'),
    path('login/' , views.login_view , name='login'),
    path('logout/' , views.logout_view , name='logout'),
    path('' , views.home_required , name='home'),
    path('explore/', views.explore_view, name='explore'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/<int:user_id>/', views.profile_view, name='user_profile'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/change-password/', views.change_password_view, name='change_password'),
    path('settings/delete-account/', views.delete_account_view, name='delete_account'),
    path('posts/create/', views.create_post_view, name='create_post'),
    path('posts/<int:post_id>/edit/', views.create_post_view, name='edit_post'),
    path('posts/<int:post_id>/delete/', views.delete_post_view, name='delete_post'),
    path('posts/<int:post_id>/comments/', views.post_comments_view, name='post_comments'),
    path('posts/<int:post_id>/like/', views.toggle_like_view, name='toggle_like'),
]
