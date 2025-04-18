# users/views.py
from django.contrib.auth import authenticate
from django.db import IntegrityError

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializers import SignupSerializer


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "username": user.username,
            }, status=status.HTTP_201_CREATED)
        
        # username가 중복일 경우
        if 'username' in serializer.errors:
            return Response({
                "error": {
                    "code": "USER_ALREADY_EXISTS",
                    "message": "이미 사용 중인 사용자 이름입니다."
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 그외 오류인 경우.
        return Response({
            "error": {
                "code": "INVALID_INPUT",
                "message": "입력 값에 오류가 있습니다.",
                "details": serializer.errors  
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "token": str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(
            {"error": {
                "code": "INVALID_CREDENTIALS",
                "message": "아이디 또는 비밀번호가 올바르지 않습니다."
                }
            }, status=status.HTTP_401_UNAUTHORIZED)


# test용 api
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"detail": "You are authenticated!"})