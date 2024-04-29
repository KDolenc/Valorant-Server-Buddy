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

def help():
    return "Commands List:\n>>> - elo\n- ranks\n- smurfs\n"

# Called when a message is recieved/read by Valorant Server Buddy.
@bot.event
async def on_message(message):
    apology = "Sorry, I don't understand."
    # Ignore the bot's own messages.
    if message.author == bot.user:
        return

    # Turn incoming messages into clowercase.
    message.content = message.content.lower()

    # Only ready the message if it starts with "valorant":
    if message.content.startswith("!valorant"):
        message.content = message.content.replace("!valorant ", "")
    else:
        return

    if "elo" in message.content:
        try:
            await message.channel.send(get_elos())
        except:
            await message.channel.send(apology)

    elif "rank" in message.content:
        try:
            await message.channel.send(get_ranks())
        except:
            await message.channel.send(apology)

    elif "smurf" in message.content:
        try:
            await message.channel.send(get_smurfs())
        except:
            await message.channel.send(apology)

    elif "help" in message.content:
        await message.channel.send(help())

    else:
        await message.channel.send(apology)
    
    return

bot.run(get_token())