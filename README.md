# Discord Voice Assistant Bot

A Discord bot that can join voice channels, listen to voice commands, and respond with both text and voice using either Google Search or AI (BLOOMZ) for generating responses.

## Features

- **Voice Commands**: Listen to voice input and respond with voice
- **Dual Search Modes**:
  - Google Search (default): Provides detailed responses with source links
  - AI Mode (BLOOMZ): Generates natural language responses
- **Multilingual Support**: 
  - Brazilian Portuguese (default)
  - English
  - Other languages configurable
- **Automatic Voice Channel Management**:
  - Join/leave voice channels
  - Automatic disconnection after responses
- **Configurable Settings**:
  - Language and region preferences
  - Search mode selection
  - Response length control

## Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
- Discord Bot Token
- Google Custom Search API credentials (for Google Search mode)
- Hugging Face account (for AI mode)

## Installation

1. **Clone the repository**:
   ```bash
   git clone [repository-url]
   cd discord.bot
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg**:
   - Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html)
   - Add FFmpeg to your system PATH

4. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Fill in your credentials:
     ```
     DISCORD_TOKEN=your_bot_token_here
     GOOGLE_API_KEY=your_google_api_key_here
     GOOGLE_CSE_ID=your_custom_search_engine_id_here
     DEFAULT_LANGUAGE=pt-BR
     DEFAULT_REGION=br
     DEFAULT_COUNTRY=BR
     SEARCH_MODE=google
     AI_MODEL=bigscience/bloomz-7b1
     AI_MAX_LENGTH=150
     ```

## Usage

1. **Start the bot**:
   ```bash
   python bot.py
   ```

2. **Discord Commands**:
   - `!join`: Bot joins your voice channel
   - `!leave`: Bot leaves the voice channel
   - `!listen`: Bot listens for your voice command (10 seconds)
   - `!ping`: Check if bot is responsive

3. **Voice Interaction**:
   - Join a voice channel
   - Use `!listen` command
   - Speak your question within 10 seconds
   - Bot will respond with both text and voice

## Search Modes

### Google Search Mode (Default)
- Provides detailed responses with source links
- Supports multiple results
- Requires Google Custom Search API credentials

### AI Mode (BLOOMZ)
- Generates natural language responses
- No API key required
- Runs locally on your machine
- Model size: ~7GB

To switch modes, update `SEARCH_MODE` in `.env`:
- `SEARCH_MODE=google` for Google Search
- `SEARCH_MODE=ai` for BLOOMZ AI

## Language and Region Settings

Configure language and region in `.env`:
```
DEFAULT_LANGUAGE=pt-BR  # Language code
DEFAULT_REGION=br       # Region code
DEFAULT_COUNTRY=BR      # Country code
```

## Performance Notes

- **AI Mode**:
  - Works best with a GPU
  - Falls back to CPU if no GPU available
  - First response might be slower (model warm-up)
  - Model is downloaded only once and reused

- **Google Search Mode**:
  - Faster response times
  - Requires internet connection
  - Subject to API quota limits

## Troubleshooting

1. **Voice Recognition Issues**:
   - Check microphone permissions
   - Ensure clear audio input
   - Verify FFmpeg installation

2. **AI Mode Issues**:
   - Check available disk space
   - Verify GPU compatibility
   - Monitor system resources

3. **Google Search Issues**:
   - Verify API credentials
   - Check API quota limits
   - Ensure internet connection

## Contributing

Feel free to submit issues and enhancement requests!