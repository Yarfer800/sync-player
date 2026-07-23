import asyncio
from dataclasses import dataclass
from pathlib import Path

import yt_dlp
from yt_dlp.utils import download_range_func


@dataclass
class ChunkVideo:
    start_time: int
    end_time: int


STREAM_HEADERS_CACHE = {}

class YTDlpPlayer:
    async def download_chunk_of_video(self, url: str, chunk: ChunkVideo, output_path: str | Path):
        return await asyncio.to_thread(self._sync_download_video, url, chunk, output_path)


    def _sync_download_video(self, url: str, chunk: ChunkVideo, output_path: str | Path):
        ydl_opts = {
                'quiet': False,
                'no_warnings': False,
                'overwrites': True,
                'download_ranges': download_range_func(None, [(chunk.start_time, chunk.end_time)]),
                'outtmpl': str(output_path),
                'format': 'bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
                'format_sort': ['res', 'codec', 'size'],
                'merge_output_format': 'mp4',
                }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.download([url])

    async def get_video_info(self, url: str):
        return await asyncio.to_thread(self._sync_get_video_info, url)

    def _sync_get_video_info(self, url: str):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            req_formats = info.get("requested_formats", [])
            video_url = req_formats[0].get("url") if req_formats else info.get("url")
            audio_url = req_formats[1].get("url") if req_formats else info.get("url")

            headers = info.get("http_headers", {})
            cookies = info.get("cookies", "")
            
            import urllib.parse
            if video_url:
                netloc = urllib.parse.urlparse(video_url).netloc
                STREAM_HEADERS_CACHE[netloc] = {"headers": headers, "cookies": cookies}
            if audio_url:
                netloc = urllib.parse.urlparse(audio_url).netloc
                STREAM_HEADERS_CACHE[netloc] = {"headers": headers, "cookies": cookies}

            return {
                "duration": info.get("duration"),
                "title": info.get("title"),
                "video_url": video_url,
                "audio_url": audio_url
            }

    async def get_direct_stream_url(self, url: str):
        return await asyncio.to_thread(self._sync_get_direct_stream_url, url)

    def _sync_get_direct_stream_url(self, url: str):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best[ext=mp4]/best',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get("url")
