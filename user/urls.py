from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Customer storefront auth
    path('auth/login/', views.CustomerLoginView.as_view(), name='customer-login'),
    path('auth/register/', views.CustomerRegisterView.as_view(), name='customer-register'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/otp/send/', views.SendOtpView.as_view(), name='send-otp'),
    path('auth/otp/verify/', views.VerifyOtpView.as_view(), name='verify-otp'),
    path('me/', views.MeView.as_view(), name='me'),

    # Customer addresses
    path('addresses/', views.AddressListCreateView.as_view(), name='address-list-create'),
    path('addresses/<str:pk>/', views.AddressDetailView.as_view(), name='address-detail'),

    # Admin RBAC management
    path('roles/', views.RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<str:pk>/', views.RoleDetailView.as_view(), name='role-detail'),
    path('roles/<str:pk>/permissions/', views.RolePermissionBulkSetView.as_view(), name='role-permissions-bulk'),
    path('role-permissions/', views.RolePermissionListCreateView.as_view(), name='role-permission-list-create'),
    path('role-permissions/<str:pk>/', views.RolePermissionDetailView.as_view(), name='role-permission-detail'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/create/', views.UserCreateView.as_view(), name='user-create'),
    path('users/<str:pk>/', views.UserDetailView.as_view(), name='user-detail'),
]
