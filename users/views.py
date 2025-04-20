# users/views.py
from django.contrib.auth import authenticate

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from datetime import datetime, timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from drf_spectacular.utils import extend_schema,OpenApiExample, OpenApiResponse

from .serializers import SignupSerializer,LoginSerializer



class SignupView(APIView):

    @extend_schema(
        tags=["feature"],
        description="회원가입을 위한 API. 회원가입시 입력한 정보를 반환합니다.",
        request=SignupSerializer,
        examples=[
            OpenApiExample(
                name="요청 예시",
                value={
                    "username": "testuser",
                    "email": "user@email.com",
                    "password": "password"
                },
                request_only=True
            )
        ],
        responses={
            201: OpenApiResponse(
                response=SignupSerializer,
                examples=[
                    OpenApiExample(
                        name="회원가입 성공 예시",
                        value={
                            "username": "testuser9",
                            "email": "user@email.com"
                        },
                        response_only=True,
                    )
                ]
            ),
            400: OpenApiResponse(
                response=SignupSerializer,
                description="회원가입 실패 예시",
                examples=[
                OpenApiExample(
                    name="아이디 미입력",
                    value={
                        "error": {
                            "code": "USERNAME_REQUIRED",
                            "message": "사용자 이름을 입력해 주세요."
                        }
                    },
                    response_only=True
                ),
                OpenApiExample(
                    name="중복 아이디",
                    value={
                        "error": {
                            "code": "USER_ALREADY_EXISTS",
                            "message": "사용자 이름이 중복되었습니다."
                        }
                    },
                    response_only=True
                ),
                OpenApiExample(
                    name="그 외 입력 오류",
                    value={
                        "error": {
                            "code": "INVALID_INPUT",
                            "message": "입력 값에 오류가 있습니다.",
                            "details": {
                                "email": ["This field is required."],
                                "password": ["This field is required."]
                                    }
                                }
                            },
                            response_only=True
                            ),
                        ]
                    )
                }
            )
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "username": user.username,
                "email" : user.email,
            }, status=status.HTTP_201_CREATED)
        
        # username가 중복일 경우
        if 'username' in serializer.errors:
            username_errors = serializer.errors['username'] 
            if any("already exists" in str(err) for err in username_errors):
                return Response({
                    "error": {
                        "code": "USER_ALREADY_EXISTS",
                        "message": "사용자 이름이 중복되었습니다."
                        }
                        }, status=status.HTTP_400_BAD_REQUEST)

            elif any("is required." in str(err) for err in username_errors):
                return Response({
                    "error": {
                        "code": "USERNAME_REQUIRED",
                        "message": "사용자 이름을 입력해 주세요."
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
    @extend_schema(
        tags=["feature"],
        description="로그인을 위한 API. 로그인 성공시 JWT access token을 반환합니다.",
        request=LoginSerializer,
        
        examples=[
            OpenApiExample(
                name="요청 예시",
                value={"username": "testuser", 
                       "password": "password"},
                request_only=True
            )
        ],
        responses={            
            200: OpenApiResponse(
                response=LoginSerializer,
                examples=[
                    OpenApiExample(
                        name="로그인 성공 예시",
                        value={"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9......"},
                        response_only=True,
                    )
                ]                                
            ),
            401: OpenApiResponse(
                response=LoginSerializer,
                examples=[
                    OpenApiExample(
                        name="로그인 실패 예시",
                        value={
                            "error": {
                                "code": "INVALID_CREDENTIALS",
                                "message": "아이디 또는 비밀번호가 올바르지 않습니다."
                                }
                                },
                                response_only=True,
                                )
                            ]
                        )
                    }
                )        
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "token": str(refresh.access_token),
                }, status=status.HTTP_200_OK)

            return Response({
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "아이디 또는 비밀번호가 올바르지 않습니다."
                }
            }, status=status.HTTP_401_UNAUTHORIZED)

        # serializer.is_valid() 실패 시
        return Response({
            "error": {
                "code": "INVALID_INPUT",
                "message": "입력 값이 유효하지 않습니다.",
                "details": serializer.errors
            }
        }, status=status.HTTP_400_BAD_REQUEST)


# test용 api
class ProtectedView(APIView):
    permission_classes = []

    @extend_schema(
        tags=["test"],
        description="pytest에서 토큰 유효성을 검사하기 위한 API.",
    )
    def get(self, request): 
        token = request.headers.get('Authorization')
        if not token:
            return Response({
                "error": {
                    "code": "TOKEN_NOT_FOUND",
                    "message": "토큰이 없습니다."
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        if token.startswith('Bearer '):
            token = token[7:]
        else:
            return Response({
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "토큰이 유효하지 않습니다."
                }
            }, status=status.HTTP_400_BAD_REQUEST)     
        return Response({"message": "토큰이 인증 되었습니다."})