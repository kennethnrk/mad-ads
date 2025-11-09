import { MdFileUpload, MdVideoLibrary } from "react-icons/md";
import Card from "components/card";
import React, { useState, useRef } from "react";
import { processVideoAndMatch } from "services/api";

const Upload = ({ onUploadStart, onUploadComplete, onUploadError }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  console.log('[Upload] Component rendered', { uploading, hasResults: !!results, error });

  const handleFileSelect = async (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      console.log('[Upload] No file selected');
      return;
    }

    console.log('[Upload] File selected', { 
      name: file.name, 
      size: file.size, 
      type: file.type 
    });

    // Validate file type
    const validTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo'];
    const validExtensions = ['.mp4', '.avi', '.mov'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!validTypes.includes(file.type) && !validExtensions.includes(fileExtension)) {
      const errorMsg = 'Please upload a valid video file (MP4, AVI, or MOV)';
      console.error('[Upload] Invalid file type', { type: file.type, extension: fileExtension });
      setError(errorMsg);
      return;
    }

    setError(null);
    setUploading(true);
    setUploadProgress(0);
    setResults(null);
    
    // Notify parent component
    onUploadStart?.();

    try {
      console.log('[Upload] Starting video processing...');
      
      // Simulate progress for better UX (actual progress would come from server)
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 500);

      const result = await processVideoAndMatch(file, {
        model_size: 'tiny', // Use tiny for faster processing
        limit: 10
      });

      clearInterval(progressInterval);
      setUploadProgress(100);
      
      console.log('[Upload] Video processing completed', {
        success: result.success,
        adsCount: result.count,
        transcriptionLength: result.transcription?.text?.length
      });

      // Store file reference for thumbnail
      const resultWithFile = {
        ...result,
        videoFile: file
      };
      setResults(resultWithFile);
      console.log(resultWithFile);
      onUploadComplete?.(resultWithFile);
    } catch (err) {
      console.error('[Upload] Video processing error', err);
      const errorMessage = err.message || 'Failed to process video. Please try again.';
      setError(errorMessage);
      setUploadProgress(0);
      onUploadError?.(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  const handleUploadClick = () => {
    console.log('[Upload] Upload button clicked');
    fileInputRef.current?.click();
  };

  const handleReset = () => {
    console.log('[Upload] Resetting upload state');
    setResults(null);
    setError(null);
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Card className="grid h-full w-full grid-cols-1 gap-3 rounded-[20px] bg-white bg-clip-border p-3 font-dm shadow-3xl shadow-shadow-500 dark:!bg-navy-800 dark:shadow-none 2xl:grid-cols-11">
      <div className="col-span-5 h-full w-full rounded-xl bg-lightPrimary dark:!bg-navy-700 2xl:col-span-6">
        <input
          ref={fileInputRef}
          type="file"
          accept="video/mp4,video/avi,video/quicktime,video/x-msvideo,.mp4,.avi,.mov"
          onChange={handleFileSelect}
          className="hidden"
          disabled={uploading}
        />
        <button
          onClick={handleUploadClick}
          disabled={uploading}
          className="flex h-full w-full flex-col items-center justify-center rounded-xl border-[2px] border-dashed border-gray-200 py-3 dark:!border-navy-700 lg:pb-0 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {uploading ? (
            <>
              <div className="mb-4 h-16 w-16 animate-spin rounded-full border-4 border-solid border-brand-500 border-t-transparent"></div>
              <h4 className="text-xl font-bold text-brand-500 dark:text-white">
                Processing...
              </h4>
              <p className="mt-2 text-sm font-medium text-gray-600">
                {uploadProgress}% - Transcribing and finding matches
              </p>
            </>
          ) : results ? (
            <>
              <MdVideoLibrary className="text-[80px] text-green-500 dark:text-green-400" />
              <h4 className="text-xl font-bold text-green-500 dark:text-green-400">
                Video Processed!
              </h4>
              <p className="mt-2 text-sm font-medium text-gray-600">
                {results.count} ads matched
              </p>
              <div
                onClick={(e) => {
                  e.stopPropagation();
                  handleReset();
                }}
                className="mt-4 cursor-pointer rounded-lg bg-brand-500 px-4 py-2 text-center text-sm font-medium text-white hover:bg-brand-600"
              >
                Upload Another
              </div>
            </>
          ) : (
            <>
              <MdFileUpload className="text-[80px] text-brand-500 dark:text-white" />
              <h4 className="text-xl font-bold text-brand-500 dark:text-white">
                Upload Videos
              </h4>
              <p className="mt-2 text-sm font-medium text-gray-600">
                MP4, AVI, and MOV files are allowed
              </p>
            </>
          )}
        </button>
      </div>

      <div className="col-span-5 flex h-full w-full flex-col justify-center overflow-hidden rounded-xl bg-white pl-3 pb-4 dark:!bg-navy-800">
        <h5 className="text-left text-xl font-bold leading-9 text-navy-700 dark:text-white">
          {results ? 'Processing Complete' : 'Upload your Product Details'}
        </h5>
        <p className="leading-1 mt-2 text-base font-normal text-gray-600">
          {results
            ? `Found ${results.count} matching ads for your video content.`
            : 'Upload a video to automatically find matching product ads using AI.'}
        </p>
        {results && results.videoFile && (
          <div className="mt-4">
            <p className="mb-2 text-xs font-semibold text-gray-600 dark:text-gray-400">
              Video Thumbnail:
            </p>
            <video
              src={URL.createObjectURL(results.videoFile)}
              className="w-full rounded-lg"
              controls={false}
              muted
              style={{ maxHeight: '200px', objectFit: 'cover' }}
            />
          </div>
        )}
        {results && results.summary?.embedding_query && (
          <div className="mt-4 rounded-lg bg-gray-50 p-3 dark:bg-navy-700">
            <p className="text-xs font-semibold text-gray-600 dark:text-gray-400">
              LLM Summary (Used for Matching):
            </p>
            <p className="mt-1 text-sm text-gray-700 dark:text-gray-300">
              {results.summary.embedding_query.length > 200 
                ? `${results.summary.embedding_query.substring(0, 200)}...` 
                : results.summary.embedding_query}
            </p>
          </div>
        )}
        {!results && (
          <button
            onClick={handleUploadClick}
            disabled={uploading}
            className="linear mt-4 flex items-center justify-center rounded-xl bg-brand-500 px-2 py-2 text-base font-medium text-white transition duration-200 hover:bg-brand-600 active:bg-brand-700 dark:bg-brand-400 dark:text-white dark:hover:bg-brand-300 dark:active:bg-brand-200 disabled:opacity-50"
          >
            {uploading ? 'Processing...' : 'Upload Video'}
          </button>
        )}
      </div>
    </Card>
  );
};

export default Upload;
