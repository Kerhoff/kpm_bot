import os
import logging

from telegram import ParseMode, ChatAction, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters

import task_manager

logging.basicConfig(format='%(asctime)s - %(name)s- %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    context.bot.send_chat_action(chat_id=update.effective_chat.id,
                                 action=ChatAction.TYPING)
    if task_manager.load_data():
        message = "Task Manager started"
    else:
        message = "Error loading data"

    bot_keyboard: list = [['Update data'],
                          ['Completed Stories Cards'],
                          ['New Stories not in Board'],
                          ['New Cards not in JIRA']]
    reply_markup = ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=message,
                             reply_markup=reply_markup)

def check_permissions(user_id: int):
    admin_ids: list = os.environ['ADMINS'].split(':')
    

    if str(user_id) in admin_ids:
        return True
    else:
        return False

def update_data(update, context):
    if task_manager.update_data():
        message="Cards updated"
    else:
        message="Cards update error"
    
    context.bot.send_message(chat_id=update.effective_chat.id,
                                text=message)

def send_completed_cards(update, context):
    message: dict = task_manager.get_completed_cards()
    inline_keyboard = [[InlineKeyboardButton("Delete completed Cards", callback_data="delete_completed_cards")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
        
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=message['message'],
                             reply_markup=reply_markup,
                             parse_mode=ParseMode.HTML)

def send_new_stories(update, context):
    message: dict = task_manager.get_open_stories_without_card()
    inline_keyboard = [[InlineKeyboardButton("Create Cards in Inbox", callback_data="create_cards_in_inbox")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
        
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=message['message'],
                             reply_markup=reply_markup,
                             parse_mode=ParseMode.HTML)

def send_new_cards(update, context):
    message: dict = task_manager.get_new_cards_without_story()
    
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=message['message'],
                             parse_mode=ParseMode.HTML)

def reply_to_message(update, context):
    context.bot.send_chat_action(chat_id=update.effective_chat.id,
                                 action=ChatAction.TYPING)
    
    user_id: int = update.effective_user.id
    if check_permissions(user_id):
        text: str = update.message.text
        if text == 'Update data':
            update_data(update, context)   
        elif text == 'Completed Stories Cards':
            send_completed_cards(update, context)
        elif text == 'New Stories not in Board':
            send_new_stories(update, context)
        elif text == 'New Cards not in JIRA':
            send_new_cards(update, context)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                text=text)
    else:
        message = "You don't have permission to access this bot"
        context.bot.send_message(chat_id=update.effective_chat.id,
                                    text=message,
                                    parse_mode=ParseMode.MARKDOWN_V2)

def button_pressed(update, context):
    query = update.callback_query
    query.answer()

    if query.data == 'delete_completed_cards':
        message = task_manager.delete_closed_stories_cards()
        query.edit_message_text(text=message)
    elif query.data == 'create_cards_in_inbox':
        message = task_manager.create_new_stories_cards_on_board()
        query.edit_message_text(text=message['message'])
    else:
        query.edit_message_text(text=f"Selected option: {query.data}")

def help(update, context):
    update.message.reply_text("Use /start to start use this bot.")

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Sorry, I didn't understand that command.")

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)



def bot():
    bot_token = os.environ['BOT_TOKEN']
    task_manager.load_data()

    updater = Updater(token=bot_token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))
    dispatcher.add_handler(MessageHandler(Filters.text, reply_to_message))
    dispatcher.add_handler(CallbackQueryHandler(button_pressed))
    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    bot()
