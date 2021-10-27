import numpy as np
import pickle
import os
from os import path

# ------------------------------------------------------------------------------
# Utilities :

def chain(list_names):
    """
    Input: List of names ('@username') of participants
    Output: Dict {'giver': 'receiver'} with giver and receiver being usernames
    """

    np.random.shuffle(list_names)

    list_couples = []

    for i in range(len(list_names) - 1):
        list_couples.append((list_names[i], list_names[i+1]))

    list_couples.append((list_names[-1], list_names[0]))

    dict_couples = {}
    for couple in list_couples:
        dict_couples[couple[0]] = couple[1]

    return dict_couples

# ------------------------------------------------------------------------------
# Handlers

def start(update, context):
    """
    Welcome message on /start
    """
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Welcome to bot-Santa!\nTo join the pool of participants, use /join.\nTo see the list of participants, use /list. \nTo get the name of the person that was drawn for you, use /get_name. \n")


def reset(update, context):
    """
    PROTECTED
    Cleans up the data folder
    """
    try:
        if path.exists("data/participants.pkl"):
            os.remove('data/participants.pkl')
        if path.exists("data/assignements.pkl"):
            os.remove('data/assignements.pkl')
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Reset done")
    except:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Error, please check https://github.com/RomainC123/bot-santa and add a pull request")


def add(update, context):
    """
    PROTECTED
    Adds a list of users (provided in the command, /add @username1 @username2) to the list of participants
    """
    if not path.exists("data/assignements.pkl"):
        try:
            with open('data/participants.pkl', 'rb') as f:
                list_participants = pickle.load(f)
        except:
            list_participants = []

        list_names_to_add = context.args
        for name in list_names_to_add:
            if name not in list_participants:
                list_participants.append(name)

        with open('data/participants.pkl', 'wb') as f:
            pickle.dump(list_participants, f)

        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Participants added")
    else:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Couple assignement has already been done, it's not possible to add more participants now.")


def assign(update, context):
    """
    PROTECTED
    Uses the list of participants to generate the pairings, and store these pairings
    """

    try:
        with open('data/participants.pkl', 'rb') as f:
            list_participants = pickle.load(f)

        print('loaded')

        dict_couples = chain(list_participants)

        print('chained')

        with open('data/assignements.pkl', 'wb') as f:
            pickle.dump(dict_couples, f)

        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Assignements done")
    except:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Participants list empty of invalid")


def list_participants(update, context):
    """
    Returns the list of participants in the chat
    """
    try:
        with open('data/participants.pkl', 'rb') as f:
            list_participants = pickle.load(f)

        if len(list_participants) == 0:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text="There are no participants yet")
        else:
            text = ''
            for username in list_participants:
                text += f'{username}\n'
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text=text)
    except:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="There are no participants yet")


def join(update, context):
    """
    Adds the username that called /join to the list of participants
    """
    if not path.exists("data/assignements.pkl"):
        try:
            with open('data/participants.pkl', 'rb') as f:
                list_participants = pickle.load(f)
        except:
            list_participants = []

        username = '@' + update.message.from_user.username
        if username not in list_participants:
            list_participants.append(username)

        with open('data/participants.pkl', 'wb') as f:
            pickle.dump(list_participants, f)

        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="You have been added")
    else:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Couple assignement has already been done, it is too late to join now")


def get_name(update, context):
    """
    Returns the name chosen for the username that called /get_name
    """
    try:
        with open('data/assignements.pkl', 'rb') as f:
            dict_couples = pickle.load(f)

        username = update.message.from_user.username
        text = f'You will be giving a gift to {dict_couples["@" + username]}'
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=text)
    except:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Couple assignement hasn't been done yet")


def get_all(update, context):
    """
    PROTECTED, TEST ONLY
    Returns the name chosen for the username that called /get_name
    """
    try:
        with open('data/assignements.pkl', 'rb') as f:
            dict_couples = pickle.load(f)

        text = ''
        for giver in dict_couples:
            text += f'{giver} gives a gift to {dict_couples[giver]}\n'
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=text)
    except:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Couple assignement hasn't been done yet")
