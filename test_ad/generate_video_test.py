#!/usr/bin/env python3
"""
Test script to generate a video ad using Gemini Veo3
Takes image and text from test_ad folder and generates a video
Uses the correct Veo3 API from google.genai
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

from google import genai
from PIL import Image

def generate_video_with_veo3(image_path: str, text_prompt: str, output_dir: str):
    """
    Generate a video using Gemini Veo3 from an image and text prompt
    
    Args:
        image_path: Path to the product image
        text_prompt: Text description/prompt for the video
        output_dir: Directory to save the generated video
    """
    print(f"Loading image from: {image_path}")
    print(f"Text prompt: {text_prompt[:100]}...")
    
    # Use provided API key or fallback to env var
    gemini_api_key = os.getenv("GEMINI_API_KEY") or "AIzaSyA_Fo89_kwjvtzzxgIL-lDs0JPKvPSQFTk"
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not set")
    
    # Initialize the client
    client = genai.Client(api_key=gemini_api_key)
    
    # Load the image file
    print(f"Loading image from: {image_path}")
    pil_image = Image.open(image_path)
    print(f"Image loaded: {pil_image.size}")
    
    # Approach: Follow the example pattern - generate an image first, then use it
    # Step 1: Upload the image file with explicit mime type in config
    print("Uploading image file...")
    from google.genai import types
    upload_config = types.UploadFileConfig(mime_type="image/jpeg")
    with open(image_path, 'rb') as f:
        uploaded_file = client.files.upload(file=f, config=upload_config)
    print(f"Image uploaded: {uploaded_file.name}")
    
    # Step 2: Follow the example pattern exactly
    # In the example: image = generate_content(...), then image.parts[0].as_image()
    # We need to create a content response that has parts with as_image() method
    print("Processing image for Veo3 (following example pattern)...")
    try:
        # Create a content object with our uploaded file
        # Then try to use parts[0].as_image() like in the example
        from google.genai import types as genai_types
        
        # Try creating a Content object with the uploaded file
        # The example shows: image.parts[0].as_image()
        # So we need a response-like object with parts that have as_image()
        
        # Alternative: Try using the file URI to create a Part, then see if it has as_image()
        part_from_uri = types.Part.from_uri(file_uri=uploaded_file.uri, mime_type="image/jpeg")
        
        # Check if the part has as_image() method
        if hasattr(part_from_uri, 'as_image'):
            image_data = part_from_uri.as_image()
            print("Using part.as_image() method")
        else:
            # Try creating a mock content response structure
            # Or just use the part directly
            image_data = part_from_uri
            print(f"Using Part.from_uri: {uploaded_file.uri}")
        
    except Exception as e:
        print(f"Error processing image: {e}")
        import traceback
        traceback.print_exc()
        # Fallback: try without image
        image_data = None
    
    # Create a prompt for video generation
    video_prompt = f"""Create a short product advertisement video (5-8 seconds) for Versa Gripps.

Product: {text_prompt}

Video should show:
- The product being used in a fitness/weightlifting context
- Highlight key features: grip enhancement, wrist support, safety quick-release
- Professional, engaging, suitable for social media
- Focus on benefits for athletes and weightlifters
- Dynamic and visually appealing
"""
    
    print("\nGenerating video with Veo3...")
    print(f"Prompt: {video_prompt[:200]}...")
    
    try:
        # Generate video with Veo3
        # Model options: "veo-3.0-generate-001" or "veo-3.1-generate-preview"
        print("\nStarting video generation operation...")
        
        # Build the call - include image if available
        generate_kwargs = {
            "model": "veo-3.0-generate-001",  # or "veo-3.1-generate-preview"
            "prompt": video_prompt,
        }
        
        # Add image if we have it
        if image_data:
            print(f"Using image in video generation: {type(image_data)}")
            generate_kwargs["image"] = image_data
        else:
            print("Generating video without image (text prompt only)")
        
        operation = client.models.generate_videos(**generate_kwargs)
        
        print(f"Operation started: {operation.name if hasattr(operation, 'name') else 'N/A'}")
        
        # Poll the operation status until the video is ready
        poll_count = 0
        max_polls = 60  # Maximum 10 minutes (60 * 10 seconds)
        
        while not operation.done:
            poll_count += 1
            print(f"Polling {poll_count}... Waiting for video generation to complete...")
            time.sleep(10)
            
            if poll_count >= max_polls:
                raise TimeoutError("Video generation timed out after 10 minutes")
            
            # Get updated operation status
            operation = client.operations.get(operation)
        
        print("\n✅ Video generation completed!")
        
        # Download the generated video
        generated_video = operation.response.generated_videos[0]
        print(f"Downloading video...")
        
        # Download the video file
        client.files.download(file=generated_video.video)
        
        # Save the video
        video_path = os.path.join(output_dir, "generated_ad.mp4")
        generated_video.video.save(video_path)
        
        print(f"✅ Video saved to: {video_path}")
        
        # Also save metadata
        metadata_file = os.path.join(output_dir, "video_metadata.txt")
        with open(metadata_file, "w", encoding="utf-8") as f:
            f.write(f"Prompt: {video_prompt}\n\n")
            f.write(f"Operation Name: {operation.name if hasattr(operation, 'name') else 'N/A'}\n")
            f.write(f"Video File: {video_path}\n")
            if hasattr(generated_video, 'duration'):
                f.write(f"Duration: {generated_video.duration}\n")
        
        return video_path
        
    except Exception as e:
        print(f"\n❌ Error generating video: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        # Save error for debugging
        error_file = os.path.join(output_dir, "error.txt")
        with open(error_file, "w") as f:
            f.write(f"Error: {str(e)}\n\n")
            f.write(traceback.format_exc())
        
        raise


def main():
    """Main function"""
    # Get paths
    script_dir = Path(__file__).parent
    image_path = script_dir / "check.jpg"
    text_path = script_dir / "add.txt"
    output_dir = script_dir / "gen_test"
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    # Read text
    print("Reading product text...")
    with open(text_path, "r", encoding="utf-8") as f:
        product_text = f.read()
    
    print(f"Product text length: {len(product_text)} characters")
    
    # Generate video
    try:
        video_path = generate_video_with_veo3(
            str(image_path),
            product_text,
            str(output_dir)
        )
        print("\n" + "="*50)
        print("✅ Video generation test completed successfully!")
        print(f"📹 Video saved to: {video_path}")
        print(f"📁 Check output in: {output_dir}")
        print("="*50)
    except Exception as e:
        print("\n" + "="*50)
        print(f"❌ Test failed: {e}")
        print(f"📁 Error details saved to: {output_dir}/error.txt")
        print("="*50)
        sys.exit(1)


if __name__ == "__main__":
    main()
