"""
A file that contains handlers for booking conversation.
"""

import re

from telegram.ext import CallbackContext
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update

# Import necessary constants
from consts import (
    END,
    TIME,
    TYPING,
    RETURNING,
    START_OVER,
    TABLE_INFO,
    CURRENT_FEATURE,
    NUMBER_OF_PEOPLE,
    SELECTING_FEATURE,
    SELECTING_TABLE_PARAMS,
)


def _print_data(update: Update, user_data: dict) -> None:
    """Print inserted data when entering the booking info."""
    table_info = user_data[TABLE_INFO]
    if NUMBER_OF_PEOPLE in table_info:
        text = f'Количество человек: {table_info[NUMBER_OF_PEOPLE]}'
        update.message.reply_text(text=text)

    if TIME in table_info:
        text = f'Время: {table_info[TIME]}.'
        update.message.reply_text(text=text)


def select_table_features(update: Update, context: CallbackContext) -> None:
    """A handler for selecting table features."""
    # Buttons in selecting table features menu
    buttons = [
        [
            InlineKeyboardButton(
                text='Количество людей',
                callback_data=NUMBER_OF_PEOPLE,
            ),
            InlineKeyboardButton(text='Время', callback_data=TIME),
        ],
        [
            InlineKeyboardButton(text='Назад', callback_data=RETURNING),
            InlineKeyboardButton(text='Готово', callback_data=END),
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    user_data = context.user_data
    # Continue the dialog or start over
    if user_data.get(START_OVER):
        # Update table info
        user_data[TABLE_INFO] = {}
        text = 'Укажите количество человек и время посещения.'

        # Answer user query
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=keyboard,
        )
    else:
        entered_people = NUMBER_OF_PEOPLE in user_data[TABLE_INFO]
        entered_time = TIME in user_data[TABLE_INFO]

        # Send helper messages to the user
        # depending on the entered data
        if not entered_people:
            update.message.reply_text(
                text='Осталось указать количество человек.',
            )

        if not entered_time:
            update.message.reply_text(text='Осталось указать время.')

        if entered_time and entered_people:
            text = 'Все необходимые данные получены. ' \
                   'Чтобы завершить бронь нажмите \"Готово\". \n\n' \
                   'Если хотите что-то поменять, ' \
                   'нажмите на соответствующую кнопку.'
        else:
            text = 'Укажите недостающие данные или измените уже указанные.'

        update.message.reply_text(text=text, reply_markup=keyboard)

    user_data[START_OVER] = False
    return SELECTING_FEATURE


def ask_for_input(update: Update, context: CallbackContext) -> None:
    """Handle user input."""
    cur_feature = update.callback_query.data
    context.user_data[CURRENT_FEATURE] = cur_feature

    # User helper messages depending on the data being entered
    if cur_feature == NUMBER_OF_PEOPLE:
        text = 'Введите количество человек (число от 1 до 10).'
    elif cur_feature == TIME:
        text = 'Введите время (чч:мм).'
    else:
        raise Exception('Incorrect feature')

    # Answer user query
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)

    return TYPING


def _check_data_correctness(cur_feature: str, data: str) -> bool:
    """Check user input on matching the pattern."""
    if cur_feature == NUMBER_OF_PEOPLE:
        return bool(re.match(r'[1-9]$', data))
    elif cur_feature == TIME:
        return bool(re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', data))
    else:
        raise Exception('Incorrect feature')


def save_input(update: Update, context: CallbackContext) -> None:
    """Save the user data to the context."""
    user_data = context.user_data

    if CURRENT_FEATURE not in user_data:
        raise Exception('The feature is not set')

    cur_feature = user_data[CURRENT_FEATURE]
    msg_text = update.message.text

    # Check input fo correctness
    is_correct = _check_data_correctness(cur_feature, msg_text)

    if is_correct:
        # Save correct data to the context
        user_data[TABLE_INFO][cur_feature] = msg_text
        _print_data(update, user_data)
    else:
        update.message.reply_text(
            text='Вы ввели данные в неправильном формате!',
        )
    return select_table_features(update, context)


def end_booking(update: Update, context: CallbackContext) -> None:
    """End booking handler."""
    user_data = context.user_data

    # Start over after ending the dialog
    user_data[START_OVER] = True

    # Buttons for end booking menu
    buttons = [
        [
            InlineKeyboardButton(
                text='Назад',
                callback_data=SELECTING_TABLE_PARAMS,
            ),
            InlineKeyboardButton(text='Выход', callback_data=END),
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    entered_num_people = NUMBER_OF_PEOPLE in user_data[TABLE_INFO]
    entered_time = TIME in user_data[TABLE_INFO]
    if entered_num_people and entered_time:
        text = 'Ваш столик забронирован!'
    else:
        text = 'Недостаточно данных для бронирования!'

    # Answer user query
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return END
