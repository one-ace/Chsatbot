import discord
import google.generativeai as genai
import os
from dotenv import load_dotenv # Import this

# Load variables from .env file
load_dotenv()

# --- CONFIGURATION ---
# Now we grab the keys from the secure environment
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# ... rest of your code ...

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
    # 1. Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    # 2. Check if the bot is mentioned (pinged)
    if client.user.mentioned_in(message):

        # Create a visual indicator that the bot is "thinking"
        async with message.channel.typing():

            # 3. manage Context
            # Check if a session exists for this channel, if not, create one
            channel_id = message.channel.id
            if channel_id not in chat_sessions:
                # Initialize chat with a specific persona if desired
                chat_sessions[channel_id] = model.start_chat(
                    history=[
                        {"role": "user", "parts": "You are a helpful Discord assistant. Keep answers concise."}
                    ]
                )

            chat = chat_sessions[channel_id]

            # 4. Clean the prompt
            # Remove the @BotName from the message text so Gemini doesn't get confused
            clean_text = message.content.replace(f'<@{client.user.id}>', '').strip()

            # Handle empty messages (just a ping)
            if not clean_text:
                await message.channel.send("Hello! How can I help you today?")
                return

            try:
                # 5. Send to Gemini and get response
                # The chat object automatically handles the history/context!
                response = chat.send_message(clean_text)

                # Discord has a 2000 character limit per message.
                # If response is too long, we might need to split it (basic implementation below)
                response_text = response.text
                if len(response_text) > 2000:
                    response_text = response_text[:1990] + "...(truncated)"

                await message.channel.send(response_text)

            except Exception as e:
                print(f"Error: {e}")
                await message.channel.send("I encountered an error processing that request.")


# Run the bot
client.run(DISCORD_TOKEN)