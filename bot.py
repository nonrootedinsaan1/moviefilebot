import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
from telegram.error import TelegramError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API token and channel IDs from environment variables
API_TOKEN = os.getenv("API_TOKEN")
MANDATORY_CHANNEL_ID = os.getenv("MANDATORY_CHANNEL_ID")
OPTIONAL_CHANNEL_ID = os.getenv("OPTIONAL_CHANNEL_ID")
FILE_CHANNEL_ID = os.getenv("FILE_CHANNEL_ID")

# Store the file IDs for video files
FILE_IDS = {
    'Squid Game': {
        'Ep1': 'BAACAgEAAxkBAAMEZ3DsN-FA7IHHgPkO8USXnYhEBtwAAoQFAAIt7mhHV63yXpwpBpA2BA',
        'Ep2': 'BAACAgEAAxkBAAMGZ3DsRNfoIaokkV5CfHR_w8OL-nwAAoMFAAIt7mhHgPxtW15Ot0Q2BA',
        'Ep4': 'BAACAgEAAxkBAAMIZ3DsSmUIP1eCrw3ijYi3D9WGm9wAAo0FAAIt7mhHSreQD3RfqAw2BA',
        'Ep5': 'BAACAgEAAxkBAAMKZ3DsU5MEC6LmZSr2N1G7EJfA6gwAApMFAAIt7mhHth32fOmvfP82BA',
        'Ep6': 'BAACAgEAAxkBAAMMZ3DsV4cmdHQJZcArX0xftYWY3tAAAqIFAAIt7mhHmZHe_Z6mSsI2BA',
        'Ep7': 'BAACAgEAAxkBAAMOZ3DsXC8QIk_H9st_o92X2KE21zUAAqUFAAIt7mhHHVdJ-c7a1682BA',
        'Combined 480p': 'BAACAgEAAxkBAAMQZ3DsYMX4Qh8Tizxl1KHNyLC5TD4AAqoFAAIt7mhH0VafMpHBYrY2BA',
        'Combined 720p': 'BAACAgEAAxkBAAMSZ3DsZv12_d56s_lTsh8AAS5xSpg3AAKwBQACLe5oR6cLuEWPjoOINgQ'
    },
    'Culpa Tuya': {
        'Ep1': 'FILE_ID_CULPA1',
        'Ep2': 'FILE_ID_CULPA2'
    }
}

# Function to check if user is a member of the mandatory channel
async def is_member(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(MANDATORY_CHANNEL_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except TelegramError:
        pass
    return False

# /start command handler
async def start(update: Update, context: CallbackContext):
    join_mandatory = InlineKeyboardButton("Join Channel", url=f"https://t.me/+QuF5rK2K6UE3Y2E1")
    join_optional = InlineKeyboardButton("Join Channel", url=f"https://t.me/squidgameculpatuya")
    check_button = InlineKeyboardButton("Check Membership", callback_data='check_membership')
    keyboard = InlineKeyboardMarkup([[join_mandatory], [join_optional], [check_button]])
    await update.message.reply_text(
        "Welcome! Please join all the channels to get the direct video file.",
        reply_markup=keyboard
    )

# Check membership and show series options
async def check_membership(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    if await is_member(update, context):
        keyboard = [
            [InlineKeyboardButton("Squid Game", callback_data='show_squid_game')],
            [InlineKeyboardButton("Culpa Tuya", callback_data='show_culpa_tuya')]
        ]
        await query.edit_message_text("Select a series to view episodes:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await query.edit_message_text("You need to join all the channels first!")

# Show episodes for Squid Game or Culpa Tuya
async def show_episodes(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    if query.data == 'show_squid_game':
        keyboard = [[InlineKeyboardButton(ep, callback_data=f"Squid Game|{ep}")] for ep in FILE_IDS['Squid Game'].keys()]
    elif query.data == 'show_culpa_tuya':
        keyboard = [[InlineKeyboardButton(ep, callback_data=f"Culpa Tuya|{ep}")] for ep in FILE_IDS['Culpa Tuya'].keys()]
    else:
        return
    await query.edit_message_text("Select an episode:", reply_markup=InlineKeyboardMarkup(keyboard))

# Send the video file when an episode is selected
async def send_file(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    series, episode = query.data.split('|')
    file_id = FILE_IDS[series].get(episode)
    if file_id:
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video=file_id,
            caption=f"Here is {series} - {episode}",
            supports_streaming=True,
            protect_content=True
        )
    else:
        await query.edit_message_text("Sorry, the requested file is not available. Kindly contact the admin @mayank_ka_b_for_bot .")

# Main function
def main():
    application = Application.builder().token(API_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(check_membership, pattern='^check_membership$'))
    application.add_handler(CallbackQueryHandler(show_episodes, pattern='^show_'))
    application.add_handler(CallbackQueryHandler(send_file, pattern=r'^[^|]+\|[^|]+$'))
    application.run_polling()

if __name__ == '__main__':
    main()
