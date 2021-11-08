import numpy as np
import pandas as pd
import pickle
import os
import uuid
import datetime
import requests
import json
from os import path

# ------------------------------------------------------------------------------
# Utilities :

with open('data/token_card', 'r') as f:
    tokens = f.read().strip().split('\n')
    token_write = tokens[0]
    token_read = tokens[1]


def get_status():
    """
    Fetches status updates from the card
    """
    url = f"https://api.thingspeak.com/channels/1530398/feeds.json?api_key={token_read}&results=5"
    with requests.get(url) as r:
        info_json = json.loads(r.text)
        status_card = int(info_json['feeds'][-1]['field1'])
    return status_card


def status_updater():
    """
    Continuously updates the machine status
    """

    try:
        with open('data/status.pkl', 'rb') as f:
            list_status = pickle.load(f)

        status_card = get_status()
        old_status = list_status[0]

        if old_status == 0 and status_card == 1:
            # Send message to user thats says Cycle done, please come pick up your shit
            list_status[2] = None
        elif old_status == 1 and status_card == 2:
            # Send message to user thats says Door was opened
            list_status[1] = None

        list_status[0] = status_card

        with open('data/status.pkl', 'wb') as f:
            pickle.dump(list_status, f)

    except:
        print("Error fetching updates, please check the logs")

# ------------------------------------------------------------------------------
# Handlers


def start(update, context):
    """
    Welcome message on /start
    """
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Welcome to the Smart Washing Mashine Bot!\nAvaliable commands:\n- /status: Displays the status of all connected machines\n- /start_cycle Use it after strating a machine cycle. Write the command followed by the duration of the program you started (for example, for a 50 minutes program, write /start_cycle 50).")


def init(update, context):
    """
    PROTECTED
    Initialises all necessary folders
    """
    df_subscribers = pd.DataFrame(columns=['username', 'nfc_id'])
    list_status = [2, None, None, None]

    with open('data/subscribers.pkl', 'wb') as f:
        pickle.dump(df_subscribers, f)

    with open('data/status.pkl', 'wb') as f:
        pickle.dump(list_status, f)

    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Init done!")


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


def subscribe(update, context):
    """
    Adds the username of the sender of the request to the list of subscribers, and creates an id for that person
    """
    try:
        with open('data/subscribers.pkl', 'rb') as f:
            df_subscribers = pickle.load(f)
    except:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=f"I haven't been initalized, please contact an admin.")

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


def start_cycle(update, context):
    """
    Informs the system that the user that called the command started a cycle, with the duration of the cycle given by the user
    """

    username = update.message.from_user.username

    try:
        duration = int(context.args[0])
        if duration != 0:

            with open('data/status.pkl', 'rb') as f:
                list_status = pickle.load(f)

            if list_status[0] != 2 and list_status[1] != None:
                context.bot.send_message(chat_id=update.message.chat_id,
                                         text=f"The machine is already being used by @{list_status[1]}, please wait for that cycle to end before requesting anoither start")
            else:
                list_status[1] = username
                list_status[2] = datetime.datetime.now() + datetime.timedelta(minutes=duration)
                list_status[3] = update.message.chat_id

                with open('data/status.pkl', 'wb') as f:
                    pickle.dump(list_status, f)

                context.bot.send_message(chat_id=update.message.chat_id,
                                         text=f"Your cycle has been registered.\nNow don't forget to press the button on the card to update the bot /status command.")
        else:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text=f"Please provide a valid duration (in minutes) with your command (/start_sycle 90 for example).")
    except:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=f"Please provide a valid duration (in minutes) with your command (/start_sycle 90 for example).")


def status(update, context):

    try:
        with open('data/status.pkl', 'rb') as f:
            list_status = pickle.load(f)
    except:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Init not done, please contact an admin.")

    if list_status[0] == 2:
        status = "Free"
    elif list_status[0] == 1:
        status = "Cycle done, machine still full"
    else:
        status = "Cycle running"

    message = f"Machine 1:\nStatus: {status}\n"

    if list_status[0] == 1:
        if list_status[1] != None:
            message += f"User: @{list_status[1]}\n"
        else:
            message += f"User: Not specified\n"

    elif list_status[0] == 0:
        try:
            duration_left = ((list_status[2] - datetime.datetime.now()).seconds // 60) % 60
            if duration_left > 0:
                message += f"User: @{list_status[1]}\nTime left: {duration_left} min\n"
            else:
                list_status[2] = None
                message += f"User: @{list_status[1]}\nTime left: Cycle nears completion\n"
        except:
            message += f"User: Not specified\nDuration: Not specified"

    with open('data/status.pkl', 'wb') as f:
        pickle.dump(list_status, f)

    context.bot.send_message(chat_id=update.message.chat_id,
                             text=message)
