from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.permissions import IsAdminOrSuperUser, IsAuthenticatedUser
from .models import Payment
from .serializers import PaymentCreateSerializer, PaymentListSerializer, PaymentDetailSerializer, PaymentUpdateSerializer


class PaymentsView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAdminOrSuperUser()]
        return [IsAuthenticatedUser()]
    
    def get(self, request):
        payments = Payment.objects.all()
        serializer = PaymentListSerializer(payments, many=True)
        return Response({
            'payments': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save()
            return Response(serializer.to_representation(payment), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticatedUser()]
        return [IsAdminOrSuperUser()]
    
    def get_object(self, payment_id):
        try:
            return Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return None
    
    def get(self, request, payment_id):
        payment = self.get_object(payment_id)
        if payment is None:
            return Response({'detail': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PaymentDetailSerializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, payment_id):
        payment = self.get_object(payment_id)
        if payment is None:
            return Response({'detail': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PaymentUpdateSerializer(payment, data=request.data)
        if serializer.is_valid():
            updated_payment = serializer.save()
            response_serializer = PaymentDetailSerializer(updated_payment)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, payment_id):
        payment = self.get_object(payment_id)
        if payment is None:
            return Response({'detail': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        payment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
