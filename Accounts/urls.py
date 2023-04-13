from . import views
from django.urls import path, include
from dj_rest_auth.views import LogoutView,LoginView,PasswordChangeView

urlpatterns = [

    path('phones/',views.PhoneView.as_view(),name='phones_view'),
    path('phones/change/', views.SubmitChangePhoneNumber.as_view(), name='change_phone'),

    path('send_otp/', views.SendPhoneOTP.as_view(),name='sent_otp'),
    path('validate_otp/', views.ValidateOTP.as_view(),name='validate_otp'),
    path('register/', views.Register.as_view(),name='register_otp'),
    path('login/', views.DefaultLoginView.as_view(), name='login_otp'),
    path('login-phone/', views.PhoneLoginView.as_view(), name='login_phone_otp'),
    path('logout/', LogoutView.as_view(),name='logout_otp'),
    path('change_password/', PasswordChangeView.as_view(),name='change_password_otp'),

    path('user_profile/', views.ProfileView.as_view(),name='user_profile_otp'),

    path('forgot_password_otp/', views.ForgotPasswordOTP.as_view(), name='forgot_password_otp'),
    path('validate_forgot_password_otp/', views.ValidateForgotPasswordOTP.as_view(), name='validate_forgot_password_otp'),
    path('change_password_otp/', views.ForgotPasswordChange.as_view(),name='change_forgot_password_otp'),

    path('team/',views.UserView.as_view(),name='users_view'),
    path('profiles/<int:pk>/',views.ProfileDetailView.as_view(),name='profiles_view'),

]
