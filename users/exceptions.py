from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, AuthenticationFailed as JWTAuthFailed
from jwt.exceptions import ExpiredSignatureError

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is None:
        return None

    custom_response_data = {}

    if isinstance(exc, JWTAuthFailed): 
        custom_response_data = {
            "error": {
                "code": "INVALID_TOKEN",
                "message": "토큰과 사용자 매칭을 실패하였습니다."
            }
        }
        response.status_code = 401

    elif isinstance(exc, InvalidToken): 
        custom_response_data = {
            "error": {
                "code": "INVALID_TOKEN",
                "message": "토큰이 검증을 실패했습니다."
            }
        }
        response.status_code = 401

    elif isinstance(exc, TokenError): 
        custom_response_data = {
            "error": {
                "code": "INVALID_TOKEN",
                "message": "토큰 형식에 문제가 있거나, 유효하지 않은 토큰 값입니다."
            }
        }
        response.status_code = 401

    elif isinstance(exc, NotAuthenticated):
        custom_response_data = {
            "error": {
                "code": "TOKEN_NOT_FOUND",
                "message": "토큰이 없습니다."
            }
        }
        response.status_code = 401

    elif isinstance(exc, AuthenticationFailed): 
        custom_response_data = {
            "error": {
                "code": "INVALID_TOKEN",
                "message": "인증된 유저가 아닙니다."
            }
        }
        response.status_code = 401

    elif isinstance(getattr(exc, 'detail', None), dict) and 'code' in exc.detail:
        if exc.detail['code'] == 'token_not_valid':
            messages = exc.detail.get('messages', [])
            if messages and messages[0].get('message') == 'Token is invalid or expired':
                custom_response_data = {
                    "error": {
                        "code": "TOKEN_EXPIRED",
                        "message": "토큰이 만료되었습니다."
                    }
                }
                response.status_code = 401

    if custom_response_data:
        response.data = custom_response_data

    return response
