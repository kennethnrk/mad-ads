"""Video editing service using FFmpeg"""

import os
import subprocess
import tempfile
import shutil
from typing import List, Dict, Any
from app.logging_config import get_logger

logger = get_logger(__name__)


def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds using ffprobe"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
             '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
            capture_output=True,
            text=True,
            check=True
        )
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError) as e:
        logger.error("could_not_get_video_duration", video_path=video_path, error=str(e))
        raise


def normalize_video_segment(input_path: str, output_path: str, fps: int = 30):
    """
    Normalize a video segment to ensure consistent codec, framerate, and sync.
    Re-encodes to ensure audio/video synchronization.
    """
    logger.info("normalizing_video_segment", input_path=input_path, output_path=output_path)
    
    subprocess.run([
        'ffmpeg', '-i', input_path,
        '-c:v', 'libx264',  # Video codec
        '-c:a', 'aac',      # Audio codec
        '-r', str(fps),     # Frame rate
        '-preset', 'medium', # Encoding speed
        '-crf', '23',       # Quality (lower = better, 18-28 is good range)
        '-movflags', '+faststart',  # Web optimization
        '-pix_fmt', 'yuv420p',  # Compatibility
        '-shortest',  # Handle different audio/video durations
        '-y',
        output_path
    ], check=True, capture_output=True, text=True)


def insert_ads_into_video(
    main_video_path: str,
    ad_video_path: str,
    placements: List[Dict[str, Any]],
    output_path: str
) -> None:
    """
    Insert ads into video at specified timestamps.
    Uses re-encoding to ensure audio/video sync.
    
    Args:
        main_video_path: Path to main video file
        ad_video_path: Path to ad video file
        placements: List of {timestamp: float, ad_id: Optional[str]} dicts
        output_path: Path where output video will be saved
    """
    logger.info("insert_ads_into_video", 
                main_video=main_video_path,
                ad_video=ad_video_path,
                placement_count=len(placements),
                output=output_path)
    
    # Check if ffmpeg is available
    if not shutil.which('ffmpeg'):
        raise RuntimeError("FFmpeg is not installed")
    
    # Get video duration
    video_duration = get_video_duration(main_video_path)
    
    # Sort placements by timestamp
    def get_timestamp(p):
        return p['timestamp'] if isinstance(p, dict) else p.timestamp
    
    sorted_placements = sorted(placements, key=get_timestamp)
    
    # Validate timestamps
    for placement in sorted_placements:
        timestamp = placement['timestamp'] if isinstance(placement, dict) else placement.timestamp
        if timestamp >= video_duration:
            raise ValueError(f"Timestamp {timestamp}s exceeds video duration {video_duration:.2f}s")
    
    # Create temp directory for segments
    temp_dir = tempfile.mkdtemp()
    normalized_segments = []
    last_timestamp = 0.0
    
    try:
        # Process each placement
        for idx, placement in enumerate(sorted_placements):
            timestamp = placement['timestamp'] if isinstance(placement, dict) else placement.timestamp
            logger.info("processing_placement", index=idx, timestamp=timestamp)
            
            # Extract and normalize segment from last insertion point to current timestamp
            if timestamp > last_timestamp:
                raw_segment = os.path.join(temp_dir, f"raw_segment_{idx}.mp4")
                normalized_segment = os.path.join(temp_dir, f"segment_{idx}.mp4")
                
                # Extract raw segment
                start_time = last_timestamp
                duration = timestamp - last_timestamp
                
                subprocess.run([
                    'ffmpeg', '-i', main_video_path,
                    '-ss', str(start_time),
                    '-t', str(duration),
                    '-c', 'copy',  # Fast extraction
                    '-y',
                    raw_segment
                ], check=True, capture_output=True, text=True)
                
                # Normalize segment for sync
                normalize_video_segment(raw_segment, normalized_segment)
                normalized_segments.append(normalized_segment)
            
            # Normalize ad segment
            normalized_ad = os.path.join(temp_dir, f"ad_{idx}.mp4")
            normalize_video_segment(ad_video_path, normalized_ad)
            normalized_segments.append(normalized_ad)
            
            last_timestamp = timestamp
        
        # Extract and normalize final segment (from last insertion to end)
        if last_timestamp < video_duration:
            raw_final = os.path.join(temp_dir, "raw_final.mp4")
            normalized_final = os.path.join(temp_dir, "final.mp4")
            
            subprocess.run([
                'ffmpeg', '-i', main_video_path,
                '-ss', str(last_timestamp),
                '-c', 'copy',
                '-y',
                raw_final
            ], check=True, capture_output=True, text=True)
            
            normalize_video_segment(raw_final, normalized_final)
            normalized_segments.append(normalized_final)
        
        # Create concat list file
        concat_list = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_list, 'w') as f:
            for segment in normalized_segments:
                f.write(f"file '{os.path.abspath(segment)}'\n")
        
        # Concatenate all normalized segments
        # Since all segments are normalized, we can use copy for faster concatenation
        logger.info("concatenating_segments", segment_count=len(normalized_segments))
        subprocess.run([
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_list,
            '-c', 'copy',  # Safe to copy since all segments are normalized
            '-y',
            output_path
        ], check=True, capture_output=True, text=True)
        
        logger.info("ad_insertion_completed", output_path=output_path, placement_count=len(sorted_placements))
        
    except subprocess.CalledProcessError as e:
        logger.error("ffmpeg_error", error=str(e.stderr), stdout=str(e.stdout))
        raise RuntimeError(f"FFmpeg error: {e.stderr}")
    finally:
        # Cleanup temp directory (optional - can keep for debugging)
        # shutil.rmtree(temp_dir, ignore_errors=True)
        pass

