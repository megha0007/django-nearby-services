__author__ = "Megha Shinde"
__date__ = "16-02-2026"
__lastupdatedby__ = "Megha Shinde"
__lastupdateddate__ = "18-02-2026"

from django.urls import path
from .views import (
    RegisterView,
    ServiceCreateView,
    ServiceListView,
    ServiceDetailView,
    ServiceUpdateView,
    ServiceDeleteView,
    NearbyServiceView,
    UpdateUserRoleView,
    AdminCreateUserView,
    ToggleUserStatusView,
    UserListView,
    ActivityLogListView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),

    path('services/', ServiceListView.as_view(), name='service-list'),
    path('services/create/', ServiceCreateView.as_view(), name='service-create'),
    path('services/<int:pk>/', ServiceDetailView.as_view(), name='service-detail'),
    path('services/<int:pk>/update/', ServiceUpdateView.as_view(), name='service-update'),
    path('services/<int:pk>/delete/', ServiceDeleteView.as_view(), name='service-delete'),
    path("users/<int:pk>/update-role/", UpdateUserRoleView.as_view(), name="update-role"),
    path("admin/create-user/", AdminCreateUserView.as_view(), name="admin-create-user"),
    path("users/<int:pk>/disable/", ToggleUserStatusView.as_view(), name="disable-user"),
    path("users/", UserListView.as_view(), name="user-list"),
    path('nearby/', NearbyServiceView.as_view(), name='nearby-services'),
    path('activity-logs/', ActivityLogListView.as_view(), name='activity-logs'),
]
