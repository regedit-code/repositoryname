from telebot import TeleBot
from telebot.types import (ReplyKeyboardRemove,ReplyKeyboardMarkup,KeyboardButton)
from db import *
from random import choice
import os
from time import sleep
token = 'git'
bot = TeleBot(token)
game = False
night = False

if not os.path.exists('db.db'):
    create_tabels()


def get_killed(night):
    if not night:
        u_killed = citizen_kill()
        return f'lydi kiknyl1 {u_killed}'
    u_killed = mafia_kill()
    return f'maf1a yb1la {u_killed}'

def autoplay_citizen(message):
    player_roles = get_players_roles()
    for player_id, _ in player_roles:
        usernames = get_all_alive()
        name = f'bot_{player_id}'
        if player_id < 5 and name in usernames:
            usernames.remove(name)
            vote_username = choice(usernames)
            vote('citizen_vote',vote_username,player_id)
            bot.send_message(message.chat.id,f'{name} za {vote_username}')
            sleep(0.5)

def auto_play_mafia():
    players_rols = get_players_roles()
    for player_id,role in players_rols:
        usernames = get_all_alive()
        name = f'bot_{player_id}'
        if player_id < 5 and name in usernames and role == 'mafia':
            usernames.remove(name)
            vote_username = choice(usernames)
            vote('mafia_vote',vote_username,player_id)

def game_loop(message):
    global game,night
    bot.send_message(message.chat.id,'d0br0 poз4Л0Bat B 1gry(2min dlya znakomstva)')
    sleep(5)
    while True:
        msg = get_killed(night)
        bot.send_message(message.chat.id,msg)
        if not night:
            bot.send_message(message.chat.id,'g0r0d zasipaet,mafia prosipaetsya.noch nastypil4')
        else:
            bot.send_message(message.chat.id,'gor0d pr0Сipaetsya')

        winner = check_win()
        if winner == 'Mafia' or winner == 'citizen':
            game = False
            bot.send_message(message.chat.id, f'podea {winner}')
        clear(dead=False)
        night = not night
        alive = get_all_alive()
        alive = '\n'.join(alive)
        bot.send_message(message.chat.id,f'v 1gre {alive}')
        sleep(10)
        auto_play_mafia() if night else autoplay_citizen(message)

@bot.message_handler(commands=['start'])
def game_on(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('ready'))
    bot.send_message(message.chat.id,'press button',reply_markup=keyboard)
    
@bot.message_handler(func=lambda message: message.text.lower() == "ready", chat_types=["private"])
def send_text(message):
    bot.send_message(message.chat.id, f"{message.from_user.first_name} играет!", reply_markup=ReplyKeyboardRemove())
    if get_user(message.from_user.id):
        bot.send_message(message.chat.id, "Вы уже есть")
    else:
        bot.send_message(message.chat.id, "Вы добавлены в игру!")
        insert_player(message.from_user.id, message.from_user.first_name)
 
@db_connect
def get_user(cur, player_id: int) -> bool:
    cur.execute("SELECT * FROM players WHERE player_id=?", (player_id,))
    if cur.fetchone():
        return True
    return False 
@bot.message_handler(commands=['game'])
def game_start(message):
    global game
    players = players_amount()
    if players >= 5 and not game:
        set_roles(players)
        player_roles = get_players_roles()
        mafia = get_mafia_usernames()
        for player_id,role in player_roles:
            try:
                bot.send_message(player_id,role)
                if role =='mafia':
                    bot.send_message(player_id,f'vs3 ch3n1 mAfi1: {mafia}')
            except:
                print(f'1D: {player_id}\n r0l3: {role}')    
                continue
        game = True
        bot.send_message(message.chat.id,'1gra startyet')
        game_loop(message)
        return
    bot.send_message(message.chat.id,'n3D0statochn0 zh3rtV')
    for i in range(5):
        bot_name = f'bot_{i}'
        insert_player(i,bot_name)
        bot.send_message(message.chat.id,f'{bot_name} d0bavl3n!')
        sleep(0.2)
    game_start(message)

@bot.message_handler(commands=['kick'])
def kick(message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = get_all_alive()

    if not night:
        if not username in usernames:
            bot.send_message(message.chat.id,'1men1 n3t')
            return
        voted = vote('citizen_vote',username,message.from_user.id)
        if voted:
            bot.send_message(message.chat.id,'g0loC ycht3n')
            return
        bot.send_message(message.chat.id,'n3t pr4vA gol0covat')
        return
    bot.send_message(message.chat.id,'n0ch,n3lsa')

@bot.message_handler(commands=['kill'])
def kill(message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = get_all_alive()
    mafia_usernames = get_mafia_usernames()
    if night and message.from_user.first_name in mafia_usernames:
        if not username in usernames:
            bot.send_message(message.chat.id,'1meni net')
            return
        voted = vote('mafia_vote',username,message.from_user.id)
        if voted:
            bot.send_message(message.chat.id,'g0los ycht3n')
            return
        bot.send_message(message.chat.id,'nety pr4v')
        return
    bot.send_message(message.chat.id,'d3n, nelsya yb1vat')
if __name__ == "__main__":
    bot.polling(non_stop=True)