import os

import requests
from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import OauthSerializer

User = get_user_model()


class GoogleLoginAPIView(CreateAPIView):
    serializer_class = OauthSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]

        token_response = requests.post(
            url="https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
                "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
                "redirect_uri": os.environ.get("GOOGLE_REDIRECT_URI"),
                "grant_type": "authorization_code",
            },
        )

        token_data = token_response.json()
        print("TOKEN_DATA:", token_data)
        access_token = token_data.get("access_token")

        if not access_token:
            return Response({"error": "Invalid access_token!"})

        user_info = requests.get(
            url="https://www.googleapis.com/oauth2/v3/userinfo",
            params={"alt": "json"},
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()

        print("=|" * 50)
        print("access_token: ", access_token)
        print(f"user_info: {user_info}")
        print("=|" * 50)

        email = user_info["email"]

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': user_info.get('given_name', ''),
                'last_name': user_info.get('family_name', ''),
                'registration_source': 'google',
                'is_active': True,
            }
        )

        if not created:
            user.last_login_google = timezone.now()
            user.save()
            
        print("USER CREATED: ", created)

        refresh = RefreshToken.for_user(user)
        refresh["email"] = user.email

        return Response(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            }
        )