import { useState, useCallback } from 'react';

/**
 * Custom hook for managing video timeline markers
 */
export const useMarkers = () => {
  const [markers, setMarkers] = useState([]);
  const [selectedMarker, setSelectedMarker] = useState(null);

  const addMarker = useCallback((timestamp, adId = null) => {
    const newMarker = {
      id: Date.now() + Math.random(),
      timestamp: Math.max(0, timestamp),
      adId,
    };
    setMarkers(prev => [...prev, newMarker].sort((a, b) => a.timestamp - b.timestamp));
    setSelectedMarker(newMarker.id);
    return newMarker.id;
  }, []);

  const removeMarker = useCallback((id) => {
    setMarkers(prev => prev.filter(m => m.id !== id));
    if (selectedMarker === id) {
      setSelectedMarker(null);
    }
  }, [selectedMarker]);

  const selectMarker = useCallback((id) => {
    setSelectedMarker(id);
    return markers.find(m => m.id === id);
  }, [markers]);

  const clearMarkers = useCallback(() => {
    setMarkers([]);
    setSelectedMarker(null);
  }, []);

  return {
    markers,
    selectedMarker,
    addMarker,
    removeMarker,
    selectMarker,
    clearMarkers,
  };
};

