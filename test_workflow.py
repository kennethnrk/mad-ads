#!/usr/bin/env python3
"""Test the complete video processing workflow"""

import requests
import json
import sys

API_BASE = "http://localhost:8000/api/v1"

def test_workflow():
    """Test: Upload video → Transcribe → Summarize → Find ads → Return ranked results"""
    
    print("=" * 60)
    print("Testing Complete Video Processing Workflow")
    print("=" * 60)
    
    # Step 1: Upload and process video
    print("\n[1/3] Uploading video and processing...")
    video_path = "test_vid/videoplayback.mp4"
    
    try:
        with open(video_path, "rb") as f:
            files = {"file": ("videoplayback.mp4", f, "video/mp4")}
            data = {
                "model_size": "tiny",
                "limit": "10"
            }
            
            response = requests.post(
                f"{API_BASE}/video/process-and-match",
                files=files,
                data=data,
                timeout=180  # 3 minutes for transcription
            )
            
            if response.status_code != 200:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                return False
            
            result = response.json()
            
            print("✅ Video processed successfully!")
            print(f"\n📝 Transcription:")
            print(f"   Language: {result['transcription']['language']}")
            print(f"   Duration: {result['transcription']['duration']:.2f}s")
            print(f"   Text preview: {result['transcription']['text'][:100]}...")
            
            print(f"\n🔍 Summary:")
            if result.get('summary'):
                summary = result['summary']
                print(f"   Query: {summary.get('query', 'N/A')}")
                print(f"   Topics: {', '.join(summary.get('topics', [])[:5])}")
                if summary.get('signals'):
                    signals = summary['signals']
                    print(f"   Categories: {', '.join(signals.get('categories', []))}")
                    print(f"   Product Needs: {', '.join(signals.get('product_needs', [])[:3])}")
            
            print(f"\n🎯 Matching Ads Found: {result['count']}")
            
            if result['ads']:
                print("\n📊 Ranked Ads:")
                for ad in result['ads'][:5]:  # Show top 5
                    rank = ad.get('rank', '?')
                    score = ad.get('relevance_score', ad.get('@score', ad.get('score', 'N/A')))
                    name = ad.get('name', ad.get('id', 'Unknown'))
                    category = ad.get('category', 'N/A')
                    print(f"   [{rank}] {name} (Category: {category}, Score: {score})")
            else:
                print("   ⚠️  No ads found. This might indicate:")
                print("      - Snowflake Cortex service not configured")
                print("      - No matching products in database")
                print("      - Connection issues")
            
            print(f"\n✅ Workflow completed successfully!")
            print(f"   Total ads returned: {result['count']}")
            
            return True
            
    except FileNotFoundError:
        print(f"❌ Video file not found: {video_path}")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out (transcription takes time)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_workflow()
    sys.exit(0 if success else 1)

