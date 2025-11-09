import React from "react";
import Card from "components/card";

const MatchedAds = ({ ads, loading, error, summary, transcription }) => {
  console.log('[MatchedAds] Rendering', { 
    adsCount: ads?.length, 
    loading, 
    error,
    hasSummary: !!summary,
    hasTranscription: !!transcription
  });

  if (loading) {
    return (
      <Card extra="w-full p-4">
        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-brand-500 border-r-transparent"></div>
            <p className="mt-4 text-sm text-gray-600">Finding matching ads...</p>
          </div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card extra="w-full p-4">
        <div className="rounded-lg bg-red-50 p-4 dark:bg-red-900/20">
          <p className="text-red-800 dark:text-red-200">
            <strong>Error:</strong> {error}
          </p>
        </div>
      </Card>
    );
  }

  if (!ads || ads.length === 0) {
    return (
      <Card extra="w-full p-4">
        <h5 className="mb-4 text-xl font-bold text-navy-700 dark:text-white">
          Matched Ads
        </h5>
        <p className="text-gray-600 dark:text-gray-400">No ads found. Upload a video to find matches.</p>
      </Card>
    );
  }

  return (
    <Card extra="w-full p-4">
      <div className="mb-4 flex items-center justify-between">
        <h5 className="text-xl font-bold text-navy-700 dark:text-white">
          Matched Ads ({ads.length})
        </h5>
        {summary?.query && (
          <span className="text-xs text-gray-500 dark:text-gray-400">
            Query: "{summary.query}"
          </span>
        )}
      </div>
      <div className="space-y-3">
        {ads.map((ad, index) => {
          const score = ad.relevance_score || ad['@scores']?.cosine_similarity || ad.score || 0;
          const name = ad.name || ad.EMBEDDED_TEXT?.substring(0, 50) || ad.id || 'Unknown Product';
          const category = ad.category || 'Uncategorized';
          const description = ad.description || ad.EMBEDDED_TEXT || '';
          const company = ad.company || ad.brand || ad.manufacturer || null;
          const product = ad.product || ad.product_name || null;
          const productDescription = ad.product_description || ad.description || ad.EMBEDDED_TEXT || '';
          const price = ad.price || null;
          const imageUrl = ad.image_url || ad.image || null;
          
          console.log(`[MatchedAds] Rendering ad ${index + 1}`, { 
            rank: ad.rank, 
            score, 
            name: name.substring(0, 30),
            hasCompany: !!company,
            hasProduct: !!product,
            hasDescription: !!productDescription,
            hasPrice: !!price,
            hasImage: !!imageUrl,
            allKeys: Object.keys(ad)
          });

          return (
            <div
              key={ad.id || index}
              className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm dark:border-navy-700 dark:bg-navy-800"
            >
              <div className="flex items-start gap-4">
                {imageUrl && (
                  <div className="flex-shrink-0">
                    <img
                      src={imageUrl}
                      alt={name}
                      className="h-20 w-20 rounded-lg object-cover"
                      onError={(e) => {
                        console.error(`[MatchedAds] Image load error for ad ${index + 1}`, imageUrl);
                        e.target.style.display = 'none';
                      }}
                    />
                  </div>
                )}
                <div className="flex-1">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-semibold text-brand-500">
                          #{ad.rank || index + 1}
                        </span>
                        <h6 className="text-base font-bold text-navy-700 dark:text-white">
                          {name}
                        </h6>
                      </div>
                      
                      {company && (
                        <p className="mt-1 text-sm font-semibold text-gray-700 dark:text-gray-300">
                          Company: {company}
                        </p>
                      )}
                      
                      {product && (
                        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                          Product: {product}
                        </p>
                      )}
                      
                      <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                        Category: {category}
                      </p>
                      
                      {productDescription && (
                        <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
                          {productDescription.length > 150 
                            ? `${productDescription.substring(0, 150)}...` 
                            : productDescription}
                        </p>
                      )}
                      
                      {price && (
                        <p className="mt-2 text-sm font-semibold text-navy-700 dark:text-white">
                          Price: ${price}
                        </p>
                      )}
                      
                      {/* Show all available metadata for debugging */}
                      {process.env.NODE_ENV === 'development' && (
                        <details className="mt-2">
                          <summary className="cursor-pointer text-xs text-gray-400">
                            Debug: All Metadata
                          </summary>
                          <pre className="mt-2 max-h-40 overflow-auto rounded bg-gray-100 p-2 text-xs dark:bg-navy-900">
                            {JSON.stringify(ad, null, 2)}
                          </pre>
                        </details>
                      )}
                    </div>
                    <div className="ml-4 text-right">
                      <div className="rounded-full bg-brand-500 px-3 py-1 text-xs font-bold text-white">
                        {(score * 100).toFixed(0)}%
                      </div>
                      <p className="mt-1 text-xs text-gray-500">Match</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
};

export default MatchedAds;

