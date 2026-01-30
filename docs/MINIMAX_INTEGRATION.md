# MiniMax Image Generation Integration

## Overview
Added AI image generation capability to event creation using MiniMax API.

## Features

### 1. Auto-generate images on event creation
When creating an event, set `generate_image: true` to automatically generate an event image:
```json
{
  "title": "AI Workshop",
  "description": "Learn about AI",
  "topic": "Artificial Intelligence",
  "generate_image": true
}
```

### 2. Generate images for existing events
Use the new endpoint to generate images for events:
```
POST /events/{event_id}/generate-image
```

### 3. Image storage
Generated images are stored as base64 data URLs in the `image_url` field of the event.

## API Endpoints

### Create Event with Image Generation
```bash
POST /events/
{
  "title": "Event Title",
  "description": "Event description",
  "topic": "Event topic",
  "generate_image": true  # Optional, defaults to false
}
```

### Generate Image for Existing Event
```bash
POST /events/{event_id}/generate-image
```

## Configuration

### Set MiniMax API Key
Add your MiniMax API key to the `.env` file:
```
MINIMAX_API_KEY=your-api-key-here
```

Get your API key from: https://platform.minimax.io/

## MiniMax API Details

### Endpoint
```
https://api.minimax.io/v1/image_generation
```

### Parameters
- `model`: "image-01"
- `prompt`: Detailed description of the image
- `aspect_ratio`: "16:9" (default)
- `response_format`: "base64"

### Example Response
```json
{
  "data": {
    "image_base64": ["base64-encoded-image-data"]
  }
}
```

## Database Changes

Added `image_url` column to the `events` table:
- Type: VARCHAR(500)
- Stores base64 data URLs
- Nullable (null if no image generated)

## Files Modified

1. **app/models/database_models.py**
   - Added `image_url` column to Event model

2. **app/database/schemas.py**
   - Added `generate_image` field to EventCreate
   - Added `image_url` field to EventResponse

3. **app/routers/events.py**
   - Added image generation to create_event
   - Added POST /events/{event_id}/generate-image endpoint
   - Updated dependencies to bypass auth in dev mode

4. **app/services/minimax_service.py** (NEW)
   - Created MiniMax image generation service
   - `generate_event_image()` function
   - `generate_image_prompt()` helper function

## Error Handling

- If no API key configured: Returns error message
- If API call fails: Returns error message
- Images stored as base64 data URLs for immediate use

## Testing

Test the endpoints:
```bash
# List events
curl http://localhost:8000/events/

# Create event with image
curl -X POST http://localhost:8000/events/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Event","generate_image":true}'

# Generate image for existing event
curl -X POST http://localhost:8000/events/1/generate-image
```

## Notes

- MiniMax API is paid service - check pricing at https://platform.minimax.io/
- Generated images are high-quality, photorealistic
- Supports 16:9 aspect ratio (default)
- Response format is base64 for immediate use
