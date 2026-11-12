from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsSupportAgent
from .models import AgentProfile
from .serializers import AgentProfileSerializer
from .permissions import IsAgentManagementStaff


class AgentProfileView(APIView):
    permission_classes = [IsAuthenticated, IsSupportAgent]

    def get(self, request):
        profile, created = AgentProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'employee_id': f"AGENT-{request.user.id}"
            }
        )

        serializer = AgentProfileSerializer(profile)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request):
        profile, created = AgentProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'employee_id': f"AGENT-{request.user.id}"
            }
        )

        serializer = AgentProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class AgentListView(APIView):
    permission_classes = [IsAuthenticated, IsAgentManagementStaff]

    def get(self, request):
        agents = AgentProfile.objects.select_related('user').all()

        serializer = AgentProfileSerializer(
            agents,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class AgentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAgentManagementStaff]

    def get(self, request, pk):
        agent = get_object_or_404(
            AgentProfile.objects.select_related('user'),
            pk=pk
        )

        serializer = AgentProfileSerializer(agent)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )