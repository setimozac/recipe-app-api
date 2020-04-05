from django.urls import path

from users import views


app_name = 'users'

urlpatterns = [
    path('create/', views.CreateUsersView.as_view(), name='create'),
    path('token/', views.AuthTokenView.as_view(), name='token'),
]
