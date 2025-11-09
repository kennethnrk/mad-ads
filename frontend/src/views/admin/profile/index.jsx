import Banner from "./components/Banner";
import Storage from "./components/Storage";
import Upload from "./components/Upload";
import MatchedAds from "./components/MatchedAds";
import AdInsertion from "./components/ad-insertion/AdInsertion";
import { useState } from "react";

const AdStudio = () => {
  const [uploadResults, setUploadResults] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  console.log('[AdStudio] Component rendered', { 
    hasResults: !!uploadResults, 
    loading: uploadLoading, 
    error: uploadError 
  });

  // This will be passed down to Upload component via props in future
  // For now, we'll handle it via state management
  const handleUploadComplete = (results) => {
    console.log('[AdStudio] Upload completed', { adsCount: results?.count });
    setUploadResults(results);
    setUploadLoading(false);
    setUploadError(null);
  };

  const handleUploadStart = () => {
    console.log('[AdStudio] Upload started');
    setUploadLoading(true);
    setUploadError(null);
    setUploadResults(null);
  };

  const handleUploadError = (error) => {
    console.error('[AdStudio] Upload error', error);
    setUploadError(error);
    setUploadLoading(false);
  };

  return (
    <div className="flex w-full flex-col gap-5">
      <div className="w-full mt-3 flex h-fit flex-col gap-5 lg:grid lg:grid-cols-12">
        <div className="col-span-4 lg:!mb-0">
          <Banner />
        </div>

        <div className="col-span-3 lg:!mb-0">
          <Storage />
        </div>

        <div className="col-span-5 lg:!mb-0">
          {/* Placeholder for future content */}
        </div>
      </div>

      {/* Video Upload Section - New Line */}
      <div className="w-full">
        <Upload 
          onUploadStart={handleUploadStart}
          onUploadComplete={handleUploadComplete}
          onUploadError={handleUploadError}
        />
      </div>

      {/* Matched Ads Section */}
      {uploadResults && (
        <div className="w-full">
          <MatchedAds 
            ads={uploadResults.ads || []} 
            loading={uploadLoading}
            error={uploadError}
            summary={uploadResults.summary}
            transcription={uploadResults.transcription}
            videoFile={uploadResults.videoFile}
          />
        </div>
      )}

      {/* Ad Insertion Section - Always visible for testing with hardcoded videos */}
      <div className="w-full">
        <AdInsertion 
          transcription={uploadResults?.transcription}
          videoFile={uploadResults?.videoFile}
        />
      </div>
    </div>
  );
};

export default AdStudio;
