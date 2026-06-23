from fastapi import APIRouter
from fastapi.responses import Response
from api.core.response import ApiResponse
from api.sys.bing.service import get_daily_wallpaper, proxy_image

router = APIRouter(prefix="/bing", tags=["bing"])


@router.get("/wallpaper", response_model=ApiResponse)
async def wallpaper():
    data = await get_daily_wallpaper()
    return ApiResponse.ok(data=data)


@router.get("/wallpaper/image")
async def wallpaper_image():
    content, content_type = await proxy_image()
    return Response(
        content=content,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=3600"},
    )
