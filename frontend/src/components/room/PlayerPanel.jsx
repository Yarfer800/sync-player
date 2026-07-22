import { useRef, useEffect, useState } from 'react';
import { getInitData } from '../../utils/telegram';
import Hls from 'hls.js';

export default function PlayerPanel({ playerState, loading, isOwner, onUpdateState }) {
  const [videoInfo, setVideoInfo] = useState(null);
  
  const videoRef = useRef(null);
  const audioRef = useRef(null);
  const hlsRef = useRef(null);
  
  const [localTime, setLocalTime] = useState(0);
  
  // 1. Fetch info (this gets the direct 1080p video URL and the audio URL)
  useEffect(() => {
    if (!playerState?.video_source_link) return;
    const fetchInfo = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || '/api';
        const res = await fetch(`${apiUrl}/player/info`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Init-Data': getInitData()
          },
          body: JSON.stringify({ url: playerState.video_source_link })
        });
        if (res.ok) setVideoInfo(await res.json());
      } catch (e) {
        console.error("Info error", e);
      }
    };
    fetchInfo();
  }, [playerState?.video_source_link]);

  // Sync to playerState timecode (like when someone else seeks or initially)
  useEffect(() => {
    if (!playerState || !videoInfo) return;
    // We only seek if the difference is large enough to avoid feedback loops
    if (Math.abs(playerState.current_timecode - localTime) > 2) {
      handleSeek(playerState.current_timecode, false);
    }
  }, [playerState?.current_timecode, videoInfo]);

  // Handle Play/Pause sync
  useEffect(() => {
    if (!videoRef.current) return;
    
    if (playerState?.is_paused) {
      if (audioRef.current && !audioRef.current.paused) audioRef.current.pause();
      if (!videoRef.current.paused) videoRef.current.pause();
    } else {
      if (audioRef.current && audioRef.current.paused) audioRef.current.play().catch(() => {});
      if (videoRef.current.paused) videoRef.current.play().catch(() => {});
    }
  }, [playerState?.is_paused]);

  const handleSeek = (newTime, sendUpdate = true) => {
    setLocalTime(newTime);
    if (audioRef.current) audioRef.current.currentTime = newTime;
    if (videoRef.current) videoRef.current.currentTime = newTime;

    if (sendUpdate && isOwner) {
      onUpdateState({ ...playerState, current_timecode: newTime });
    }
  };

  const handleTimeUpdate = () => {
    const isCombined = videoInfo?.video_url === videoInfo?.audio_url;
    
    if (isCombined) {
      if (!videoRef.current) return;
      setLocalTime(videoRef.current.currentTime);
    } else {
      if (!audioRef.current || !videoRef.current) return;
      
      const time = audioRef.current.currentTime;
      setLocalTime(time);

      // Sync video to audio if they drift (audio is master clock)
      if (Math.abs(videoRef.current.currentTime - time) > 0.3) {
        videoRef.current.currentTime = time;
      }
    }
  };

  if (loading || !playerState) return null;

  const togglePlay = () => {
    if (!isOwner) return;
    onUpdateState({ ...playerState, is_paused: !playerState.is_paused });
  };

  const formatTime = (time) => {
    if (!time || isNaN(time)) return "0:00";
    const m = Math.floor(time / 60);
    const s = Math.floor(time % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  const apiUrl = import.meta.env.VITE_API_URL || '/api';
  const videoStreamUrl = videoInfo?.video_url ? `${apiUrl}/player/stream?url=${encodeURIComponent(videoInfo.video_url)}` : undefined;
  const audioStreamUrl = videoInfo?.audio_url ? `${apiUrl}/player/stream?url=${encodeURIComponent(videoInfo.audio_url)}` : undefined;
  const isCombined = videoInfo?.video_url === videoInfo?.audio_url;

  // Initialize HLS for video stream if needed
  useEffect(() => {
    if (!videoStreamUrl || !videoRef.current) return;
    
    // Check if URL suggests m3u8
    const isHls = videoInfo?.video_url?.includes('.m3u8');
    
    if (isHls && Hls.isSupported()) {
      const hls = new Hls({ maxBufferLength: 30 });
      hls.loadSource(videoStreamUrl);
      hls.attachMedia(videoRef.current);
      hlsRef.current = hls;
      
      return () => {
        hls.destroy();
        hlsRef.current = null;
      };
    } else {
      videoRef.current.src = videoStreamUrl;
    }
  }, [videoStreamUrl]);

  return (
    <div className="player-panel">
      {playerState.video_source_link ? (
        <div style={{ position: 'relative', paddingTop: '56.25%', width: '100%', background: '#000', borderRadius: '8px', overflow: 'hidden' }}>
          
          {/* Video */}
          <video
            ref={videoRef}
            style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}
            playsInline
            muted={!isCombined}
            onTimeUpdate={isCombined ? handleTimeUpdate : undefined}
          />

          {/* Audio (Master Clock for split streams) */}
          {!isCombined && audioStreamUrl && (
            <audio
              ref={audioRef}
              src={audioStreamUrl}
              onTimeUpdate={handleTimeUpdate}
            />
          )}

          {/* Custom Controls Container */}
          <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, padding: '15px', background: 'linear-gradient(transparent, rgba(0,0,0,0.8))', display: 'flex', alignItems: 'center', gap: '15px', zIndex: 20 }}>
            
            <button 
              onClick={togglePlay} 
              disabled={!isOwner}
              style={{ background: 'none', border: 'none', color: '#fff', cursor: isOwner ? 'pointer' : 'not-allowed', fontSize: '20px', padding: 0 }}
            >
              {playerState.is_paused ? '▶' : '⏸'}
            </button>
            
            <span style={{ color: '#fff', fontSize: '14px', fontFamily: 'monospace' }}>
              {formatTime(localTime)}
            </span>

            <input 
              type="range"
              min={0}
              max={videoInfo?.duration || 100}
              value={localTime}
              onChange={(e) => isOwner && handleSeek(Number(e.target.value))}
              style={{ flex: 1, cursor: isOwner ? 'pointer' : 'not-allowed' }}
              disabled={!isOwner}
            />

            <span style={{ color: '#aaa', fontSize: '14px', fontFamily: 'monospace' }}>
              {formatTime(videoInfo?.duration)}
            </span>

          </div>
        </div>
      ) : (
        <div style={{ padding: '40px 20px', textAlign: 'center', background: '#1a1a1a', borderRadius: '8px', border: '1px solid #333' }}>
          <p style={{ color: '#888', margin: 0 }}>No video loaded.</p>
        </div>
      )}

      <div className="player-panel__status" style={{ marginTop: '12px' }}>
        <span className={`player-panel__indicator ${playerState.is_paused ? '' : 'player-panel__indicator--playing'}`} />
        <span className="player-panel__state">
          {playerState.is_paused ? 'PAUSED' : 'PLAYING'}
        </span>
      </div>
    </div>
  );
}
