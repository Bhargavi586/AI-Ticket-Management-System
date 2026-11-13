
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Category
from .serializers import CategorySerializer
from .permissions import IsCategoryManagementStaff


class CategoryListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]

        return [
            IsAuthenticated(),
            IsCategoryManagementStaff(),
        ]

    # Get all active categories
    def get(self, request):
        categories = Category.objects.filter(is_active=True)
        serializer = CategorySerializer(categories, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # Create category
    def post(self, request):
        serializer = CategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class CategoryDetailView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsCategoryManagementStaff,
    ]

    def get_object(self, pk):
        return get_object_or_404(Category, pk=pk)

    # Get category details
    def get(self, request, pk):
        category = self.get_object(pk)
        serializer = CategorySerializer(category)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # Update complete category
    def put(self, request, pk):
        category = self.get_object(pk)
        serializer = CategorySerializer(
            category,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update partial category details
    def patch(self, request, pk):
        category = self.get_object(pk)
        serializer = CategorySerializer(
            category,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # Deactivate category instead of permanently deleting
    def delete(self, request, pk):
        category = self.get_object(pk)
        category.is_active = False
        category.save()

        return Response(
            {"message": "Category deactivated successfully."},
            status=status.HTTP_200_OK
        )
