from django.urls import path
from . import views
from users.google_oauth import GoogleLoginAPIView


urlpatterns = [
    path('registration/', views.RegistrationAPIView.as_view()),
    path('authorization/', views.AuthorizationAPIView.as_view()),
    path('confirm/', views.ConfirmUserAPIView.as_view()),

    path("google-login/", GoogleLoginAPIView.as_view()),


]