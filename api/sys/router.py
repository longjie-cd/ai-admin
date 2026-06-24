from fastapi import APIRouter
from api.sys.auth.router import router as auth_router
from api.sys.bing.router import router as bing_router
from api.sys.user.router import router as user_router
from api.sys.role.router import router as role_router
from api.sys.permission.router import router as permission_router
from api.sys.team.router import router as team_router
from api.sys.dict.router import router as dict_router
from api.sys.api_interface.router import router as api_router
from api.sys.menu.router import router as menu_router
from api.sys.message.router import router as message_router
from api.sys.todo.router import router as todo_router
from api.sys.schedule.router import router as schedule_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(bing_router)
router.include_router(user_router)
router.include_router(role_router)
router.include_router(permission_router)
router.include_router(team_router)
router.include_router(dict_router)
router.include_router(api_router)
router.include_router(menu_router)
router.include_router(message_router)
router.include_router(todo_router)
router.include_router(schedule_router)
