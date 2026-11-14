
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Ticket, TicketHistory
from .serializers import TicketSerializer

User = get_user_model()


class TicketListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    # Customer history and staff ticket viewing
    def get(self, request):

        role = request.user.role

        if role == 'CUSTOMER':
            tickets = Ticket.objects.filter(
                customer=request.user
            )

        elif role == 'SUPPORT_AGENT':
            tickets = Ticket.objects.filter(
                assigned_agent=request.user
            )

        elif role in ['ADMIN', 'TEAM_LEAD']:
            tickets = Ticket.objects.all()

        else:
            return Response(
                {"message": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TicketSerializer(
            tickets.order_by('-created_at'),
            many=True
        )

        return Response(serializer.data)

    # Customer complaint submission
    def post(self, request):

        if request.user.role != 'CUSTOMER':
            return Response(
                {"message": "Only customers can create tickets."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TicketSerializer(data=request.data)

        if serializer.is_valid():

            ticket = serializer.save(customer=request.user)

            TicketHistory.objects.create(
                ticket=ticket,
                changed_by=request.user,
                action='TICKET_CREATED',
                new_value=ticket.ticket_id
            )

            return Response(
                TicketSerializer(ticket).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class TicketStaffListView(APIView):

    permission_classes = [IsAuthenticated]

    # Search and filter tickets
    def get(self, request):

        role = request.user.role

        if role == 'SUPPORT_AGENT':
            tickets = Ticket.objects.filter(
                assigned_agent=request.user
            )

        elif role in ['ADMIN', 'TEAM_LEAD']:
            tickets = Ticket.objects.all()

        else:
            return Response(
                {"message": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN
            )

        search = request.query_params.get('search')
        ticket_status = request.query_params.get('status')
        priority = request.query_params.get('priority')
        category = request.query_params.get('category')

        if search:
            tickets = tickets.filter(
                Q(ticket_id__icontains=search) |
                Q(subject__icontains=search) |
                Q(description__icontains=search)
            )

        if ticket_status:
            tickets = tickets.filter(
                status=ticket_status.upper()
            )

        if priority:
            tickets = tickets.filter(
                priority=priority.upper()
            )

        if category:
            tickets = tickets.filter(
                category_id=category
            )

        serializer = TicketSerializer(
            tickets.order_by('-created_at'),
            many=True
        )

        return Response(serializer.data)


class TicketStaffDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Ticket, pk=pk)

    # View ticket details
    def get(self, request, pk):

        ticket = self.get_object(pk)
        role = request.user.role

        if role == 'SUPPORT_AGENT':

            if ticket.assigned_agent_id != request.user.id:
                return Response(
                    {"message": "This ticket is not assigned to you."},
                    status=status.HTTP_403_FORBIDDEN
                )

        elif role not in ['ADMIN', 'TEAM_LEAD']:
            return Response(
                {"message": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN
            )

        return Response(
            TicketSerializer(ticket).data
        )

    # Assign ticket and update priority/status
    def patch(self, request, pk):

        ticket = self.get_object(pk)
        role = request.user.role

        if role == 'SUPPORT_AGENT':

            if ticket.assigned_agent_id != request.user.id:
                return Response(
                    {"message": "This ticket is not assigned to you."},
                    status=status.HTTP_403_FORBIDDEN
                )

        elif role not in ['ADMIN', 'TEAM_LEAD']:
            return Response(
                {"message": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Store old values before updating
        old_priority = ticket.priority
        old_status = ticket.status
        old_agent = ticket.assigned_agent_id

        allowed_fields = {
            'assigned_agent',
            'priority',
            'status'
        }

        if not request.data:
            return Response(
                {"message": "No update data provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        invalid_fields = set(request.data.keys()) - allowed_fields

        if invalid_fields:
            return Response(
                {
                    "message": "Invalid fields: " +
                    ", ".join(invalid_fields)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Assign support agent
        if 'assigned_agent' in request.data:

            if role not in ['ADMIN', 'TEAM_LEAD']:
                return Response(
                    {
                        "message":
                        "Only Admin or Team Lead can assign tickets."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            agent_id = request.data['assigned_agent']

            if agent_id is None:
                ticket.assigned_agent = None

            else:
                agent = User.objects.filter(
                    id=agent_id,
                    role='SUPPORT_AGENT'
                ).first()

                if not agent:
                    return Response(
                        {"message": "Invalid support agent ID."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                ticket.assigned_agent = agent

        # Update priority
        if 'priority' in request.data:

            priority = request.data['priority']

            if not isinstance(priority, str):
                return Response(
                    {"message": "Invalid priority."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            priority = priority.upper()

            if priority not in Ticket.Priority.values:
                return Response(
                    {"message": "Invalid priority."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ticket.priority = priority

        # Update ticket status
        if 'status' in request.data:

            ticket_status = request.data['status']

            if not isinstance(ticket_status, str):
                return Response(
                    {"message": "Invalid ticket status."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ticket_status = ticket_status.upper()

            if ticket_status not in Ticket.Status.values:
                return Response(
                    {"message": "Invalid ticket status."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ticket.status = ticket_status

        ticket.save()

        # Record priority changes
        if old_priority != ticket.priority:

            TicketHistory.objects.create(
                ticket=ticket,
                changed_by=request.user,
                action='PRIORITY_UPDATED',
                old_value=old_priority,
                new_value=ticket.priority
            )

        # Record status changes
        if old_status != ticket.status:

            TicketHistory.objects.create(
                ticket=ticket,
                changed_by=request.user,
                action='STATUS_UPDATED',
                old_value=old_status,
                new_value=ticket.status
            )

        # Record agent assignment changes
        if old_agent != ticket.assigned_agent_id:

            TicketHistory.objects.create(
                ticket=ticket,
                changed_by=request.user,
                action='AGENT_ASSIGNED',
                old_value=str(old_agent),
                new_value=str(ticket.assigned_agent_id)
            )

        return Response(
            TicketSerializer(ticket).data,
            status=status.HTTP_200_OK
        )


class TicketHistoryView(APIView):

    permission_classes = [IsAuthenticated]

    # View ticket history
    def get(self, request, pk):

        ticket = get_object_or_404(Ticket, pk=pk)
        role = request.user.role

        if role == 'CUSTOMER':

            if ticket.customer_id != request.user.id:
                return Response(
                    {"message": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN
                )

        elif role == 'SUPPORT_AGENT':

            if ticket.assigned_agent_id != request.user.id:
                return Response(
                    {
                        "message":
                        "This ticket is not assigned to you."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

        elif role not in ['ADMIN', 'TEAM_LEAD']:
            return Response(
                {"message": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN
            )

        history = ticket.history.select_related(
            'changed_by'
        )

        data = [
            {
                'action': item.action,
                'old_value': item.old_value,
                'new_value': item.new_value,
                'changed_by': (
                    item.changed_by.username
                    if item.changed_by else None
                ),
                'created_at': item.created_at
            }
            for item in history
        ]

        return Response(
            data,
            status=status.HTTP_200_OK
        )
