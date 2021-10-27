from functions import *
import logging
import time

from telegram.ext import Updater, Filters, CommandHandler

with open('data/token_bot', 'r') as f:
    token = f.read().strip()
    updater = Updater(token=token, use_context=True)

dispatcher = updater.dispatcher

with open('data/token_card', 'r') as f:
    tokens = f.read().strip().split('\n')
    token_write = tokens[0]
    token_read = tokens[1]

# ------------------------------------------------------------------------------

# Enable logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# ------------------------------------------------------------------------------

# Get admins list
admins = []
with open('data/admins', 'r') as f:
    admins = f.read().strip()

# ------------------------------------------------------------------------------

start_handler = CommandHandler('start', start, filters=Filters.user(username=admins))
dispatcher.add_handler(start_handler)

reset_handler = CommandHandler('reset', reset, filters=Filters.user(username=admins))
dispatcher.add_handler(reset_handler)

subscribe_handler = CommandHandler('subscribe', subscribe)
dispatcher.add_handler(subscribe_handler)

unsubscribe_handler = CommandHandler('unsubscribe', unsubscribe)
dispatcher.add_handler(unsubscribe_handler)

status_handler = CommandHandler('status', status)
dispatcher.add_handler(status_handler)

updater.start_polling()
