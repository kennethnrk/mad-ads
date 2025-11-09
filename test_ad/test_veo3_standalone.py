#!/usr/bin/env python3
"""
Standalone Veo3 Video Generation Test Script
Run this to test Gemini Veo3 video generation

Requirements:
    pip install google-genai

Usage:
    python3 test_veo3_standalone.py
"""

import os
import sys
import time
from pathlib import Path

# API Key
API_KEY = "AIzaSyB0Wf27nQYiWtSdgEoRgCzdwBvf9tpNefk"

try:
    from google import genai
except ImportError:
    print("❌ Error: google-genai package not installed")
    print("Please install it with: pip install google-genai")
    sys.exit(1)

def main():
    print("=" * 60)
    print("Veo3 Video Generation Test")
    print("=" * 60)
    print()
    
    # Initialize client
    print("🔑 Initializing Gemini client...")
    try:
        client = genai.Client(api_key=API_KEY)
        print("✅ Client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return False
    
    # Create prompt
    prompt = """A close-up of Versa Gripps weightlifting grips being used on a barbell during a deadlift. 
Professional gym setting with dynamic lighting. Show the secure grip and wrist support features. 
Engaging, cinematic shot suitable for social media advertisement."""
    
    print()
    print("📝 Prompt:")
    print(prompt[:100] + "...")
    print()
    
    # Generate video
    print("🎬 Starting video generation...")
    print("   (This may take 1-3 minutes)")
    print()
    
    try:
        operation = client.models.generate_videos(
            model="veo-3.0-generate-001",
            prompt=prompt,
        )
        
        print(f"✅ Operation started: {operation.name if hasattr(operation, 'name') else 'N/A'}")
        print()
        
        # Poll for completion
        poll_count = 0
        max_polls = 30  # 5 minutes max (30 * 10 seconds)
        
        while not operation.done:
            poll_count += 1
            print(f"⏳ Polling {poll_count}... (waiting for video generation)")
            time.sleep(10)
            
            if poll_count >= max_polls:
                print("❌ Timeout: Video generation took too long")
                return False
            
            # Get updated status
            operation = client.operations.get(operation)
        
        print()
        print("✅ Video generation completed!")
        print()
        
        # Download video
        print("📥 Downloading video...")
        generated_video = operation.response.generated_videos[0]
        client.files.download(file=generated_video.video)
        
        # Save video
        output_dir = Path(__file__).parent / "gen_test"
        output_dir.mkdir(exist_ok=True)
        video_path = output_dir / "veo3_generated_video.mp4"
        generated_video.video.save(str(video_path))
        
        print()
        print("=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print(f"📹 Video saved to: {video_path}")
        print(f"📁 Full path: {video_path.absolute()}")
        print()
        
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        
        # Check if it's a quota error
        if "429" in str(e) or "quota" in str(e).lower() or "RESOURCE_EXHAUSTED" in str(e):
            print("⚠️  This appears to be a quota/rate limit issue.")
            print("   The API key may have exceeded its quota.")
            print("   Check: https://ai.dev/usage?tab=rate-limit")
        elif "400" in str(e):
            print("⚠️  This appears to be a request format issue.")
            print("   The API call structure may need adjustment.")
        
        print()
        import traceback
        print("Full error details:")
        traceback.print_exc()
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

