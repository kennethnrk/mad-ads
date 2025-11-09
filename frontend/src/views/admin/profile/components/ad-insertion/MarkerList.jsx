import React from 'react';

/**
 * MarkerList component - displays and manages markers
 */
const MarkerList = ({ 
  markers, 
  selectedMarker, 
  onSelectMarker, 
  onRemoveMarker,
  onSeekToMarker 
}) => {
  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  if (markers.length === 0) {
    return null;
  }

  return (
    <div className="bg-gray-50 dark:bg-navy-700 rounded-lg p-3">
      <h6 className="text-sm font-semibold text-navy-700 dark:text-white mb-2">
        Markers ({markers.length})
      </h6>
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {markers.map((marker) => (
          <div
            key={marker.id}
            className={`flex items-center justify-between p-2 rounded ${
              selectedMarker === marker.id
                ? 'bg-purple-100 dark:bg-purple-900/30 border-2 border-purple-500'
                : 'bg-white dark:bg-navy-800 border border-gray-200 dark:border-navy-600'
            }`}
          >
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-navy-700 dark:text-white">
                {formatTime(marker.timestamp)}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                (Ad: demo_ad.mp4)
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  onSelectMarker(marker.id);
                  onSeekToMarker(marker.timestamp);
                }}
                className="px-2 py-1 text-xs bg-brand-500 text-white rounded hover:bg-brand-600"
              >
                Go to
              </button>
              <button
                onClick={() => onRemoveMarker(marker.id)}
                className="px-2 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600"
              >
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MarkerList;

