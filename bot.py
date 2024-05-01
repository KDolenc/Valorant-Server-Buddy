from valoranttrackerpackage import valorantAPI

import discord

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

def get_token():
    token_file = open("token.txt", 'r')
    token = token_file.read()
    token_file.close()
    return token

# Returns a string of main accounts and their current elo.
def get_elos():
    valorantAPI.update_accounts_data("mains")

    message = "## VALORANT ELOS \n>>> "
    for account in valorantAPI.get_accounts_data("mains"):
        message += account["user"] + ": " + str(account["elo"]) + '\n'

    return message

# Returns a string of main accounts and their current ranks.
def get_ranks():
    valorantAPI.update_accounts_data("mains")

    message = "## VALORANT RANKS \n>>> "
    for account in valorantAPI.get_accounts_data("mains"):
        message += account["user"] + ": " + account["current_rank"] + '\n'

    return message

# Returns a string of smurf accounts and their current ranks.
def get_smurfs():
    valorantAPI.update_accounts_data("smurfs")

    message = "## VALORANT SMURF RANKS \n>>> "
    for account in valorantAPI.get_accounts_data("smurfs"):
        message += account["user"] + ": " + account["current_rank"] + '\n'

    return message

# Adds an account to the accounts_data file.
def add_account(tokens):
    # Ensure there are the right amount of tokens (4).
    if len(tokens) < 4:
        return "Not enough tokens!"
    elif len(tokens) > 4:
        return "Too many tokens!"
    
    account_group = tokens[0]
    user = tokens[1]
    username = tokens[2]
    tag = tokens[3]

    # Check if there are any errors when running add_account().
    # valorantAPI.add_account() returns error codes if a problem occurs.
    error_code = valorantAPI.add_account(account_group, user, username, tag)
    # Error if the account_group isnt in the accounts_data.json file.
    if error_code == "failed to find account_group":
        return "Account group not found!"
    # Error if the account doesn't exist.
    elif error_code == "failed to find account":
        return "Account doesn't exist!"
    
    else:
        return user.capitalize() + " has been added!"

# Removes an account from the accounts_data file.
def remove_account(tokens):
    # Ensure there are the right amount of tokens (2).
    if len(tokens) < 2:
        return "Not enough tokens!"
    elif len(tokens) > 2:
        return "Too many tokens!"

    account_group = tokens[0]
    user = tokens[1]

    # Check if there are any errors when running remove_account().
    # valorantAPI.remove_account() returns error codes if a problem occurs.
    error_code = valorantAPI.remove_account(account_group, user)
    # Error if the account_group isnt in the accounts_data.json file.
    if error_code == "failed to find account_group":
        return "Account group not found!"
    # Error if the account isnt in the accounts_data.json file.
    elif error_code == "failed to find account":
        return "Account not found!"
    
    else:
        return user.capitalize() + " has been removed!"

def help():
    return "Commands List:\n>>> - add [account_group] [user] [username] [tag]\n- remove [account_group] [user]\n- elos\n- ranks\n- smurfs\n"

# Called when a message is recieved/read by Valorant Server Buddy.
@bot.event
async def on_message(message):
    apology = "Sorry, I don't understand."
    # Ignore the bot's own messages.
    if message.author == bot.user:
        return

    # Turn incoming messages into lowercase tokens.
    message.content = message.content.lower()
    tokens = message.content.split()

    # Only read the message if it starts with "valorant":
    if tokens[0] == "!valorant":
        tokens.pop(0)
    else:
        return

    if tokens[0] == "add":
        tokens.pop(0)
        await message.channel.send(add_account(tokens))

    elif tokens[0] == "remove":
        tokens.pop(0)
        await message.channel.send(remove_account(tokens))

    elif tokens[0] == "elos":
        try:
            await message.channel.send(get_elos())
        except:
            await message.channel.send(apology)

    elif tokens[0] == "ranks":
        try:
            await message.channel.send(get_ranks())
        except:
            await message.channel.send(apology)

    elif tokens[0] == "smurfs":
        try:
            await message.channel.send(get_smurfs())
        except:
            await message.channel.send(apology)

    elif tokens[0] == "help":
        await message.channel.send(help())

    else:
        await message.channel.send(apology)
    
    return

bot.run(get_token())