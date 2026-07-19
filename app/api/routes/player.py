import os
import tempfile

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.api.deps import CurrentUser
from app.services.player import ChunkVideo, YTDlpPlayer

router = APIRouter(prefix="/player", tags=["player"])


class DownloadRequest(BaseModel):
    url: str
    start_time: int
    end_time: int


def cleanup_file(path: str):
    try:
        os.remove(path)
    except OSError:
        pass


@router.post("/download")
async def download_chunk(
    body: DownloadRequest,
    background_tasks: BackgroundTasks,
    user: CurrentUser = None,  # Require authentication
):
    if body.start_time < 0 or body.end_time <= body.start_time:
        raise HTTPException(status_code=400, detail="Invalid time range")

    player = YTDlpPlayer()
    chunk = ChunkVideo(start_time=body.start_time, end_time=body.end_time)

    # Note: yt-dlp might change the extension based on format, so we use a template
    fd, temp_path = tempfile.mkstemp(suffix=".mp4")
    os.close(fd)

    try:
        await player.download_chunk_of_video(body.url, chunk, temp_path)
    except Exception as e:
        cleanup_file(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

    background_tasks.add_task(cleanup_file, temp_path)
    return FileResponse(temp_path, media_type="video/mp4", filename="chunk.mp4")
