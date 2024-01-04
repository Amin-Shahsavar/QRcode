from django.urls import path

from user import views


auth_urls = [
    path('register/', views.RegistartionView.as_view(), name='register'),
    path('login/', views.TokenObtainPairView.as_view(), name='login_token'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('change_password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('reset_password_check_email/', views.ResetPasswordCheckEmailView.as_view(), name='reset_password_check_email'),
    path('reset_password/<str:uidb64>/<str:token>/', views.RestPasswordView.as_view(), name='reset_password'),
    path('verify_email/<str:uidb64>/<str:token>/', views.VerifyEmailView.as_view(), name='verify_email'),
]

profile_urls = [
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update_firstname_lastname/', views.ChangeFirstNameLastNameView.as_view(), name='change_firstname_lastname'),
]

urlpatterns = auth_urls + profile_urls
