from django.urls import path

from . import views

urlpatterns = [
    path('', views.getDatanew, name='getDatanew'),
    path('submit-email/', views.submit_email, name='submit-email'),
    path('get-profiles/<str:email>/', views.get_profiles, name='get-profiles'),
    path('get-profile-details/<str:email>/<str:profile_name>/',
         views.get_profile_details, name='get-profile-details'),
]
