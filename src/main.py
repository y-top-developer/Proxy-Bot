import telebot
import logging
from telebot import types

from settings import TELEGRAM_TOKEN, APPROVE_CHAT, MEETUP_CHAT
from text import WELCOME, REQUEST_ADD_WHOIS, APPROVED, DENIED, WAIT_APPROVE, APPROVE, DENY, REQUEST_WHOIS

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)


bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode='markdown')


class States:
    wait_whois = 0
    none = 1


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.chat.type == 'private':
        bot.send_message(
            message.chat.id, WELCOME, disable_web_page_preview=True)
        bot.send_message(
            message.chat.id, REQUEST_WHOIS)
        bot.set_state(message.chat.id, States.wait_whois)


@bot.message_handler(regexp="#whois", state=States.wait_whois)
def ask_whois(message):
    if message.chat.type == 'private':
        bot.forward_message(APPROVE_CHAT, message.chat.id, message.message_id)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row_width = 2

        keyboard.add(
            types.InlineKeyboardButton(
                text=APPROVE,
                callback_data=f'approve_{message.chat.id}_{message.message_id}'
            ),
            types.InlineKeyboardButton(
                text=DENY,
                callback_data=f'deny_{message.chat.id}_{message.message_id}'
            )
        )
        bot.send_message(
            APPROVE_CHAT, f'Will approve? {message.chat.first_name} {message.chat.last_name}', reply_markup=keyboard)

        bot.send_message(message.chat.id, WAIT_APPROVE)
        bot.set_state(message.chat.id, States.none)


@bot.message_handler(state=States.wait_whois)
def send_result(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, REQUEST_ADD_WHOIS)


@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_'))
def approve_user(call):
    bot.edit_message_text(
        chat_id=APPROVE_CHAT,
        message_id=call.message.id,
        text=f'{call.message.text}\n\n{APPROVE}'
    )

    _, user_id, whois_message_id = call.data.split('_')
    bot.send_message(
        user_id, f'{APPROVED}\n{bot.export_chat_invite_link(MEETUP_CHAT)}' parse_mode=None)

    bot.forward_message(MEETUP_CHAT, user_id, whois_message_id)
    bot.set_state(int(user_id), States.none)


@bot.callback_query_handler(func=lambda call: call.data.startswith('deny_'))
def deny_user(call):

    bot.edit_message_text(
        chat_id=APPROVE_CHAT,
        message_id=call.message.id,
        text=f'{call.message.text}\n\n{DENY}'
    )

    _, user_id, _ = call.data.split('_')
    bot.send_message(user_id, DENIED)
    bot.set_state(int(user_id), States.wait_whois)


bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))
bot.add_custom_filter(telebot.custom_filters.IsDigitFilter())

bot.infinity_polling()
