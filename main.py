from keep_alive import keep_alive
import discord
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load variables from .env file (for local testing)
load_dotenv()

# --- CONFIGURATION ---
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash') 

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

chat_sessions = {}

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message):
        async with message.channel.typing():
            channel_id = message.channel.id
            if channel_id not in chat_sessions:
                chat_sessions[channel_id] = model.start_chat(
                    history=[
                        {"role": "user", "parts": "You are a helpful Discord assistant. Keep answers concise."}
                    ]
                )

            chat = chat_sessions[channel_id]
            clean_text = message.content.replace(f'<@{client.user.id}>', '').strip()

            if not clean_text:
                await message.channel.send("Hello! How can I help you today?")
                return

            try:
                response = chat.send_message(clean_text)
                response_text = response.text
                if len(response_text) > 2000:
                    response_text = response_text[:1990] + "...(truncated)"
                await message.channel.send(response_text)

            except Exception as e:
                print(f"Error: {e}")
                await message.channel.send("I encountered an error processing that request.")

# --- START THE WEB SERVER ---
keep_alive()  

# --- RUN THE BOT ---
client.run(DISCORD_TOKEN)
