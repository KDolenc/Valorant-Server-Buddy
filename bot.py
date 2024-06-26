from valoranttrackerpackage import valorantAPI

import discord

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

# Returns the token for the bot in the discord-token.txt file.
def get_discord_token():
    discord_token_file = open("discord-token.txt", 'r')
    discord_token = discord_token_file.read()
    discord_token_file.close()
    
    return discord_token

# Returns a string of accounts from an account group and their current elo.
def get_elos(message_tokens):
    # Checks if an account group was requested in the message.
    # If not, default to the first account group in accounts_data.json.
    if len(message_tokens) > 1:
        return "Too many tokens!"
    elif len(message_tokens) == 1:
        account_group = message_tokens[0]
    else:
        account_group = valorantAPI.get_account_groups()[0]
    
    # Returns an error message if the requested account group wasn't found.
    error_code = valorantAPI.update_accounts_data(account_group)
    if error_code == "failed to find account_group":
        return "Account group not found!"

    message = "## VALORANT ELOS \n>>> "
    for account in valorantAPI.get_accounts_data(account_group):
        message += account["user"] + ": " + str(account["elo"]) + '\n'

    return message

# Returns a string of accounts from an account group and their current ranks.
def get_ranks(message_tokens):
    # Checks if an account group was requested in the message.
    # If not, default to the first account group in accounts_data.json.
    if len(message_tokens) > 1:
        return "Too many tokens!"
    elif len(message_tokens) == 1:
        account_group = message_tokens[0]
    else:
        account_group = valorantAPI.get_account_groups()[0]
    
    # Returns an error message if the requested account group wasn't found.
    error_code = valorantAPI.update_accounts_data(account_group)
    if error_code == "failed to find account_group":
        return "Account group not found!"

    message = "## VALORANT RANKS \n>>> "
    for account in valorantAPI.get_accounts_data(account_group):
        message += account["user"] + ": " + account["current_rank"] + '\n'

    return message

# Adds an account to the accounts_data file.
def add_account(message_tokens):
    # Ensure there are the right amount of message tokens (4).
    if len(message_tokens) < 4:
        return "Not enough tokens!"
    elif len(message_tokens) > 4:
        return "Too many tokens!"
    
    account_group = message_tokens[0]
    user = message_tokens[1]
    username = message_tokens[2]
    tag = message_tokens[3]

    # Check if there are any errors when running add_account().
    # valorantAPI.add_account() returns error codes if a problem occurs.
    error_code = valorantAPI.add_account(account_group, user, username, tag)
    # Error if the account_group isnt in accounts_data.json.
    if error_code == "failed to find account_group":
        return "Account group not found!"
    # Error if the account doesn't exist.
    elif error_code == "failed to find account":
        return "Account doesn't exist!"
    
    else:
        return user.capitalize() + " has been added!"

# Removes an account from the accounts_data file.
def remove_account(message_tokens):
    # Ensure there are the right amount of message tokens (2).
    if len(message_tokens) < 2:
        return "Not enough tokens!"
    elif len(message_tokens) > 2:
        return "Too many tokens!"

    account_group = message_tokens[0]
    user = message_tokens[1]

    # Check if there are any errors when running remove_account().
    # valorantAPI.remove_account() returns error codes if a problem occurs.
    error_code = valorantAPI.remove_account(account_group, user)
    # Error if the account_group isnt in accounts_data.json.
    if error_code == "failed to find account_group":
        return "Account group not found!"
    # Error if the account isnt in accounts_data.json.
    elif error_code == "failed to find account":
        return "Account not found!"
    
    else:
        return user.capitalize() + " has been removed!"

# Adds a new account group to the accounts_data.json file.
def add_account_group(message_tokens):
    # Ensure there are the right amount of message tokens (2).
    if len(message_tokens) < 1:
        return "Not enough tokens!"
    elif len(message_tokens) > 1:
        return "Too many tokens!"
    
    account_group = message_tokens[0]

    # Check if there is an error when running add_account_group().
    # valorantAPI.add_account_group() returns an error code if a problem occurs.
    error_code = valorantAPI.add_account_group(account_group)
    # Error if the account already exists in accounts_data.json.
    if error_code == "account_group already exists":
        return "Account group already exists!"

# Removes an account group from the accounts_data.json file.
def remove_account_group(message_tokens):
    # Ensure there are the right amount of message tokens (2).
    if len(message_tokens) < 1:
        return "Not enough tokens!"
    elif len(message_tokens) > 1:
        return "Too many tokens!"
    
    account_group = message_tokens[0]

    # Check if there is an error when running remove_account_group().
    # valorantAPI.remove_account_group() returns an error code if a problem occurs.
    error_code = valorantAPI.remove_account_group(account_group)
    # Error if the account is unable to be found in accounts_data.json.
    if error_code == "failed to find account_group":
        return "Account group not found!"

def help():
    # Adds a commands list to the message.
    message = "## Commands List:\n> - elos [account_group]\n> - ranks [account_group]\n> - add [account_group] [user] [username] [tag]\n> - remove [account_group] [user]\n> - addgroup [account_group]\n> - removegroup [account_group]"

    # Adds a list of account groups in accounts_data.json to the message.
    account_groups = valorantAPI.get_account_groups()
    message += "\n## Account Groups"
    for account in account_groups:
        message += "\n> - " + account.capitalize()

    return message

# Called when a message is recieved/read by Valorant Server Buddy.
@bot.event
async def on_message(message):
    # Define apology variable for when the bot is unable to read/repond to a message.
    apology = "Sorry, I don't understand."
    
    # Ignore the bot's own messages.
    if message.author == bot.user:
        return

    # Turn incoming messages into lowercase tokens.
    message.content = message.content.lower()
    message_tokens = message.content.split()

    # Only read the message if it starts with "!valorant".
    if message_tokens[0] == "!valorant":
        message_tokens.pop(0)
    else:
        return

    if message_tokens[0] == "elo" or message_tokens[0] == "elos":
        try:
            message_tokens.pop(0)
            await message.channel.send(get_elos(message_tokens))
        except:
            await message.channel.send(apology)

    elif message_tokens[0] == "rank" or message_tokens[0] == "ranks":
        try:
            message_tokens.pop(0)
            await message.channel.send(get_ranks(message_tokens))
        except:
            await message.channel.send(apology)

    elif message_tokens[0] == "add":
        message_tokens.pop(0)
        await message.channel.send(add_account(message_tokens))

    elif message_tokens[0] == "remove":
        message_tokens.pop(0)
        await message.channel.send(remove_account(message_tokens))

    elif message_tokens[0] == "addgroup":
        message_tokens.pop(0)
        await message.channel.send(add_account_group(message_tokens))

    elif message_tokens[0] == "removegroup":
        message_tokens.pop(0)
        await message.channel.send(remove_account_group(message_tokens))

    elif message_tokens[0] == "help":
        await message.channel.send(help())

    else:
        await message.channel.send(apology)
    
    return

bot.run(get_discord_token())