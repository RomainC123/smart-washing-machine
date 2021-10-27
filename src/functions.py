import numpy as np
import pandas as pd
import pickle
import os
import uuid
from os import path

# ------------------------------------------------------------------------------
# Utilities :


def grab_updates():
    """
    Periodicly called to fetch updates from the card
    Updates the status command (machines used, time left estimated, users currently using)
    """
    pass

# ------------------------------------------------------------------------------
# Handlers


def start(update, context):
    """
    Welcome message on /start
    """
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Welcome to the Smart Washing Mashine Bot!\nAvaliable commands:\n- /subscribe: Provides you with a NFC tag to use the machines\n- /unsubscribe: Removes your tag and username from the database\n- /status: Displays the status of all connected machines")


def reset(update, context):
    """
    PROTECTED
    Cleans up the data folder
    """
    try:
        if path.exists("data/subscribers.pkl"):
            os.remove('data/subscribers.pkl')
        if path.exists("data/status.pkl"):
            os.remove('data/status.pkl')
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Reset done")
    except:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Error, please check https://github.com/RomainC123/smart-washing-machine and add a pull request (don't do that)")


def connect(update, context):
    pass


def subscribe(update, context):
    """
    Adds the username of the sender of the request to the list of subscribers, and creates an id for that person
    """
    try:
        with open('data/subscribers.pkl', 'rb') as f:
            df_subscribers = pickle.load(f)
    except:
        df_subscribers = pd.DataFrame(columns=['username', 'nfc_id'])

    print(df_subscribers['username'].values)

    username = update.message.from_user.username
    if username not in df_subscribers['username'].values:
        new_nfc_id = uuid.uuid4()
        new_sub = pd.DataFrame({'username': [username], 'nfc_id': [new_nfc_id]})
        df_subscribers = df_subscribers.append(new_sub, ignore_index=True)

        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=f"You have subscribed to our service. Your NFC tag id is:\n{new_nfc_id}\nPlease keep it.\nTo use our machines, download a nfc tag maker on your phone, and create a NFC tag with your given id")

    else:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=f"You are already subscribed to our service\nPlease use contact an administrator of you forgot your NFC ID, or use /unsubscribe to remove your subscription")

    with open('data/subscribers.pkl', 'wb') as f:
        pickle.dump(df_subscribers, f)


def unsubscribe(update, context):
    """
    Removes the username of the sender of the request form the list of subscribers
    """
    try:
        with open('data/subscribers.pkl', 'rb') as f:
            df_subscribers = pickle.load(f)
    except:
        df_subscribers = pd.DataFrame(columns=['username', 'nfc_id'])

    print(df_subscribers)

    username = update.message.from_user.username
    if username in df_subscribers['username'].values:
        df_subscribers.drop(df_subscribers[df_subscribers['username'] == username].index, inplace=True)
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=f"You have successefully unsubscribed.")

    else:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=f"You aren't subscribed to our service, please consider using /subscribe to do so.")

    with open('data/subscribers.pkl', 'wb') as f:
        pickle.dump(df_subscribers, f)


def status(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=f"PLACEHOLDER message for status updates")
