import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
import tempfile
import asyncio
import requests
from datetime import datetime, timedelta
import json
import logging
import time
from langdetect import detect, DetectorFactory
from search_providers import GoogleSearchProvider, BloomzSearchProvider

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Language and Region Settings
DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'pt-BR')
DEFAULT_REGION = os.getenv('DEFAULT_REGION', 'br')
DEFAULT_COUNTRY = os.getenv('DEFAULT_COUNTRY', 'BR')

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize search providers
search_mode = os.getenv('SEARCH_MODE', 'google')
search_provider = BloomzSearchProvider() if search_mode == 'ai' else GoogleSearchProvider()

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

# Initialize speech recognition
recognizer = sr.Recognizer()
recognizer.energy_threshold = 4000
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8

# Voice state tracking
voice_client = None
recording = False
last_command_time = None

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print('------')
    print(f'Language: {DEFAULT_LANGUAGE}')
    print(f'Region: {DEFAULT_REGION}')
    print(f'Country: {DEFAULT_COUNTRY}')
    logger.info(f'Bot is ready! Logged in as {bot.user.name}')
    logger.info(f'Search mode: {search_mode}')
    logger.info(f'Language: {os.getenv("DEFAULT_LANGUAGE")}')
    logger.info(f'Region: {os.getenv("DEFAULT_REGION")}')
    logger.info(f'Country: {os.getenv("DEFAULT_COUNTRY")}')

@bot.command(name='join')
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel first!")
        return

    channel = ctx.author.voice.channel
    await channel.connect()
    await ctx.send(f"Joined {channel.name}")

@bot.command(name='leave')
async def leave(ctx):
    if not ctx.voice_client:
        await ctx.send("I'm not in a voice channel!")
        return

    await ctx.voice_client.disconnect()
    await ctx.send("Left the voice channel")

@bot.command(name='listen')
async def listen(ctx):
    if not ctx.voice_client:
        await ctx.send("You need to be in a voice channel first!")
        return

    await ctx.send("Listening... (10 seconds)")
    
    # Create a temporary file for audio
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        temp_filename = temp_file.name

    try:
        # Record audio
        source = ctx.voice_client.source
        audio_data = await source.read()
        
        # Save audio to temporary file
        with open(temp_filename, 'wb') as f:
            f.write(audio_data)

        # Recognize speech
        with sr.AudioFile(temp_filename) as source:
            audio = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio, language='pt-BR')
                await ctx.send(f"You said: {text}")
                
                # Process the command
                text_response, voice_response = await process_command(text)
                
                # Send text response
                await ctx.send(text_response)
                
                # Convert response to speech
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    response_filename = temp_file.name
                
                engine.save_to_file(voice_response, response_filename)
                engine.runAndWait()
                
                # Play the response
                ctx.voice_client.play(discord.FFmpegPCMAudio(response_filename))
                
            except sr.UnknownValueError:
                await ctx.send("Sorry, I couldn't understand that.")
            except sr.RequestError as e:
                await ctx.send(f"Sorry, there was an error with the speech recognition service: {e}")
            except Exception as e:
                await ctx.send(f"An error occurred: {e}")
    
    finally:
        # Clean up temporary files
        try:
            os.unlink(temp_filename)
            os.unlink(response_filename)
        except:
            pass

async def process_command(text: str) -> tuple[str, str]:
    try:
        # Get search results
        results = search_provider.search(text)
        
        # Format response
        text_response, voice_response = search_provider.format_response(results)
        
        return text_response, voice_response
        
    except Exception as e:
        logger.error(f"Error processing command: {str(e)}")
        return "Desculpe, ocorreu um erro ao processar sua solicitação.", "Desculpe, ocorreu um erro ao processar sua solicitação."

@bot.command(name='ping')
async def ping(ctx):
    """Simple command to test if the bot is responsive"""
    await ctx.send(f'Pong! Latency: {round(bot.latency * 1000)}ms')

@bot.command(name='hello')
async def hello(ctx):
    """Greets the user"""
    await ctx.send(f'Hello {ctx.author.name}! 👋')

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN')) 