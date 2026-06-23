from fastapi import APIRouter, HTTPException, status
from api.core.response import ApiResponse
from api.sys.auth.schema import LoginRequest, TokenResponse
from api.sys.auth.service import authenticate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=ApiResponse)
def login(body: LoginRequest):
    token = authenticate(body.username, body.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    return ApiResponse.ok(
        data=TokenResponse(access_token=token).model_dump(),
        message="登录成功",
    )
