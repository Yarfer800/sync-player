import asyncio
from dataclasses import dataclass
from pathlib import Path

import yt_dlp
from yt_dlp.utils import download_range_func


@dataclass
class ChunkVideo:
    start_time: int
    end_time: int


class YTDlpPlayer:
    def __init__(self) -> None:
        ...

    async def download_chunk_of_video(self, url: str, chunk: ChunkVideo, output_path: str | Path):
        return await asyncio.to_thread(self._sync_download_video, url, chunk, output_path)


    def _sync_download_video(self, url: str, chunk: ChunkVideo, output_path: str | Path):
        ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'download_ranges': download_range_func(None, [(chunk.start_time, chunk.end_time)]),
                'outtmpl': str(output_path),
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
                'format_sort': ['res', 'codec', 'size'],
                'merge_output_format': 'mp4',
                }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.download([url])
