#!/usr/bin/env python3
"""
Simplified test - try video generation without image first to verify API works
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from google import genai

def test_video_generation():
    # Use provided API key or fallback to env var
    gemini_api_key = "AIzaSyB0Wf27nQYiWtSdgEoRgCzdwBvf9tpNefk" or os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not set")
    
    client = genai.Client(api_key=gemini_api_key)
    
    # Read product description for better prompt
    script_dir = Path(__file__).parent
    text_path = script_dir / "add.txt"
    product_text = ""
    if text_path.exists():
        with open(text_path, "r", encoding="utf-8") as f:
            product_text = f.read()
    
    # Test 1: Generate video without image (text only)
    print("Test 1: Generating video with text prompt only...")
    prompt = f"""Create a short product advertisement video (5-8 seconds) for Versa Gripps weightlifting grips.

Product: {product_text[:500] if product_text else 'Versa Gripps are self-supporting grip aids for weightlifting'}

Video should show:
- The product being used in a fitness/weightlifting context
- Professional gym setting with dynamic lighting
- Highlight key features: grip enhancement, wrist support, safety quick-release
- Engaging and suitable for social media"""
    
    try:
        operation = client.models.generate_videos(
            model="veo-3.0-generate-001",
            prompt=prompt,
        )
        
        print(f"Operation started, polling for completion...")
        poll_count = 0
        while not operation.done:
            poll_count += 1
            print(f"Polling {poll_count}...")
            time.sleep(10)
            operation = client.operations.get(operation)
        
        print("✅ Video generation completed!")
        
        # Download video
        generated_video = operation.response.generated_videos[0]
        client.files.download(file=generated_video.video)
        
        output_dir = Path(__file__).parent / "gen_test"
        output_dir.mkdir(exist_ok=True)
        video_path = output_dir / "test_video_text_only.mp4"
        generated_video.video.save(str(video_path))
        
        print(f"✅ Video saved to: {video_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_video_generation()

