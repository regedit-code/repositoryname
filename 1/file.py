from time import time
from threading import Timer 
from random import randint
from telebot import Telebot
from telebot.types import message
from telebot import InlineKeyboardMarkup,InlineKeyboardButton
from collections import defaultdict,deque

message_lim = 5
time_window = 10
user_messages = defaultdict(lambda: deque(maxlen=message_lim))
warned_users = set()
TOKEN = 'x'
bot = Telebot(TOKEN)
with open('bad.txt','r',encoding='utf-8') as file:
    data = [word.strip().lower() for word in file.readlines()]


def is_admin(message):
    chat_member = bot.get_chat_member(message.chat.id,message.from_user.id)

    if chat_member.status in ('administrator','owner','creater'):
        return True
    return False

def has_bad(text:str):
    words = text.split(' ')
    for word in words:
        if word in data:
            return True
    return False


def remove_warn(user_id):
    warned_users.discard(user_id)



keyboard = InlineKeyboardMarkup()
numbers = ['один','два','три','четыре','пять','шесть','семь','восемь','девять','десять']
keys = []
for indx, number in enumerate(numbers):
    keys.append(InlineKeyboardButton(
        text=number, callback_data=indx+1
    ))
keyboard.row(*keys)

n1 = randint(1,5)
n2 = randint(1,5)
sum = n1+n2
bot.send_message(message.chat.id,f'Решите пример: {n1} + {n2} = ...',reply_markup=keyboard)
@bot.callback_query_handler(func=lambda call:call data)
def callback_inline(call):
    global sum
    if int(call.data) == sum:
        bot.send_message(message.chat.id,'проверка пройдена', reply_to_message_id=message.message_id)
    elif int(call.data) != sum:

        bot.send_message(message.chat.id,'проверка не пройдена', reply_to_message_id=message.message_id)
        bot.restrict_chat_member(message.chat.id,message.from_user.id, time() + 60)



@bot.message_handler(chat_types=['group','supergroup'],func = lambda message: has_bad(message.text.lower()))
def ban_user(message):
    if is_admin(message):
        bot.send_message(message.chat.id,'Не могу!!', reply_to_message_id=message.message_id)
    else:
        bot.restrict_chat_member(message.chat.id,message.from_user.id, time() + 60)
        bot.send_message(message.chat.id,'бан1!!', reply_to_message_id=message.message_id)
        bot.delete_message(message.chat.id,message.message_id)


@bot.message_handler(chat_types=['group','supergroup'])
def anti_spam(message):
    user_id = message.from_user.id
    now = time()
    if user_id in warned_users and (now - user_messages[user_id][-1] > 60):
        warned_users.remove(user_id)
    
    user_messages[user_id].append(now)
    if not is_admin(message):
        if len(user_messages[user_id] == message_lim and (now - user_messages[user_id][0])) < time_window:
            if user_id not in warned_users:
                bot.send_message(message.chat.id,f'@{message.from_user.username} спам!!!')
                bot.restrict_chat_member(message.chat.id,message.from_user.id, time() + 60)
                warned_users.add(user_id)
                Timer(60,remove_warn,args=[user_id]).start()

            bot.delete(message.chat.id,message.message_id)

@bot.message_handler(chat_types=['group','supergroup'],func=lambda message: message.enttities is not None)
def delete_link(message):
    for entity in message.entities:
        if entity.type in ('url','text_link'):
            bot.delete_message(message.chat.id,message.message_id)

bot.polling(non_stop=True)
