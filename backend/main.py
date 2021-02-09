"""
Main file for the restaurant booking bot.
It describes the dialog and contains handler functions
for top-level dialog.

Usage:
The starting point for restaurant booking bot.
Having installed all requirements, just run python3 main.py.
Then send /start command to your bot.
Don't forget to register your API key in Updater!
"""

import os
import logging

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import (
    Updater,
    Filters,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    ConversationHandler,
    CallbackQueryHandler,
)

# Import constants
from consts import (
    END,
    TIME,
    TYPING,
    SHOWING,
    RETURNING,
    TABLE_INFO,
    START_OVER,
    NUMBER_OF_PEOPLE,
    SELECTING_ACTION,
    SELECTING_FEATURE,
    SELECTING_TABLE_PARAMS,
)

# Import functions for booking dialog
from booking import (
    save_input,
    end_booking,
    ask_for_input,
    select_table_features,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> str:
    """A function to start the messaging."""
    text = 'Добро пожаловать в бот для бронирования столиков в ресторане!'

    # Welcome the user right after the start
    if not context.user_data.get(START_OVER):
        update.message.reply_text(text=text)

    # Indicate that the dialog is started
    context.user_data[START_OVER] = True
    return select_action(update, context)


def select_action(update: Update, context: CallbackContext) -> str:
    """A function to select the appropriate action."""
    # Buttons to reply with
    buttons = [
        [
            InlineKeyboardButton(
                text='Забронировать столик',
                callback_data=SELECTING_TABLE_PARAMS,
            ),
        ],
        [
            InlineKeyboardButton(
                text='Показать данные',
                callback_data=SHOWING,
            ),
            InlineKeyboardButton(text='Готово', callback_data=END),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    text = 'Выберите действие!'
    # Reply if the user just started the messaging
    # Edit the message otherwise
    if context.user_data.get(START_OVER):
        update.message.reply_text(text=text, reply_markup=keyboard)
    else:
        # Answer on user request
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=keyboard,
        )

    # Indicate that the dialog is started
    context.user_data[START_OVER] = True
    return SELECTING_ACTION


def show_data(update: Update, context: CallbackContext) -> str:
    """A function to show the booking data to user."""
    user_data = context.user_data
    user_data[START_OVER] = False

    table_info = user_data.get(TABLE_INFO)
    entered_people = table_info and NUMBER_OF_PEOPLE in user_data[TABLE_INFO]
    entered_time = table_info and TIME in user_data[TABLE_INFO]

    text = 'Информация по Вашему бронированию:\n'
    # Check if all the needed parameters are present
    if entered_time and entered_people:
        text += f'Время: {table_info[TIME]}\n'
        text += f'Количество человек: {table_info[NUMBER_OF_PEOPLE]}'
    else:
        text += 'Нет бронирований.'

    # 'Go back' button
    buttons = [[InlineKeyboardButton(text='Назад', callback_data=END)]]
    keyboard = InlineKeyboardMarkup(buttons)

    # Answer on user request
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SHOWING


def cancel_booking(update: Update, context: CallbackContext) -> str:
    """A function to go back to selecting action from booking dialog."""
    select_action(update, context)
    return RETURNING


def end(update: Update, context: CallbackContext) -> str:
    """Function to end the dialog with."""
    context.user_data[START_OVER] = True
    # Answer on user request
    update.callback_query.answer()
    text = 'Спасибо, что воспользовались ботом! ' \
           'Чтобы забронировать стол введите /start'
    update.callback_query.edit_message_text(text=text)

    return END


def main() -> None:
    """Main function of the app. It describes the dialog."""
    # Register the API key
    updater = Updater(os.environ.get('API_KEY'))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Describe the conversation to register the table
    table_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                select_table_features,
                pattern=f'^{SELECTING_TABLE_PARAMS}$|^{RETURNING}$',
            )
        ],
        states={
            SELECTING_FEATURE: [
                CallbackQueryHandler(
                    ask_for_input,
                    pattern=f'^{NUMBER_OF_PEOPLE}$|^{TIME}$',
                ),
            ],
            TYPING: [
                MessageHandler(Filters.text & ~Filters.command, save_input),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_booking, pattern=f'^{RETURNING}$'),
            CallbackQueryHandler(end_booking, pattern=f'^{END}$'),
        ],
        map_to_parent={
            RETURNING: SELECTING_ACTION,
        },
    )

    # Handlers for selecting action
    selection_handlers = [
        table_conv,
        CallbackQueryHandler(show_data, pattern=f'^{SHOWING}$'),
        CallbackQueryHandler(end, pattern=f'^{END}$'),
    ]

    # Handler for the main conversation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SHOWING: [CallbackQueryHandler(select_action, pattern=f'^{END}$')],
            SELECTING_ACTION: selection_handlers,
            SELECTING_TABLE_PARAMS: [table_conv],
        },
        fallbacks=[],
    )

    # Add top level conversation to the handler
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
