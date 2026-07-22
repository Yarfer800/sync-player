import os
import tempfile

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse, Response, StreamingResponse
from pydantic import BaseModel
import httpx
import hashlib
from pathlib import Path

from app.api.deps import CurrentUser
from app.services.player import ChunkVideo, YTDlpPlayer, STREAM_HEADERS_CACHE

router = APIRouter(prefix="/player", tags=["player"])


class DownloadRequest(BaseModel):
    url: str
    start_time: int
    end_time: int

class InfoRequest(BaseModel):
    url: str

def cleanup_file(path: str):
    try:
        os.remove(path)
    except OSError:
        pass

CACHE_DIR = Path("/tmp/sync_player_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_cache_path(url: str, start: int, end: int) -> Path:
    key = f"{url}_{start}_{end}".encode()
    hash_str = hashlib.md5(key).hexdigest()
    return CACHE_DIR / f"{hash_str}.mp4"


@router.get("/stream")
async def stream_video(url: str, request: Request):
    import urllib.parse
    netloc = urllib.parse.urlparse(url).netloc
    cached = STREAM_HEADERS_CACHE.get(netloc, {})
    
    headers = dict(cached.get("headers", {}))
    # Don't pass host header from cache
    headers.pop("Host", None)
    headers.pop("host", None)
    
    if "range" in request.headers:
        headers["range"] = request.headers["range"]
        
    cookies = {}
    if cached.get("cookies"):
        # Simple cookie parsing (yt-dlp returns cookie string sometimes)
        cookie_str = cached["cookies"]
        for c in cookie_str.split(";"):
            if "=" in c:
                k, v = c.strip().split("=", 1)
                cookies[k] = v

    client = httpx.AsyncClient(follow_redirects=True, cookies=cookies)
    req = client.build_request("GET", url, headers=headers)
    resp = await client.send(req, stream=True)
    
    content_type = resp.headers.get("content-type", "").lower()
    is_m3u8 = "mpegurl" in content_type or url.split("?")[0].endswith(".m3u8")

    if is_m3u8:
        await resp.aclose()
        resp = await client.get(url, headers=headers)
        text = resp.text
        
        import urllib.parse
        import re
        base_url = url
        
        rewritten_lines = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("#"):
                def replacer(match):
                    abs_uri = urllib.parse.urljoin(base_url, match.group(1))
                    return f'URI="/api/player/stream?url={urllib.parse.quote(abs_uri)}"'
                
                line = re.sub(r'URI="([^"]+)"', replacer, line)
                rewritten_lines.append(line)
            else:
                abs_url = urllib.parse.urljoin(base_url, line)
                proxy_url = f"/api/player/stream?url={urllib.parse.quote(abs_url)}"
                rewritten_lines.append(proxy_url)
                
        rewritten_text = "\n".join(rewritten_lines)
        return Response(content=rewritten_text, media_type="application/vnd.apple.mpegurl")
    
    response_headers = {
        "Content-Type": resp.headers.get("Content-Type", "application/octet-stream"),
        "Accept-Ranges": "bytes",
    }
    
    if "Content-Length" in resp.headers:
        response_headers["Content-Length"] = resp.headers["Content-Length"]
    if "Content-Range" in resp.headers:
        response_headers["Content-Range"] = resp.headers["Content-Range"]
        
    async def generate():
        async for chunk in resp.aiter_bytes():
            yield chunk
            
    status_code = resp.status_code if resp.status_code in [200, 206] else 206
    return StreamingResponse(generate(), status_code=status_code, headers=response_headers)


@router.post("/info")
async def get_info(
    body: InfoRequest,
    user: CurrentUser = None,
):
    player = YTDlpPlayer()
    try:
        info = await player.get_video_info(body.url)
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download")
async def download_chunk(
    body: DownloadRequest,
    user: CurrentUser = None,  # Require authentication
):
    if body.start_time < 0 or body.end_time <= body.start_time:
        raise HTTPException(status_code=400, detail="Invalid time range")

    cache_path = get_cache_path(body.url, body.start_time, body.end_time)

    if not cache_path.exists():
        player = YTDlpPlayer()
        chunk = ChunkVideo(start_time=body.start_time, end_time=body.end_time)

        fd, temp_path = tempfile.mkstemp(suffix=".mp4")
        os.close(fd)

        try:
            await player.download_chunk_of_video(body.url, chunk, temp_path)
            os.rename(temp_path, cache_path)
        except Exception as e:
            cleanup_file(temp_path)
            raise HTTPException(status_code=500, detail=str(e))

    return FileResponse(cache_path, media_type="video/mp4", filename="chunk.mp4")
