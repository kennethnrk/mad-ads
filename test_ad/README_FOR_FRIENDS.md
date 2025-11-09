# Veo3 Video Generation Test Script

## Quick Start

### 1. Install Requirements
```bash
pip install google-genai
```

### 2. Run the Script
```bash
python3 test_veo3_standalone.py
```

That's it! The script will:
- Generate a video using Gemini Veo3
- Save it to `gen_test/veo3_generated_video.mp4`
- Show progress and any errors

## What It Does

The script generates a short product advertisement video (5-8 seconds) for Versa Gripps weightlifting grips using text-to-video generation.

## Expected Output

If successful:
```
✅ Video saved to: gen_test/veo3_generated_video.mp4
```

If there's an error:
- **429 Quota Error**: API key has exceeded quota (wait or check billing)
- **400 Format Error**: API call structure issue
- **Other**: Check the error message

## Notes

- Video generation typically takes 1-3 minutes
- The script polls every 10 seconds for completion
- Maximum wait time is 5 minutes

## Troubleshooting

**"google-genai package not installed"**
```bash
pip install google-genai
```

**"429 RESOURCE_EXHAUSTED"**
- API key quota exceeded
- Wait for quota reset or check billing

**Script hangs**
- Video generation can take time
- Wait up to 5 minutes
- Check your internet connection

