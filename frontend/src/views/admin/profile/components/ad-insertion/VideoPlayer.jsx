import React from 'react';

/**
 * VideoPlayer component - uses native video element
 * Simpler and more reliable than ReactPlayer for local files
 */
const VideoPlayer = ({ 
  videoRef, 
  videoSrc, 
  currentTime, 
  duration, 
  isPlaying, 
  onPlayPause,
  onError 
}) => {
  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  if (!videoSrc) {
    return (
      <div className="mb-4 max-w-2xl mx-auto">
        <div className="relative w-full bg-gray-100 rounded-lg" style={{ paddingTop: '56.25%' }}>
          <div className="absolute inset-0 flex items-center justify-center">
            <p className="text-gray-500">No video source</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mb-4 max-w-2xl mx-auto">
      {/* Video Element */}
      <div className="relative w-full bg-black rounded-lg overflow-hidden" style={{ paddingTop: '56.25%' }}>
        <video
          ref={videoRef}
          src={videoSrc}
          className="absolute top-0 left-0 w-full h-full object-contain"
          controls={false}
          preload="metadata"
          onError={onError}
        />
      </div>

      {/* Playback Controls */}
      <div className="flex items-center gap-3 mt-2">
        <button
          onClick={onPlayPause}
          className="px-4 py-2 bg-brand-500 text-white rounded-lg hover:bg-brand-600 transition-colors"
        >
          {isPlaying ? "⏸ Pause" : "▶ Play"}
        </button>
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {formatTime(currentTime)} / {formatTime(duration)}
        </span>
      </div>
    </div>
  );
};

export default VideoPlayer;
