import { useState, useCallback } from 'react';
import { insertAdIntoVideo } from 'services/api';

/**
 * Custom hook for managing video generation
 */
export const useVideoGeneration = () => {
  const [generating, setGenerating] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);
  const [previewTimestamp, setPreviewTimestamp] = useState(0);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const generateVideo = useCallback(async (markers) => {
    if (markers.length === 0) {
      setError("Please add at least one marker before generating");
      return;
    }

    setGenerating(true);
    setError(null);
    setSuccess(null);
    setPreviewMode(false);

    try {
      const result = await insertAdIntoVideo(markers);
      setSuccess(result);
      // Small delay to ensure backend has finished writing the file
      // Update timestamp to force cache bust
      setTimeout(() => {
        setPreviewTimestamp(Date.now());
        setPreviewMode(true);
      }, 500);
    } catch (err) {
      console.error("Ad insertion error:", err);
      setError(err.message || "Failed to generate video");
    } finally {
      setGenerating(false);
    }
  }, []);

  const resetPreview = useCallback(() => {
    setPreviewMode(false);
    setSuccess(null);
    setError(null);
  }, []);

  return {
    generating,
    previewMode,
    previewTimestamp,
    error,
    success,
    generateVideo,
    resetPreview,
  };
};

