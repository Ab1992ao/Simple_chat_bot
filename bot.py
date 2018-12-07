# -*- coding: utf-8 -*-
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
from config import TOKEN, LOG_FILE
import pickle
from Sentiment import sentiment_model
from engine3 import ENGINE_3

# Enable logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Logging to file
fh = logging.FileHandler(LOG_FILE)#Хандлер регаирует на сообщения, различными.
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
# Logging to console
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)
engine = ENGINE_3()

#request_kwargs = {'proxy_url':'socks5://185.211.245.141:1090/', 'urllib3_proxy_kwargs':{'username':'499962286', 'password':'pass'}}

class Bot:
    def __init__(self):
        self.updater = Updater(TOKEN)#(token=TOKEN, request_kwargs=request_kwargs)
        self.dsp = self.updater.dispatcher
        self.dsp.add_handler(CommandHandler('start', get_help))
        self.dsp.add_handler(CommandHandler('help', get_help))
        self.dsp.add_handler(CommandHandler('sentiment', get_sentiment))
        self.dsp.add_handler(CommandHandler('answer', get_answer))
        self.dsp.add_handler(MessageHandler(Filters.text, echo))
        self.dsp.add_error_handler(error)
        logger.info('Im alive!')
        

    def power_on(self):
        # start the Bot
        self.updater.start_polling()
        self.updater.idle()
        
    
# define command handlers. These usually take the two arguments: bot and
# update. Error handlers also receive the raised TelegramError object in error.


def echo(bot, update):
    logger.info('echo recieved message: {}'.format(update.message.text))
    bot.send_message(update.message.chat_id, text=update.message.text)


def error(bot, update, error):
    # all uncaught telegram-related exceptions will be rerouted here
    logger.error('Update "%s" caused error "%s"' % (update, error))


def get_help(bot, update):
    logger.info('Im here!')
    logger.info('get_help recieved message: {}'.format(update.message.text))
    help_msg = ('Greetings, {} {}! Name is {}, at your service.\n'
                'I currently support the following commands:\n'
                '/start - begins our chat and prints this message\n'
                '/help - prints this message\n'
                '/sentiment [message] - predicts the sentiment of the message\n'
               '/answer [message] - predicts the answer of the question').format(update.message.from_user.first_name, update.message.from_user.last_name, bot.name)
    bot.send_message(update.message.chat_id, text=help_msg)


def get_sentiment(bot, update):
    logger.info('get_sentiment recieved message: {}'.format(update.message.text))
    msg_list=[]
    my_model=sentiment_model()
    try:
        # get message text without the command '/sentiment'
        usr_msg = update.message.text.split(' ', maxsplit=1)[1]
        msg_list.append(usr_msg)
        msg_sentiment = 0.5
        msg_sentiment= my_model.give_sentiment(msg_list)[0]
        bot.send_message(update.message.chat_id, text=round(msg_sentiment,2))
    except IndexError:
        bot.send_message(update.message.chat_id, text='Write your message after the command')
    except Exception as e:
        logger.error(e)
        
def get_answer(bot, update):
    logger.info('get_answer recieved message: {}'.format(update.message.text))
    try:
        # get message text without the command 
        usr_msg = update.message.text.split(' ', maxsplit=1)[1]
        # your code goes here
        '''
        Now determine the sentiment of usr_msg.
        This should return a real number in [0,1].
        Your code goes here.
        '''
        bot.send_message(update.message.chat_id, text=engine.get_top(usr_msg)[0])
    except IndexError:
        bot.send_message(update.message.chat_id, text='Write your message after the command')
    except Exception as e:
        logger.error(e)
               
my_bot = Bot()
my_bot.power_on()
