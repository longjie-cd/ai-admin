import httpx

BING_API = "https://www.bing.com/HPImageArchive.aspx"
BING_BASE = "https://www.bing.com"

_image_url: str = ""


async def get_daily_wallpaper() -> dict:
    global _image_url
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(BING_API, params={"format": "js", "idx": 0, "n": 1})
        resp.raise_for_status()
    image = resp.json()["images"][0]
    _image_url = BING_BASE + image["url"]
    return {
        "url": "/api/bing/wallpaper/image",
        "title": image.get("title", ""),
        "copyright": image.get("copyright", ""),
    }


async def proxy_image() -> tuple[bytes, str]:
    global _image_url
    if not _image_url:
        await get_daily_wallpaper()

    chunks: list[bytes] = []
    content_type = "image/jpeg"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            async with client.stream(
                "GET",
                _image_url,
                headers={"Referer": "https://www.bing.com/"},
                follow_redirects=True,
            ) as resp:
                content_type = resp.headers.get("content-type", "image/jpeg").split(";")[0]
                async for chunk in resp.aiter_bytes():
                    chunks.append(chunk)
    except httpx.RemoteProtocolError:
        # Bing closes connection before Content-Length is satisfied;
        # the received bytes are still a valid image.
        pass

    return b"".join(chunks), content_type
