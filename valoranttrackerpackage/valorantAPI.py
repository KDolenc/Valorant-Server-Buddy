from datetime import date
import os
import requests
import json

# Retrieves the value of a setting in the settings.json file.
def get_setting(setting: str) -> str:
    settings_file = open("valoranttrackerpackage/settings.json", "r")
    data = json.load(settings_file)
    settings_file.close()

    return data[setting]

# Retrieves the Valorant API key (from https://henrikdev.xyz/).
def get_api_key() -> str:
    key_file = open(get_setting("HDEV_api_key_path"), 'r')
    key = key_file.read()
    key_file.close()
    
    return key

# Opens accounts_data.json, saves what is given and closes the file.
def write_to_accounts_data(data: dict) -> None:
    accounts_file = open(get_setting("accounts_data_path"), "w")
    accounts_file.write(json.dumps(data, indent=4))
    accounts_file.close()

# Create a new empty accounts_data.json file.
def create_accounts_data_file() -> None:
    write_to_accounts_data({})

# Opens/closes accounts_data.json and returns the data.
def open_accounts_data() -> dict:
    # Try and open/save current accounts file to the "data" variable.
    try:
        accounts_file = open(get_setting("accounts_data_path"), "r")
    # If this is unsuccessful (because the accounts_data.json doesn't exist/can't be located), we create a new empty accounts_data.json file and try again.
    except:
        create_accounts_data_file()
        accounts_file = open(get_setting("accounts_data_path"), "r")
    
    accounts_data = json.load(accounts_file)
    accounts_file.close()

    return accounts_data

# Retrieves account data from the api.henrikdev.xyz.
def request_account_data(puuid: str) -> dict:
    request = requests.get(get_setting("api_url") + get_setting("api_subdirectory_account_data") + get_setting("region") + puuid + "?api_key=" + get_api_key())
    data = request.text
    loaded = json.loads(data)

    # Returns str "failed" if failed to retrieve data.
    try:
        loaded["status"] != 200
    except:
        return "failed"
    
    return loaded

# Sorts the updated data by elo.
def sort_by_elo(account: dict) -> int:
    return account["elo"]

# Updates an account with current data.
def update_account_data(account: list, account_group: str) -> list:
    account_data = request_account_data(account["puuid"])

    # Skips updating the account if failed to retrieve data from the API.
    if account_data == "failed":
        print("Failed to retrieve data for account:", account["user"])
        return account
    else:
        print("Retrieved data for account:", account["user"])

        account["username"] = account_data["data"]["name"]
        account["tag"] = account_data["data"]["tag"]
        account["elo"] = account_data["data"]["current_data"]["elo"]
        account["current_rank"] = account_data["data"]["current_data"]["currenttierpatched"]
        account["highest_rank"] = account_data["data"]["highest_rank"]["patched_tier"]

    # Opens the accounts_data.json file and checks if the given account group exists.
    # If not, returns an error.
    accounts_data = open_accounts_data()
    try:
        accounts_data[account_group]
    except:
        return "failed to find account_group"

    # Applies changes to "accounts_data" variable from "account" variable.
    for acc in accounts_data[account_group]:
        if acc["puuid"] == account["puuid"]:
            acc["username"] = account["username"]
            acc["tag"] = account["tag"]
            acc["elo"] = account["elo"]
            acc["current_rank"] = account["current_rank"]
            acc["highest_rank"] = account["highest_rank"]
        
    # Sort the updated data by elo.
    accounts_data[account_group].sort(reverse = True, key=sort_by_elo)

    # Overwrite the accounts file with the changes in the "accounts_data" variable.
    write_to_accounts_data(accounts_data)
    
    # Can return the account if the updated data is needed.
    # However, not using this returned list doesn't matter, as the accounts_data.json is still updated.
    return account

# Updates an account group with current data.
def update_account_group_data(account_group: str) -> None:
    # Opens the accounts_data.json file and checks if the given account group exists.
    # If not, returns an error.
    accounts_data = open_accounts_data()
    try:
        accounts_data[account_group]
    except:
        return "failed to find account_group"

    # Loop through all accounts within the account group.
    # Update username, tag, elo, current and highest rank with newly downloaded data.
    for account in accounts_data[account_group]:
            update_account_data(account)
    
    # Sort the updated data by elo.
    accounts_data[account_group].sort(reverse = True, key=sort_by_elo)

    # Overwrite the accounts file with the changes in the "accounts_data" variable.
    write_to_accounts_data(accounts_data)

# Saves the current accounts_data.json file to the "valoranttrackerpackage/saves/{current date}.json" file.
# Will overwrite if there is already a file made on the same date.
def save_accounts_data() -> None:
    # Check if save folder exists.
    # If not, create a new saves folder.
    if os.path.exists(os.path.abspath(os.getcwd()) + '/' + get_setting("saves_path")) != True:
        os.mkdir(get_setting("saves_path"))

    save_location = get_setting("saves_path") + str(date.today()) + ".json"
    save_file = open(save_location, "w")

    accounts_data = open_accounts_data()

    save_file.write(json.dumps(accounts_data))
    save_file.close()

# Returns a list of dictionaries of each account within the chosen account group.
def get_accounts_data(account_group: str) -> list[dict]:
    accounts_data = open_accounts_data()

    accounts = []
    for account in accounts_data[account_group]:
        accounts.append(account)
        
    return accounts

# Adds a new user to the chosen account group.
# Must provide the account group, a name for the account, and the desired username/tag.
def add_account(account_group: str, user: str, username: str, tag: str) -> None:
    accounts_data = open_accounts_data()
        
    # Check if the account_group provided is valid.
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

    # Save what we have in accounts_data.json to a temporary "accounts_data" variable.
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
def remove_account(account_group: str, user: str) -> None:
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

    # Remove the requested user from the accounts_data variable.
    try:
        accounts_data[account_group].pop(i)
    # Error if the account isn't in accounts_group.
    except:
        return "failed to find account"

    # Save to accounts_data.json.
    write_to_accounts_data(accounts_data)

# Adds a new account group to accounts_data.json.
def add_account_group(group_name: str) -> None:
    accounts_data = open_accounts_data()

    # Checks if the account group is already in accounts_data.json.
    # If so, return an error.
    try:
        accounts_data[group_name]
        return "account_group already exists"
    except:
        pass

    # Create new account group and saves to accounts_data.json.
    accounts_data[group_name] = []
    write_to_accounts_data(accounts_data)

# Removes an account group from accounts_data.json.
def remove_account_group(group_name: str) -> None:
    accounts_data = open_accounts_data()
    
    # Returns an error if the account_group doensn't exist.
    try:
        accounts_data[group_name]
    except:
        return "failed to find account_group"

    # Removes the account_group and saves to accounts_data.json.
    accounts_data.pop(group_name)
    write_to_accounts_data(accounts_data)

# Returns a list of the account groups in accounts_data.json.
def get_account_groups() -> list[str]:
    accounts_data = open_accounts_data()

    return list(accounts_data.keys())