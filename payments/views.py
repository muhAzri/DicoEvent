from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from django.conf import settings
from users.permissions import IsAdminOrSuperUser, IsAuthenticatedUser
from .models import Payment
from .serializers import (
    PaymentCreateSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer,
    PaymentUpdateSerializer,
)


class PaymentsView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAdminOrSuperUser()]
        return [IsAuthenticatedUser()]

    def get(self, request):
        # Try to get from cache first
        cache_key = "payments_list"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            # Return cached data with X-Data-Source header
            response = Response(cached_data, status=status.HTTP_200_OK)
            response['X-Data-Source'] = 'cache'
            return response
        
        # If not in cache, get from database
        payments = Payment.objects.all()
        serializer = PaymentListSerializer(payments, many=True)
        data = {"payments": serializer.data}
        
        # Cache the data for 1 hour
        cache.set(cache_key, data, settings.CACHE_TTL)
        
        # Return fresh data with X-Data-Source header
        response = Response(data, status=status.HTTP_200_OK)
        response['X-Data-Source'] = 'database'
        return response

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save()
            
            # Invalidate payments list cache
            cache.delete("payments_list")
            
            return Response(
                serializer.to_representation(payment), status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticatedUser()]
        return [IsAdminOrSuperUser()]

    def get_object(self, payment_id):
        try:
            return Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return None

    def get(self, request, payment_id):
        # Try to get from cache first
        cache_key = f"payment_detail_{payment_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            # Return cached data with X-Data-Source header
            response = Response(cached_data, status=status.HTTP_200_OK)
            response['X-Data-Source'] = 'cache'
            return response
        
        # If not in cache, get from database
        payment = self.get_object(payment_id)
        if payment is None:
            return Response(
                {"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = PaymentDetailSerializer(payment)
        data = serializer.data
        
        # Cache the data for 1 hour
        cache.set(cache_key, data, settings.CACHE_TTL)
        
        # Return fresh data with X-Data-Source header
        response = Response(data, status=status.HTTP_200_OK)
        response['X-Data-Source'] = 'database'
        return response

    def put(self, request, payment_id):
        payment = self.get_object(payment_id)
        if payment is None:
            return Response(
                {"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = PaymentUpdateSerializer(payment, data=request.data)
        if serializer.is_valid():
            updated_payment = serializer.save()
            
            # Invalidate cache for this specific payment detail
            cache.delete(f"payment_detail_{payment_id}")
            # Invalidate payments list cache
            cache.delete("payments_list")
            
            response_serializer = PaymentDetailSerializer(updated_payment)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, payment_id):
        payment = self.get_object(payment_id)
        if payment is None:
            return Response(
                {"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND
            )

        payment.delete()
        
        # Invalidate cache for this specific payment detail
        cache.delete(f"payment_detail_{payment_id}")
        # Invalidate payments list cache
        cache.delete("payments_list")
        
        return Response(status=status.HTTP_204_NO_CONTENT)
