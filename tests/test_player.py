import asyncio
import os
import glob

from app.services.player import ChunkVideo, YTDlpPlayer


async def test_download_video():
    _TESTS = [
            {
                'url': 'https://youtu.be/DLRjhptssns?si=gAToBxk9DPJPgAa1',
                'start': 0,
                'end': 10,
                'output_path': 'tests/test_1.%(ext)s'
                }
            ]
    player = YTDlpPlayer()
    for test in _TESTS:
        await player.download_chunk_of_video(test['url'], ChunkVideo(start_time=test['start'], end_time=test['end']), test['output_path'])
        possible_extensions = ['.mp4', '.webm', '.mkv', '.m4a']
        file_found = False
        
        for ext in possible_extensions:
            expected_file = test['output_path'].replace('%(ext)s', ext.strip('.'))
            pattern = test['output_path'].replace('%(ext)s', '*')
            files = glob.glob(pattern)
            if files:
                file_found = True
                assert os.path.getsize(files[0]) > 0, "File empty"
                os.remove(files[0])
                break
        
        assert file_found, "File not found"

