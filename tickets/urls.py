
from django.urls import path

from .views import (
    TicketListCreateView,
    TicketStaffListView,
    TicketStaffDetailView,
    TicketHistoryView,
)

urlpatterns = [
    path('', TicketListCreateView.as_view(), name='ticket-list-create'),

    path('staff/', TicketStaffListView.as_view(), name='staff-ticket-list'),

    path(
        'staff/<int:pk>/',
        TicketStaffDetailView.as_view(),
        name='staff-ticket-detail'
    ),

    path(
        '<int:pk>/history/',
        TicketHistoryView.as_view(),
        name='ticket-history'
    ),
]
