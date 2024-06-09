from datetime import date

import requests
import json

def get_api_key():
    key_file = open("valoranttrackerpackage/api-key.txt", 'r')
    key = key_file.read()
    key_file.close()
    return key

# Retrieves the value of a setting in the settings.json file.
def get_setting(setting):
    settings_file = open("valoranttrackerpackage/settings.json", "r")
    data = json.load(settings_file)
    settings_file.close()

    return data[setting]

# Opens accounts_data.json, saves what is given and closes the file.
def write_to_accounts_data(data):
    accounts_file = open(get_setting("accounts_data_path"), "w")
    accounts_file.write(json.dumps(data, indent=4))
    accounts_file.close()

# Create a new empty accounts_data.json file.
def create_accounts_data_file():
    write_to_accounts_data({"mains": [], "smurfs":[]})

# Opens/closes accounts_data.json and returns the data.
def open_accounts_data():
    accounts_file = open(get_setting("accounts_data_path"), "r")
    accounts_data = json.load(accounts_file)
    accounts_file.close()

    return accounts_data

# Retrieves account data from the api.henrikdev.xyz.
def request_account_data(puuid):
    request = requests.get(get_setting("api_url") + get_setting("api_subdirectory_account_data") + get_setting("region") + puuid + "?api_key=" + get_api_key())
    data = request.text
    loaded = json.loads(data)

    # Returns str "failed" if failed to retrieve data.
    if loaded["status"] != 200:
        return "failed"
    else:
        return loaded

# Sorts the updated data by elo.
def sort_by_elo(account):
    return account["elo"]

# Updates an account group with current data.
def update_accounts_data(account_group):
    # Try and open/save current accounts file to the "data" variable.
    try:
        accounts_data = open_accounts_data()
    # If this is unsuccessful (because the accounts_data.json doesn't exist/can't be located), we create a new empty accounts_data.json file and try again.
    except:
        create_accounts_data_file()
        
        accounts_data = open_accounts_data()

    # Loop through all accounts within the account group.
    # Update username, tag, elo, current and highest rank with newly downloaded data.
    for account in accounts_data[account_group]:
            account_data = request_account_data(account["puuid"])

            # Skips updating the account if failed to retrieve data from the API.
            if account_data == "failed":
                print("Failed to retrieve data for account:", account["user"])
                continue
            else:
                print("Retrieved data for account:", account["user"])

            account["username"] = account_data["data"]["name"]
            account["tag"] = account_data["data"]["tag"]
            account["elo"] = account_data["data"]["current_data"]["elo"]
            account["current_rank"] = account_data["data"]["current_data"]["currenttierpatched"]
            account["highest_rank"] = account_data["data"]["highest_rank"]["patched_tier"]
    
    # Sort the updated data by elo.
    accounts_data[account_group].sort(reverse = True, key=sort_by_elo)

    # Overwrite the accounts file with the changes in the "data" variable.
    write_to_accounts_data(accounts_data)

# Saves the current "accounts_data.json" file to the "valoranttrackerpackage/saves/{current date}.json" file.
# Will overwrite if there is already a file made on the same date.
def save_accounts_data():
    save_location = get_setting("saves_path") + str(date.today()) + ".json"
    save_file = open(save_location, "w")

    accounts_data = open_accounts_data()

    save_file.write(json.dumps(accounts_data))
    save_file.close()

# Returns a list of dictionaries of each account within the chosen account group.
def get_accounts_data(account_group):
    accounts_data = open_accounts_data()

    accounts = []
    for account in accounts_data[account_group]:
        accounts.append(account)
        
    return accounts

# Not implemented yet.
def add_account_group():
    pass

# Not implemented yet.
def remove_account_group():
    pass

# Adds a new user to the chosen account group.
# Must provide the account group, a name for the account, and the desired username/tag.
def add_account(account_group, user, username, tag):
    # Check if the account_group provided is valid.
    accounts_data = open_accounts_data()
    try: 
        accounts_data[account_group]
    # Returns an error if the account_group provided isnt valid.
    except:
        return "failed to find account_group"

    # Find new_account_data for the new account.
    # Only doing this to get the puuid from the provided username/tag.
    request = requests.get(get_setting("api_url") + get_setting("api_subdirectory_puuid") + get_setting("region") + username + '/' + tag + "?api_key=" + get_api_key())
    data = request.text
    new_account_data = json.loads(data)

    # Returns an error if failed to retrieve player data.
    if new_account_data["status"] != 200:
        return "failed to find account"

    # The puuid then needs to be put through our request_account_data() function to get the rest of the data we're after.
    new_account_puuid = new_account_data["data"]["puuid"]
    new_account_data = request_account_data(new_account_puuid)

    # With the rest of the data we can construct a dictionary for the new_account.
    new_account = {
        "puuid": new_account_puuid,
        "user": user.capitalize(),
        "username": new_account_data["data"]["name"],
        "tag": new_account_data["data"]["tag"],
        "elo": new_account_data["data"]["current_data"]["elo"],
        "current_rank": new_account_data["data"]["current_data"]["currenttierpatched"],
        "highest_rank": new_account_data["data"]["highest_rank"]["patched_tier"]
    }

    # Save what we have in accounts_data.json to a temporary "account_data" variable.
    accounts_data = open_accounts_data()

    # Add our new_accout to the temporary accounts_data variable.
    # accounts_data should now contain all mains/smurf accounts, including our new_account.
    new_account_group = accounts_data[account_group]
    new_account_group.append(new_account)
    accounts_data[account_group] = new_account_group

    # Sort mains by elo.
    accounts_data[account_group].sort(reverse = True, key=sort_by_elo)

    # Save to accounts_data.json.
    write_to_accounts_data(accounts_data)

# Removes an account from the chosen account group.
# Must provide the account group and the user's name.
def remove_account(account_group, user):
    # Check if the account_group provided is valid.
    accounts_data = open_accounts_data()
    try: 
        accounts_data[account_group]
    # Returns an error if the account_group provided isnt valid.
    except:
        return "failed to find account_group"

    # Save what we have in accounts_data.json to a temporary "accounts_data" variable.
    accounts_data = open_accounts_data()

    # Finds where in accounts_data the requested user is.
    i = 0
    for account in accounts_data[account_group]:
        if account["user"].lower() == user:
            break
        i += 1

    # Remove the requested user from the account_data variable.
    try:
        accounts_data[account_group].pop(i)
    # Error if the account isn't in accounts_group.
    except:
        return "failed to find account"

    # Save to accounts_data.json.
    write_to_accounts_data(accounts_data)