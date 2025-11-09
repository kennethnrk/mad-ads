import { useState, useRef, useEffect, useCallback } from 'react';

/**
 * Custom hook for managing video player state
 * Uses native video element with proper state management
 */
export const useVideoPlayer = (videoSrc) => {
  const videoRef = useRef(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isReady, setIsReady] = useState(false);

  // Update video source when it changes
  useEffect(() => {
    const video = videoRef.current;
    if (!video || !videoSrc) return;

    // Only update if source actually changed
    if (video.src !== videoSrc) {
      video.src = videoSrc;
      video.load();
      setIsReady(false);
      setCurrentTime(0);
      setIsPlaying(false);
    }
  }, [videoSrc]);

  // Set up event listeners - only once
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => {
      if (video.readyState >= 2) {
        setCurrentTime(video.currentTime);
      }
    };

    const handleDurationChange = () => {
      if (video.duration && isFinite(video.duration)) {
        setDuration(video.duration);
      }
    };

    const handleLoadedMetadata = () => {
      if (video.duration && isFinite(video.duration)) {
        setDuration(video.duration);
      }
      setIsReady(true);
      setCurrentTime(0);
    };

    const handleLoadedData = () => {
      setIsReady(true);
      if (video.duration && isFinite(video.duration)) {
        setDuration(video.duration);
      }
    };

    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);
    const handleCanPlay = () => setIsReady(true);

    // Add all event listeners
    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('durationchange', handleDurationChange);
    video.addEventListener('loadedmetadata', handleLoadedMetadata);
    video.addEventListener('loadeddata', handleLoadedData);
    video.addEventListener('canplay', handleCanPlay);
    video.addEventListener('play', handlePlay);
    video.addEventListener('pause', handlePause);

    // Check if already loaded
    if (video.readyState >= 1) {
      handleLoadedMetadata();
    }

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('durationchange', handleDurationChange);
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
      video.removeEventListener('loadeddata', handleLoadedData);
      video.removeEventListener('canplay', handleCanPlay);
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('pause', handlePause);
    };
  }, []); // Only set up once

  const play = useCallback(() => {
    const video = videoRef.current;
    if (video && isReady) {
      video.play().catch(err => {
        console.error('Play error:', err);
      });
    }
  }, [isReady]);

  const pause = useCallback(() => {
    const video = videoRef.current;
    if (video) {
      video.pause();
    }
  }, []);

  const togglePlayPause = useCallback(() => {
    if (isPlaying) {
      pause();
    } else {
      play();
    }
  }, [isPlaying, play, pause]);

  const seek = useCallback((time) => {
    const video = videoRef.current;
    if (!video) return;

    const clampedTime = Math.max(0, Math.min(time, duration || 0));

    if (video.readyState >= 2) {
      video.currentTime = clampedTime;
      setCurrentTime(clampedTime);
    } else {
      // Wait for video to be ready
      const seekWhenReady = () => {
        if (video.readyState >= 2) {
          video.currentTime = clampedTime;
          setCurrentTime(clampedTime);
          video.removeEventListener('loadeddata', seekWhenReady);
          video.removeEventListener('canplay', seekWhenReady);
        }
      };
      video.addEventListener('loadeddata', seekWhenReady);
      video.addEventListener('canplay', seekWhenReady);
    }
  }, [duration]);

  return {
    videoRef,
    currentTime,
    duration,
    isPlaying,
    isReady,
    play,
    pause,
    togglePlayPause,
    seek,
  };
};
