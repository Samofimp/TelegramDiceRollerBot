#!/usr/bin/env python
# pylint: disable=unused-argument

"""
Bot to keep track of game events progress - Progress Clock bot.

Usage:
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os
import re
import random
import time

from dotenv import load_dotenv

from telegram import Chat, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


# Enable logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

commands_description = f"""Commands usage:
`/commands` \\- Show commands description\\.
`/f` or `/full` \\- Detailed dice roll, lists every dice rolled on the throw\\.
`/r` or `/roll` \\- Simple dice roll, gives result of the throw only\\.
Dices amount allowed is between 1 and 99\\.

Dice mechanics:
*Standard dice*: d4, d6, d20, etc\\. Example of usage: `/f 5d20`\\.
*VtM dice*: rolls a set of d10s\\. Each 1 subtracts one success\\. Each 10 adds two successes\\.
_By default, throw difficulty is 6 but it can be additionally set_\\. Examples of usage:
\\- `/f 5v` \\- throws five d10s with throw difficulty of 6\\.
\\- `/f 6v8` \\- throws six d10s with throw difficulty of 8\\.
Throw difficulty cannot be lesser than 1 and greater than 10\\.
"""


# Gives list of commands as a start of a private chat
async def start_private_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.effective_user.full_name
    chat = update.effective_chat
    if chat.type != Chat.PRIVATE:
        return

    logger.info(f"{user_name} started a private chat with the bot (id={chat.id})")

    await update.effective_message.reply_text(commands_description, parse_mode=ParseMode.MARKDOWN_V2)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


# List bot commands
async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(commands_description, parse_mode=ParseMode.MARKDOWN_V2)


# Make a simple dice roll
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Check if command argument is present
    args = context.args
    num_of_args = len(args)
    if num_of_args != 1:
        await update.message.reply_text("/roll command takes one argument. Check /commands for reference.")
        return

    # Check argument (dice) type
    standard_dice_pattern = re.compile("^\\d{1,2}d\\d{1,2}$")
    vtm_dice_pattern = re.compile("^\\d{1,2}v\\d{0,2}$")
    if standard_dice_pattern.fullmatch(args[0]) is not None:
        # Throw dices and give the sum
        dice_throw = args[0]
        throw_numbers = dice_throw.split("d")
        dice_amount = int(throw_numbers[0])
        dice_faces = int(throw_numbers[1])
        if dice_faces < 1 or dice_amount < 1:
            await update.message.reply_text("Cannot parse the command argument. Check /commands for reference.")
            return
        random.seed(time.time())
        throw_sum = 0

        for i in range(0, dice_amount):
            throw_sum += random.randint(1, dice_faces)

        await update.message.reply_text(f"`{dice_throw}`: {throw_sum}", parse_mode=ParseMode.MARKDOWN_V2)

    elif vtm_dice_pattern.fullmatch(args[0]) is not None:
        # Throw dices and count successes
        dice_throw = args[0]
        throw_numbers = dice_throw.split("v")
        dice_amount = int(throw_numbers[0])
        dice_difficulty = 6
        if throw_numbers[1] != "":
            dice_difficulty = int(throw_numbers[1])
        if dice_amount < 1:
            await update.message.reply_text("Cannot parse the command argument. Check /commands for reference.")
            return
        if dice_difficulty < 1 or dice_difficulty > 10:
            await update.message.reply_text("Throw difficulty cannot be lesser than 1 and greater than 10.")
            return

        random.seed(time.time())
        successes = 0
        for i in range(0, dice_amount):
            single_throw = random.randint(1, 10)
            if single_throw == 1:
                successes -= 1
            elif single_throw == 10:
                successes += 2
            elif single_throw >= dice_difficulty:
                successes += 1

        # Print result
        if successes < 0:
            await update.message.reply_text(f"`{dice_throw}`: *Botch\\!*", parse_mode=ParseMode.MARKDOWN_V2)
        elif successes == 0:
            await update.message.reply_text(f"`{dice_throw}`: *Failure\\!*", parse_mode=ParseMode.MARKDOWN_V2)
        elif successes == 1:
            await update.message.reply_text(f"`{dice_throw}`: *1* success", parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await update.message.reply_text(f"`{dice_throw}`: *{successes}* successes", parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await update.message.reply_text("Cannot parse the command argument. Check /commands for reference.")


# Make a detailed dice roll
async def full(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Check if command argument is present
    args = context.args
    num_of_args = len(args)
    if num_of_args != 1:
        await update.message.reply_text("/full command takes one argument. Check /commands for reference.")
        return

    # Check argument (dice) type
    standard_dice_pattern = re.compile("^\\d{1,2}d\\d{1,2}$")
    vtm_dice_pattern = re.compile("^\\d{1,2}v\\d{0,2}$")
    if standard_dice_pattern.fullmatch(args[0]) is not None:
        # Throw dices, give results and the sum
        dice_throw = args[0]
        throw_numbers = dice_throw.split("d")
        dice_amount = int(throw_numbers[0])
        dice_faces = int(throw_numbers[1])
        if dice_faces < 1 or dice_amount < 1:
            await update.message.reply_text("Cannot parse the command argument. Check /commands for reference.")
            return
        random.seed(time.time())
        throw_sum = 0
        throws_list = "\\["

        for i in range(0, dice_amount):
            single_throw = random.randint(1, dice_faces)
            if i == dice_amount - 1:
                throws_list = f"{throws_list}{single_throw}\\]"
            else:
                throws_list = f"{throws_list}{single_throw},"
            throw_sum += single_throw

        await update.message.reply_text(f"`{dice_throw}`: *{throw_sum}* `{throws_list}`", parse_mode=ParseMode.MARKDOWN_V2)

    elif vtm_dice_pattern.fullmatch(args[0]) is not None:
        # Throw dices and count successes
        dice_throw = args[0]
        throw_numbers = dice_throw.split("v")
        dice_amount = int(throw_numbers[0])
        dice_difficulty = 6
        if throw_numbers[1] != "":
            dice_difficulty = int(throw_numbers[1])
        if dice_amount < 1:
            await update.message.reply_text("Cannot parse the command argument. Check /commands for reference.")
            return
        if dice_difficulty < 1 or dice_difficulty > 10:
            await update.message.reply_text("Throw difficulty cannot be lesser than 1 and greater than 10.")
            return

        random.seed(time.time())
        successes = 0
        throw_list = "\\["

        for i in range(0, dice_amount):
            single_throw = random.randint(1, 10)
            if single_throw == 1:
                successes -= 1
            elif single_throw == 10:
                successes += 2
            elif single_throw >= dice_difficulty:
                successes += 1
            if i == dice_amount - 1:
                throw_list = f"{throw_list}{single_throw}\\]"
            else:
                throw_list = f"{throw_list}{single_throw},"

        # Print result
        if successes < 0:
            await update.message.reply_text(f"`{dice_throw}`: *Botch\\!* `{throw_list}`", parse_mode=ParseMode.MARKDOWN_V2)
        elif successes == 0:
            await update.message.reply_text(f"`{dice_throw}`: *Failure\\! `{throw_list}`*", parse_mode=ParseMode.MARKDOWN_V2)
        elif successes == 1:
            await update.message.reply_text(f"`{dice_throw}`: *1* success `{throw_list}`", parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await update.message.reply_text(f"`{dice_throw}`: *{successes}* successes `{throw_list}`", parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await update.message.reply_text("Cannot parse the command argument. Check /commands for reference.")


def main() -> None:
    load_dotenv()
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()

    application.add_handler(CommandHandler("commands", commands))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("r", roll))
    application.add_handler(CommandHandler("full", full))
    application.add_handler(CommandHandler("f", full))

    # Interpret any other command or text message as a start of a private chat.
    # This will record the user as being in a private chat with bot.
    application.add_handler(MessageHandler(filters.ALL, start_private_chat))

    # Run the bot until the user presses Ctrl-C
    # We pass 'allowed_updates' handle *all* updates including `chat_member` updates
    # To reset this, simply pass `allowed_updates=[]`
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
