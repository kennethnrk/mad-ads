/**
 * Semantic matching utility to match ads to transcription segments
 * Places markers at semantically relevant timestamps based on content similarity
 */

/**
 * Extract keywords from an ad for matching
 * Uses product name, category, and any available metadata
 */
const extractAdKeywords = (ad) => {
  const keywords = [];
  
  // Add product name words (most important)
  if (ad.product_name) {
    const productWords = ad.product_name.toLowerCase().split(/\s+/);
    keywords.push(...productWords);
  }
  
  // Add category (important for matching)
  if (ad.category) {
    keywords.push(ad.category.toLowerCase());
    // Also add category words if it's a phrase
    keywords.push(...ad.category.toLowerCase().split(/\s+/));
  }
  
  // Add company name words
  if (ad.company_name) {
    keywords.push(...ad.company_name.toLowerCase().split(/\s+/));
  }
  
  // Remove common stop words and short words
  const stopWords = new Set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were']);
  return keywords
    .filter(word => word.length > 2 && !stopWords.has(word))
    .filter((word, index, self) => self.indexOf(word) === index); // Remove duplicates
};

/**
 * Calculate relevance score between ad keywords and segment text
 * Improved algorithm with better weighting
 */
const calculateRelevanceScore = (adKeywords, segmentText) => {
  if (!segmentText || !adKeywords.length) return 0;
  
  const segmentLower = segmentText.toLowerCase();
  let score = 0;
  let matchedKeywords = 0;
  
  adKeywords.forEach(keyword => {
    // Check for exact word matches (highest weight)
    const wordRegex = new RegExp(`\\b${keyword}\\b`, 'gi');
    const wordMatches = (segmentLower.match(wordRegex) || []).length;
    
    if (wordMatches > 0) {
      // Exact word match - high score
      score += 3 * wordMatches; // Each exact match worth 3 points
      matchedKeywords++;
    } else {
      // Check for partial/substring matches (lower weight)
      const partialMatches = (segmentLower.match(new RegExp(keyword, 'gi')) || []).length;
      if (partialMatches > 0) {
        score += 1 * partialMatches; // Partial matches worth 1 point
        matchedKeywords++;
      }
    }
  });
  
  // Normalize: base score on percentage of keywords matched and frequency
  const keywordMatchRatio = matchedKeywords / adKeywords.length;
  const frequencyScore = Math.min(score / (adKeywords.length * 3), 1); // Max possible is all keywords matched exactly
  
  // Combined score: 60% keyword coverage, 40% frequency
  return (keywordMatchRatio * 0.6) + (frequencyScore * 0.4);
};

/**
 * Find best matching segments for each ad
 * @param {Array} ads - Array of matched ads
 * @param {Array} segments - Array of transcription segments with start, end, text
 * @param {number} maxAds - Maximum number of ads to place
 * @param {Object} summary - Optional summary with topics and signals for better matching
 * @returns {Array} Array of {timestamp, adId, ad, score} objects
 */
export const findSemanticPlacements = (ads, segments, maxAds = 5, summary = null) => {
  if (!ads || !segments || ads.length === 0 || segments.length === 0) {
    return [];
  }
  
  console.log('[SemanticMatching] Finding placements', {
    adsCount: ads.length,
    segmentsCount: segments.length,
    maxAds,
    sampleSegment: segments[0] ? {
      start: segments[0].start,
      end: segments[0].end,
      text: segments[0].text?.substring(0, 50)
    } : null,
    sampleAd: ads[0] ? {
      product_name: ads[0].product_name,
      category: ads[0].category
    } : null
  });
  
  // Limit to top ads
  const topAds = ads.slice(0, maxAds);
  
  // Extract keywords for each ad, enhanced with summary topics if available
  const transcriptionTopics = summary?.topics || summary?.signals?.keywords || [];
  const adsWithKeywords = topAds.map(ad => {
    const baseKeywords = extractAdKeywords(ad);
    
    // Add transcription topics that might relate to this ad
    // This helps match even if exact product name isn't mentioned
    const enhancedKeywords = [...baseKeywords];
    
    // If ad category matches any transcription topics, add those
    if (ad.category) {
      transcriptionTopics.forEach(topic => {
        const topicLower = topic.toLowerCase();
        const categoryLower = ad.category.toLowerCase();
        // If topic contains category or vice versa, add topic words
        if (topicLower.includes(categoryLower) || categoryLower.includes(topicLower)) {
          enhancedKeywords.push(...topic.toLowerCase().split(/\s+/));
        }
      });
    }
    
    return {
      ad,
      keywords: enhancedKeywords.filter((word, index, self) => self.indexOf(word) === index), // Remove duplicates
      id: ad.id || ad.product_name
    };
  });
  
  // Score each segment for each ad
  const placements = [];
  const usedSegments = new Set(); // Track which segments have been used
  
  adsWithKeywords.forEach(({ ad, keywords, id }, adIndex) => {
    let bestSegment = null;
    let bestScore = 0;
    
    segments.forEach((segment, segIndex) => {
      // Handle different segment structures (Whisper can have different formats)
      const segmentText = segment.text || segment.segment || '';
      const segmentStart = segment.start !== undefined ? segment.start : (segment.start_time || 0);
      const segmentEnd = segment.end !== undefined ? segment.end : (segment.end_time || segmentStart);
      
      if (!segmentText.trim()) {
        // Skip empty segments but log for debugging
        if (segIndex < 3) { // Only log first few to avoid spam
          console.log('[SemanticMatching] Empty segment skipped', { segIndex, segment });
        }
        return;
      }
      
      const score = calculateRelevanceScore(keywords, segmentText);
      
      // Lower threshold to catch more matches, but still require some relevance
      // Also consider ad's cosine similarity score if available (boost high-relevance ads)
      const adRelevanceBoost = ad.cosine_similarity || ad.relevance_score || 0;
      const adjustedScore = score * (1 + adRelevanceBoost * 0.2); // Boost up to 20% for highly relevant ads
      
      if (adjustedScore > bestScore && adjustedScore > 0.05) { // Lower threshold to catch more semantic matches
        // Check if this segment is already used (prefer unused segments)
        const segmentKey = `${segmentStart}-${segmentEnd}`;
        const isUsed = Array.from(usedSegments).some(usedIdx => {
          const usedSeg = segments[usedIdx];
          const usedStart = usedSeg.start !== undefined ? usedSeg.start : (usedSeg.start_time || 0);
          const usedEnd = usedSeg.end !== undefined ? usedSeg.end : (usedSeg.end_time || usedStart);
          return Math.abs(usedStart - segmentStart) < 1 && Math.abs(usedEnd - segmentEnd) < 1;
        });
        
        // Only use if not already used, or if score is significantly better
        if (!isUsed || adjustedScore > bestScore + 0.2) {
          bestScore = adjustedScore;
          bestSegment = {
            ...segment,
            start: segmentStart,
            end: segmentEnd,
            text: segmentText
          };
        }
      }
      
      // Debug first few segments for first ad
      if (segIndex < 3 && id === (ads[0]?.id || ads[0]?.product_name)) {
        console.log('[SemanticMatching] Segment score', {
          segIndex,
          score: score.toFixed(3),
          adjustedScore: adjustedScore.toFixed(3),
          text: segmentText.substring(0, 40),
          keywords: keywords.slice(0, 3)
        });
      }
    });
    
    // If no good semantic match, try to find segments with high activity (longer segments = more discussion)
    if (!bestSegment && keywords.length > 0) {
      console.log('[SemanticMatching] No good semantic match found, trying activity-based placement', {
        adName: ad.product_name,
        keywords: keywords.slice(0, 5)
      });
      
      // Find segments with most text (indicates more discussion/important content)
      // But avoid segments already used by other ads
      let bestActivitySegment = null;
      let maxActivity = 0;
      
      segments.forEach((segment, segIdx) => {
        // Skip if this segment was already used
        if (usedSegments.has(segIdx)) return;
        
        const segmentText = segment.text || segment.segment || '';
        const activity = segmentText.length; // Use text length as activity measure
        
        if (activity > maxActivity && segmentText.trim().length > 20) {
          maxActivity = activity;
          bestActivitySegment = { segment, index: segIdx };
        }
      });
      
      if (bestActivitySegment) {
        const segment = bestActivitySegment.segment;
        const segmentStart = segment.start !== undefined 
          ? segment.start 
          : (segment.start_time || 0);
        const segmentEnd = segment.end !== undefined 
          ? segment.end 
          : (segment.end_time || segmentStart);
        const segmentDuration = segmentEnd - segmentStart;
        const timestamp = segmentStart + (segmentDuration > 3 ? segmentDuration / 2 : segmentDuration * 0.3);
        
        bestSegment = {
          ...segment,
          start: segmentStart,
          end: segmentEnd,
          text: segment.text || segment.segment
        };
        bestScore = 0.01; // Low score but still a placement
        usedSegments.add(bestActivitySegment.index); // Mark as used
        
        console.log('[SemanticMatching] Using activity-based placement', {
          adName: ad.product_name,
          timestamp: timestamp.toFixed(2),
          segmentLength: maxActivity
        });
      }
    }
    
    if (bestSegment) {
      // Place marker at the start of the segment, or middle if it's long
      const segmentStart = bestSegment.start !== undefined ? bestSegment.start : 0;
      const segmentEnd = bestSegment.end !== undefined ? bestSegment.end : segmentStart;
      const segmentDuration = segmentEnd - segmentStart;
      // Place at start for short segments, middle for longer ones
      const timestamp = segmentStart + (segmentDuration > 3 ? segmentDuration / 2 : segmentDuration * 0.3);
      
      // Mark this segment as used
      const segmentIndex = segments.findIndex(seg => {
        const segStart = seg.start !== undefined ? seg.start : (seg.start_time || 0);
        return Math.abs(segStart - bestSegment.start) < 0.1;
      });
      if (segmentIndex >= 0) {
        usedSegments.add(segmentIndex);
      }
      
      placements.push({
        timestamp: Math.max(0, timestamp),
        adId: id,
        ad: ad,
        score: bestScore,
        segmentText: bestSegment.text?.substring(0, 100) // For debugging
      });
      
      console.log('[SemanticMatching] Found placement', {
        adName: ad.product_name,
        timestamp: timestamp.toFixed(2),
        score: bestScore.toFixed(2),
        segmentPreview: bestSegment.text?.substring(0, 50)
      });
    }
  });
  
  // Sort by timestamp to avoid overlaps
  placements.sort((a, b) => a.timestamp - b.timestamp);
  
  // Remove placements that are too close together (within 5 seconds)
  // But prioritize higher scoring placements
  const filteredPlacements = [];
  const minGap = 5; // seconds
  
  // Sort by score first (highest first), then by timestamp
  placements.sort((a, b) => {
    if (Math.abs(a.score - b.score) > 0.01) {
      return b.score - a.score; // Higher score first
    }
    return a.timestamp - b.timestamp; // Then by timestamp
  });
  
  placements.forEach(placement => {
    const tooClose = filteredPlacements.some(existing => 
      Math.abs(existing.timestamp - placement.timestamp) < minGap
    );
    
    if (!tooClose) {
      filteredPlacements.push(placement);
    } else {
      // If too close, check if this one has a significantly better score
      const existingPlacement = filteredPlacements.find(existing => 
        Math.abs(existing.timestamp - placement.timestamp) < minGap
      );
      
      if (existingPlacement && placement.score > existingPlacement.score + 0.1) {
        // Replace with better scoring placement
        const index = filteredPlacements.indexOf(existingPlacement);
        filteredPlacements[index] = placement;
        console.log('[SemanticMatching] Replaced placement with better score', {
          oldTimestamp: existingPlacement.timestamp.toFixed(2),
          newTimestamp: placement.timestamp.toFixed(2),
          oldScore: existingPlacement.score.toFixed(2),
          newScore: placement.score.toFixed(2)
        });
      } else {
        console.log('[SemanticMatching] Skipping placement - too close to existing', {
          timestamp: placement.timestamp.toFixed(2),
          adName: placement.ad.product_name,
          score: placement.score.toFixed(2)
        });
      }
    }
  });
  
  // Re-sort by timestamp for final output
  filteredPlacements.sort((a, b) => a.timestamp - b.timestamp);
  
  console.log('[SemanticMatching] Final placements', {
    count: filteredPlacements.length,
    timestamps: filteredPlacements.map(p => p.timestamp.toFixed(2))
  });
  
  return filteredPlacements;
};

/**
 * Fallback: Distribute markers evenly if semantic matching fails
 */
export const createEvenPlacements = (ads, duration, maxAds = 5) => {
  const topAds = ads.slice(0, maxAds);
  const startTime = duration * 0.1;
  const endTime = duration * 0.9;
  const timeRange = endTime - startTime;
  
  return topAds.map((ad, index) => ({
    timestamp: startTime + (timeRange / (topAds.length + 1)) * (index + 1),
    adId: ad.id || ad.product_name,
    ad: ad,
    score: 0,
    segmentText: null
  }));
};

