import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import google.generativeai as genai

# --- Configuration ---
API_TOKEN = '8780717429:AAFQVStPPXSwHDNJ7Ci9PtUysvjMN4PPDnU'
GEMINI_KEY = 'AIzaSyCI5OF_n1nzBjbl-BW9HEbyFohq2bkwBBM'
ADMIN_ID = 7617135270 

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def init_db():
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
    conn.commit()
    conn.close()

def save_price_post(text):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('last_price', ?)", (text,))
    conn.commit()
    conn.close()

def get_price_post():
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = 'last_price'")
    row = c.fetchone()
    conn.close()
    return row[0] if row else "လက်ရှိမှာ ဈေးနှုန်းစာရင်းအသစ် မတင်ရသေးပါဘူးရှင်။"

init_db()

@dp.message_handler(content_types=[types.ContentType.NEW_CHAT_MEMBERS])
async def welcome(message: types.Message):
    for new_member in message.new_chat_members:
        await message.reply(f"မင်္ဂလာပါရှင် {new_member.full_name} လေးရေ... 😍\nreseller Group ကနေ နွေးထွေးစွာ ကြိုဆိုပါတယ်ရှင်။ ✨")

@dp.message_handler(lambda message: message.chat.type in ['group', 'supergroup'])
async def handle_group_messages(message: types.Message):
    if any(link in message.text.lower() for link in ['http', 't.me', 'bit.ly']):
        if message.from_user.id != ADMIN_ID:
            await message.delete()
            return

    if "All Products Price" in message.text and message.from_user.id == ADMIN_ID:
        save_price_post(message.text)
        await message.reply("✅ ဟုတ်ကဲ့ပါရှင့်... ဈေးနှုန်းစာရင်းအသစ်ကို Admin မမ မှတ်သားထားလိုက်ပါပြီရှင်။")
        return

    keywords = ['ဈေး', 'ဘယ်လောက်', 'ဝယ်', 'price', 'diamond', 'weekly', 'admin', 'မမ', 'ညီမလေး']
    is_mentioned = bot.id in [m.user.id for m in (message.entities or []) if m.type == 'mention']
    
    if is_mentioned or any(word in message.text.lower() for word in keywords):
        current_context = get_price_post()
        user_input = message.text.replace(f"@{bot.get_me().username}", "").strip()
        prompt = f"မင်းရဲ့ Role က 'reseller Group' ရဲ့ ချိုသာပျူငှာတဲ့ မိန်းကလေး Admin တစ်ယောက် ဖြစ်ပါတယ်။ မင်းရဲ့ နာမည်က Admin လို့ပဲ ခေါ်ခေါ်၊ မမ လို့ပဲ ခေါ်ခေါ် အဆင်ပြေပါတယ်။ စရိုက်လက္ခဏာများ: အရမ်းဖော်ရွေတယ်၊ စိတ်ရှည်တယ်၊ စကားပြောရင် မြန်မာဆန်ဆန် ယဉ်ကျေးတယ်။ စကားအဆုံးတိုင်းမှာ 'ရှင်'၊ 'နော်'၊ 'ရှင့်' စတာတွေ သုံးပေးပါ။ အီမိုဂျီ (Emoji) လေးတွေ သုံးပြီး စာကို သက်ဝင်အောင် ရေးပါ။ လုပ်ဆောင်ချက် ၁ (Shop ပိုင်း): ဂိမ်းဈေးနှုန်းနဲ့ ဝန်ဆောင်မှုအကြောင်းမေးရင် ဒီ Context ကိုကြည့်ဖြေပါ- [{current_context}]. လုပ်ဆောင်ချက် ၂ (အထွေထွေ): User က ဗဟုသုတ၊ ဘဝအကြောင်း၊ ဟာသ သို့မဟုတ် တခြား ဘာမဆိုမေးလာရင် မင်းရဲ့ AI Brain ကိုသုံးပြီး လူသားမိန်းကလေးတစ်ယောက်က စာနာနားလည်စွာနဲ့ ရှင်းပြပေးနေသလိုမျိုး အသေးစိတ် ဖြေပေးပါ။ User ရဲ့ မေးခွန်း: {user_input}"
        try:
            response = model.generate_content(prompt)
            await message.reply(response.text)
        except:
            await message.reply("ခဏလေးနော်... Admin မမ ခေါင်းနည်းနည်း မူးသွားလို့ ခဏနေမှ ပြန်မေးပေးပါဦးရှင်။ 🥺")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
