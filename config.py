from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_APIKEY = os.getenv("SUPABASE_APIKEY")
CHAT_ID = int(os.getenv("CHAT_ID"))