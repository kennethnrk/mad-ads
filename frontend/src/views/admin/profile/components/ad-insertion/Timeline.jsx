import React from 'react';

/**
 * Timeline component - visual timeline with markers and scrubber
 */
const Timeline = ({ 
  currentTime, 
  duration, 
  markers, 
  selectedMarker, 
  onSeek, 
  onMarkerClick,
  onAddMarker 
}) => {
  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const getMarkerPosition = (timestamp) => {
    if (!duration || duration === 0) return 0;
    return Math.min((timestamp / duration) * 100, 100);
  };

  const handleTimelineClick = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const percentage = clickX / rect.width;
    const timestamp = percentage * duration;
    onAddMarker(timestamp);
  };

  const progressPercentage = duration > 0 
    ? Math.min((currentTime / duration) * 100, 100) 
    : 0;

  return (
    <div className="mb-4">
      <div className="relative">
        <div className="relative h-8">
          {/* Visual timeline bar */}
          <div
            onClick={handleTimelineClick}
            className="absolute inset-0 w-full h-8 bg-gray-200 rounded-lg cursor-pointer dark:bg-gray-700 z-10"
            style={{
              background: `linear-gradient(to right, #4318FF 0%, #4318FF ${progressPercentage}%, #E2E8F0 ${progressPercentage}%, #E2E8F0 100%)`
            }}
          />
          
          {/* Timeline scrubber input */}
          <input
            type="range"
            min="0"
            max={duration || 0}
            value={currentTime}
            onChange={(e) => onSeek(parseFloat(e.target.value))}
            step="0.1"
            className="absolute inset-0 w-full h-full cursor-pointer z-20"
            style={{ background: 'transparent' }}
          />
          
          {/* Markers */}
          {markers.map((marker) => (
            <div
              key={marker.id}
              onClick={(e) => {
                e.stopPropagation();
                onMarkerClick(marker.id);
              }}
              className={`absolute top-0 w-1 h-8 cursor-pointer z-30 ${
                selectedMarker === marker.id ? 'bg-yellow-400' : 'bg-purple-600'
              }`}
              style={{ left: `${getMarkerPosition(marker.timestamp)}%` }}
              title={`Marker at ${formatTime(marker.timestamp)} - Click to select`}
            >
              <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 text-xs text-purple-700 dark:text-purple-300 font-semibold whitespace-nowrap pointer-events-none">
                {formatTime(marker.timestamp)}
              </div>
            </div>
          ))}
        </div>
        
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>0:00</span>
          <span className="font-semibold">Current: {formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>
    </div>
  );
};

export default Timeline;

