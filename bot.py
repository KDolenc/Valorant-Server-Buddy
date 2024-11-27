from valoranttrackerpackage import valorantAPI

import discord

from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

# Returns the token for the bot in the discord-token.txt file.
def get_discord_token() -> str:
    discord_token_file = open("discord-token.txt", 'r')
    discord_token = discord_token_file.read()
    discord_token_file.close()
    
    return discord_token

# Logs an incoming read message to log.txt.
def log_message(author: str, message_tokens: list[str]) -> None:
    log_file = open("logs.txt", 'a')

    datetimenow = datetime.now()
    datetimenow = datetimenow.strftime("%d/%m/%Y %H:%M:%S")
    message = datetimenow + " " + author + ": "

    for message_token in message_tokens:
        message += message_token + " "

    log_file.write(message + "\n")

    log_file.close()

# Returns a string of accounts from an account group and their current elo.
async def get_elos(message_tokens: list[str], channel) -> str:
    # Checks if an account group was requested in the message.
    # If not, default to the first account group in accounts_data.json.
    if len(message_tokens) > 1:
        return "Too many tokens!"
    elif len(message_tokens) == 1:
        account_group = message_tokens[0]
    else:
        account_group = valorantAPI.get_account_groups()[0]

    # Returns an error message if the requested account group wasn't found.
    if account_group not in valorantAPI.get_account_groups():
        return "Account group not found!" 
    
    # Sends a loading message.
    loading_message = await channel.send("Retrieving data: 0% Complete")
    
    # Updates the data within the account_group.
    accounts_data = valorantAPI.get_accounts_data(account_group)
    i = 0
    for account in accounts_data:
            valorantAPI.update_account_data(account, account_group)
            i += 1
            # Updates the loading message to display to show the completion percentage.
            loading_text = "Retrieving data: " + str(int(i/len(accounts_data)*100)) + "% Complete"
            await loading_message.edit(content=loading_text)


    # Deletes the loading message.
    await loading_message.delete()

    message = "## VALORANT ELOS: "
    message += account_group.upper() + "\n>>> "
    for account in valorantAPI.get_accounts_data(account_group):
        message += account["user"] + ": " + str(account["elo"]) + '\n'

    return message

# Returns a string of accounts from an account group and their current ranks.
async def get_ranks(message_tokens: list[str], channel) -> str:
    # Checks if an account group was requested in the message.
    # If not, default to the first account group in accounts_data.json.
    if len(message_tokens) > 1:
        return "Too many tokens!"
    elif len(message_tokens) == 1:
        account_group = message_tokens[0]
    else:
        account_group = valorantAPI.get_account_groups()[0]
    
    # Returns an error message if the requested account group wasn't found.
    if account_group not in valorantAPI.get_account_groups():
        return "Account group not found!" 
    
    # Sends a loading message.
    loading_message = await channel.send("Retrieving data: 0% Complete")
    
    # Updates the data within the account_group.
    accounts_data = valorantAPI.get_accounts_data(account_group)
    i = 0
    for account in accounts_data:
            valorantAPI.update_account_data(account, account_group)
            i += 1
            # Updates the loading message to display to show the completion percentage.
            loading_text = "Retrieving data: " + str(int(i/len(accounts_data)*100)) + "% Complete"
            await loading_message.edit(content=loading_text)

    # Deletes the loading message.
    await loading_message.delete()

    message = "## VALORANT RANKS: "
    message += account_group.upper() + "\n>>> "
    for account in valorantAPI.get_accounts_data(account_group):
        message += account["user"] + ": " + account["current_rank"] + '\n'

    return message

async def get_distributions(message_tokens: list[str], channel) -> str:
    # Checks if an account group was requested in the message.
    # If not, default to the first account group in accounts_data.json.
    if len(message_tokens) > 1:
        return "Too many tokens!"
    elif len(message_tokens) == 1:
        account_group = message_tokens[0]
    else:
        account_group = valorantAPI.get_account_groups()[0]

    # Returns an error message if the requested account group wasn't found.
    if account_group not in valorantAPI.get_account_groups():
        return "Account group not found!" 
    
    # Returns an error message if the distribution data wasn't found.
    distribution_data = valorantAPI.get_distribution_data()
    if distribution_data == "failed to find distribution_data":
        return "Distribution data not found!"
    
    # Sends a loading message.
    loading_message = await channel.send("Retrieving data: 0% Complete")

    # Updates the data within the account_group.
    accounts_data = valorantAPI.get_accounts_data(account_group)
    i = 0
    for account in accounts_data:
            #valorantAPI.update_account_data(account, account_group)
            i += 1
            # Updates the loading message to display to show the completion percentage.
            loading_text = "Retrieving data: " + str(int(i/len(accounts_data)*100)) + "% Complete"
            await loading_message.edit(content=loading_text)
            
    # Deletes the loading message.
    await loading_message.delete()

    message = "## VALORANT RANK DISTRIBUTIONS: "
    message += account_group.upper() + "\n>>> "
    for account in valorantAPI.get_accounts_data(account_group):
        # If the account is Radiant then we don't calculate the distribution percentage.
        if account["current_rank"] == "Radiant":
            message += account["user"] + ": RADIANT\n"
            continue

        # Compares account current_rank with ranks in distribution_data.json.
        for x in range(len(distribution_data)):
            # Once there is a match found, the account's current rank and next rank are used to find the account's adjusted distribution.
            if account["current_rank"] == distribution_data[x]["rank"]:
                current_rank_distribution = distribution_data[x]["distribution"]
                next_rank_distribution = distribution_data[x + 1]["distribution"]

                # rank_progress is the account's elo between ranks.
                rank_progress = account["elo"] % 100

                # adjusted_distribution is calculated by finding the distributions of the current and next rank,
                # and using the rank_progress to find the value between them that the account is sitting at.
                adjusted_distribution = (((current_rank_distribution - next_rank_distribution) / 100 * (100 - rank_progress)) + next_rank_distribution)

        message += account["user"] + ": Top " + str(round(adjusted_distribution, 1)) + "%\n"

    return message

# Adds an account to the accounts_data file.
def add_account(message_tokens: list[str]) -> str:
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
def remove_account(message_tokens: list[str]) -> str:
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
def add_account_group(message_tokens: list[str]) -> str:
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
def remove_account_group(message_tokens: list) -> str:
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

def help() -> str:
    # Adds a commands list to the message.
    message = "## Commands List:\n> - elos [account_group]\n> - ranks [account_group]\n> - distributions [account_group]\n> - add [account_group] [user] [username] [tag]\n> - remove [account_group] [user]\n> - addgroup [account_group]\n> - removegroup [account_group]"

    # Adds a list of account groups in accounts_data.json to the message.
    account_groups = valorantAPI.get_account_groups()
    message += "\n## Account Groups"
    for account in account_groups:
        message += "\n> - " + account.capitalize()

    return message

# Called when a message is recieved/read by Valorant Server Buddy.
@bot.event
async def on_message(message) -> None:
    # Define apology variable for when the bot is unable to read/repond to a message.
    apology = "Sorry, I don't understand."
    
    # Ignore the bot's own messages.
    if message.author == bot.user:
        return

    # Turn incoming messages into lowercase tokens.
    message.content = message.content.lower()
    message_tokens = message.content.split()

    # Only read the message if it starts with "!valorant".
    # Will also log the message in log.txt.
    if message_tokens[0] == "!valorant":
        log_message(message.author.name, message_tokens)
        message_tokens.pop(0)
    else:
        return

    if len(message_tokens) == 0:
        await message.channel.send(help())
        return
    
    if message_tokens[0] == "help":
        await message.channel.send(help())

    elif message_tokens[0] == "elo" or message_tokens[0] == "elos":
        message_tokens.pop(0)
        await message.channel.send(await get_elos(message_tokens, message.channel))

    elif message_tokens[0] == "rank" or message_tokens[0] == "ranks":
        message_tokens.pop(0)
        await message.channel.send(await get_ranks(message_tokens, message.channel))

    elif message_tokens[0] == "dist" or message_tokens[0] == "dists" or message_tokens[0] == "distribution" or message_tokens[0] == "distributions":
        message_tokens.pop(0)
        await message.channel.send(await get_distributions(message_tokens, message.channel))

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

    else:
        await message.channel.send(apology)
    
    return

if __name__ == "__main__":
    bot.run(get_discord_token())