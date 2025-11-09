import React, { useState, useRef } from 'react';
import Card from 'components/card';
import { API_ENDPOINTS } from 'config/api';
import Timeline from './Timeline';
import MarkerList from './MarkerList';
import { useMarkers } from './hooks/useMarkers';
import { useVideoGeneration } from './hooks/useVideoGeneration';

/**
 * Main AdInsertion component - simplified, all-in-one
 * Simple video player with marker tracking
 */
const AdInsertion = ({ transcription, videoFile }) => {
  const videoRef = useRef(null);
  
  // Video state - simple and direct
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const {
    markers,
    selectedMarker,
    addMarker,
    removeMarker,
    selectMarker,
  } = useMarkers();

  const {
    generating,
    previewMode,
    previewTimestamp,
    error,
    success,
    generateVideo,
    resetPreview,
  } = useVideoGeneration();

  // Video source - toggle between original and preview
  const videoSrc = previewMode 
    ? `${API_ENDPOINTS.VIDEO_PREVIEW}?t=${previewTimestamp}` 
    : API_ENDPOINTS.VIDEO_TEST_VIDEO;

  // Simple event handlers
  const handleTimeUpdate = (e) => {
    setCurrentTime(e.target.currentTime);
  };

  const handleLoadedMetadata = (e) => {
    const video = e.target;
    if (video.duration && isFinite(video.duration)) {
      setDuration(video.duration);
    }
    setCurrentTime(0);
  };

  const handlePlay = () => setIsPlaying(true);
  const handlePause = () => setIsPlaying(false);

  const togglePlayPause = () => {
    const video = videoRef.current;
    if (!video) return;
    
    if (isPlaying) {
      video.pause();
    } else {
      video.play().catch(err => console.error('Play error:', err));
    }
  };

  const handleSeek = (newTime) => {
    const video = videoRef.current;
    if (!video) return;
    
    const clampedTime = Math.max(0, Math.min(newTime, duration || 0));
    video.currentTime = clampedTime;
    setCurrentTime(clampedTime);
  };

  const handleAddMarker = () => {
    addMarker(currentTime);
  };

  const handleSeekToMarker = (timestamp) => {
    handleSeek(timestamp);
  };

  const handleGenerate = () => {
    generateVideo(markers);
  };

  const handleVideoError = (e) => {
    console.error("Video load error:", e);
    console.error("Video source was:", videoSrc);
    if (previewMode) {
      resetPreview();
    }
  };

  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <Card extra="w-full p-4">
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <div>
            <h5 className="text-xl font-bold text-navy-700 dark:text-white">
              Insert Ads into Video
            </h5>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              Scrub to a timestamp, click "+ Add Marker" to place ads, then generate the final video
            </p>
          </div>
          <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded text-xs font-semibold">
            TESTING MODE
          </span>
        </div>
      </div>

      {/* Main Layout: Left (Video + Timeline) | Right (Controls) */}
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Left Column - Video Player & Timeline */}
        <div className="flex-1 min-w-0">
          {/* Video Player */}
          <div className="mb-4">
            <div className="relative w-full bg-black rounded-lg overflow-hidden" style={{ paddingTop: '56.25%' }}>
              <video
                key={videoSrc} // Force remount when source changes
                ref={videoRef}
                src={videoSrc}
                className="absolute top-0 left-0 w-full h-full object-contain"
                controls={false}
                preload="metadata"
                onTimeUpdate={handleTimeUpdate}
                onLoadedMetadata={handleLoadedMetadata}
                onPlay={handlePlay}
                onPause={handlePause}
                onError={handleVideoError}
              />
            </div>
          </div>

          {/* Timeline */}
          <Timeline
            currentTime={currentTime}
            duration={duration}
            markers={markers}
            selectedMarker={selectedMarker}
            onSeek={handleSeek}
            onMarkerClick={selectMarker}
            onAddMarker={handleAddMarker}
          />
        </div>

        {/* Right Column - Controls & Buttons */}
        <div className="w-full lg:w-80 flex flex-col gap-4">
          {/* Playback Controls */}
          <div className="bg-gray-50 dark:bg-navy-700 rounded-lg p-4">
            <div className="flex flex-col gap-3">
              <button
                onClick={togglePlayPause}
                className="w-full px-4 py-2 bg-brand-500 text-white rounded-lg hover:bg-brand-600 transition-colors font-semibold"
              >
                {isPlaying ? "⏸ Pause" : "▶ Play"}
              </button>
              <div className="text-center">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {formatTime(currentTime)} / {formatTime(duration)}
                </span>
              </div>
              {previewMode && (
                <div className="text-center">
                  <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs font-semibold">
                    Preview Mode
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Add Marker Button */}
          <button
            onClick={handleAddMarker}
            className="w-full px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors font-semibold"
            title="Add marker at current time"
          >
            + Add Marker
          </button>

          {/* Marker List */}
          <MarkerList
            markers={markers}
            selectedMarker={selectedMarker}
            onSelectMarker={selectMarker}
            onRemoveMarker={removeMarker}
            onSeekToMarker={handleSeekToMarker}
          />

          {/* Generate Button */}
          <div className="flex flex-col gap-3">
            <button
              onClick={handleGenerate}
              disabled={generating || markers.length === 0}
              className="w-full px-4 py-3 bg-brand-500 text-white rounded-lg font-semibold hover:bg-brand-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {generating ? "⏳ Generating Video..." : `Generate Final Video (${markers.length} marker${markers.length !== 1 ? 's' : ''})`}
            </button>
            {previewMode && (
              <button
                onClick={resetPreview}
                className="w-full px-4 py-3 bg-gray-500 text-white rounded-lg font-semibold hover:bg-gray-600 transition-colors"
              >
                View Original
              </button>
            )}
          </div>

          {/* Status Messages */}
          {error && (
            <div className="rounded-lg bg-red-50 p-4 dark:bg-red-900/20">
              <p className="text-sm text-red-800 dark:text-red-200">
                <strong>Error:</strong> {error}
              </p>
            </div>
          )}

          {success && (
            <div className="rounded-lg bg-green-50 p-4 dark:bg-green-900/20">
              <p className="text-sm text-green-800 dark:text-green-200 font-semibold mb-1">
                ✅ {success.message}
              </p>
              <p className="text-xs text-green-700 dark:text-green-300">
                Preview is now available. Click "View Original" to switch back.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Info Footer */}
      <div className="mt-4 p-3 rounded-lg bg-gray-50 dark:bg-navy-700">
        <p className="text-xs text-gray-600 dark:text-gray-400">
          <strong>Testing Mode:</strong> This section is always visible for testing purposes using hardcoded test videos (videoplayback.mp4 and demo_ad.mp4).
          Use the "+ Add Marker" button to place ads at specific timestamps, then generate the final video.
          <span className="block mt-1 text-yellow-700 dark:text-yellow-400">
            ⚠️ This shortcut will be disabled after feature finalization.
          </span>
        </p>
      </div>
    </Card>
  );
};

export default AdInsertion;
