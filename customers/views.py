from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsCustomer
from .models import CustomerProfile
from .serializers import CustomerProfileSerializer
from django.shortcuts import get_object_or_404
from .permissions import IsCustomerManagementStaff


class CustomerProfileView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request):
        profile, created = CustomerProfile.objects.get_or_create(
            user=request.user
        )

        serializer = CustomerProfileSerializer(profile)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request):
        profile, created = CustomerProfile.objects.get_or_create(
            user=request.user
        )

        serializer = CustomerProfileSerializer(
            profile,
            data=request.data
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

    def patch(self, request):
        profile, created = CustomerProfile.objects.get_or_create(
            user=request.user
        )

        serializer = CustomerProfileSerializer(
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
class CustomerListView(APIView):
    permission_classes = [IsAuthenticated, IsCustomerManagementStaff]

    def get(self, request):
        customers = CustomerProfile.objects.select_related('user').all()

        serializer = CustomerProfileSerializer(
            customers,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CustomerDetailView(APIView):
    permission_classes = [IsAuthenticated, IsCustomerManagementStaff]

    def get(self, request, pk):
        customer = get_object_or_404(
            CustomerProfile.objects.select_related('user'),
            pk=pk
        )

        serializer = CustomerProfileSerializer(customer)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )