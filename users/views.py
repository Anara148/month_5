from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegistrationSerializer, ConfirmSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import random
import string
#from django.core.mail import send_mail
#from django.conf import settings
from .models import UserProfile


class AuthorizationAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if not user.is_active:
                return Response(
                    {'error': 'Please confirm your email first'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            try:
                token = Token.objects.get(user=user)
            except:
                token = Token.objects.create(user=user)
            return Response(data={'key': token.key})
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class RegistrationAPIView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=False)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')
        email = serializer.validated_data.get('email')

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            is_active=False
        )

        code = ''.join(random.choices(string.digits, k=6))
        
        UserProfile.objects.create(user=user, code=code)
        
        print(f"Код для {email}: {code}")

        return Response(
            data={'user_id': user.id, 'message': 'Check your email for confirmation code'},
            status=status.HTTP_201_CREATED
        )

class ConfirmAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = UserProfile.objects.get(user=user, code=code)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save()
        
        profile.delete()

        try:
            token = Token.objects.get(user=user)
        except:
            token = Token.objects.create(user=user)

        return Response(data={'key': token.key}, status=status.HTTP_200_OK)