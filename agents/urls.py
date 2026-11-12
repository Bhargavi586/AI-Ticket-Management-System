from django.urls import path

from .views import (
    AgentProfileView,
    AgentListView,
    AgentDetailView,
)

urlpatterns = [
    # Agent's own profile
    path(
        'profile/',
        AgentProfileView.as_view(),
        name='agent-profile'
    ),

    # Admin and Team Lead APIs
    path(
        '',
        AgentListView.as_view(),
        name='agent-list'
    ),

    path(
        '<int:pk>/',
        AgentDetailView.as_view(),
        name='agent-detail'
    ),
]