from api.core.security import verify_password, create_access_token
from api.sys.user.crud import get_user_by_username


def authenticate(username: str, password: str) -> str | None:
    """验证用户名密码，成功返回 JWT，失败返回 None。"""
    user = get_user_by_username(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return create_access_token(username)
