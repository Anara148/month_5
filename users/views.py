from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from .redis_client import save_confirmation_code, verify_and_delete_code 

from .serializers import (
    RegisterValidateSerializer,
    AuthValidateSerializer,
    #ConfirmationSerializer,
    CustomJWTSerializer
)
#from .models import ConfirmationCode
import random
import string
from django.contrib.auth import get_user_model
from users.models import CustomUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken 
from users.tasks import add, send_otp_mail

CustomUser = get_user_model()


class CustomJWTView(TokenObtainPairView):
    serializer_class = CustomJWTSerializer


class AuthorizationAPIView(APIView):
    serializer_class = AuthValidateSerializer
    def post(self, request):
        from time import sleep
        add.delay(5,4)
        serializer = AuthValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(**serializer.validated_data)

        if user:
            if not user.is_active:
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    data={'error': 'Аккаунт не активирован!'}
                )

            refresh = RefreshToken.for_user(user)
            refresh['birthdate'] = str(user.birthdate) if user.birthdate else None
            
            return Response(data={
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })

            #token, _ = Token.objects.get_or_create(user=user)
            #return Response(data={'key': token.key})

        return Response(
            status=status.HTTP_401_UNAUTHORIZED,
            data={'error': 'Неверные учетные данные!'}
        )


class RegistrationAPIView(CreateAPIView):
    serializer_class = RegisterValidateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        phone_number = serializer.validated_data.get('phone_number', '')
        username = serializer.validated_data.get('username', '')
        birthdate = serializer.validated_data.get('birthdate')

        with transaction.atomic():
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                phone_number=phone_number,
                username=username,
                birthdate=birthdate,
                is_active=False
            )

            code = ''.join(random.choices(string.digits, k=6))

            save_confirmation_code(email, code, timeout=300)
            
            print(f"Код для {email}: {code}")

            send_otp_mail.delay(email, code)
            #confirmation_code = ConfirmationCode.objects.create(
             #   user=user,
              #  code=code
            #)

        return Response(
            status=status.HTTP_201_CREATED,
            data={
                'user_id': user.id,
                'confirmation_code': code
            }
        )



class ConfirmUserAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=400)

        if not verify_and_delete_code(email, code):
            return Response({'error': 'Invalid or expired code'}, status=400)

        user.is_active = True
        user.save()

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            status=status.HTTP_200_OK,
            data={
                'message': 'Аккаунт успешно активирован',
                'key': token.key
            }
        )