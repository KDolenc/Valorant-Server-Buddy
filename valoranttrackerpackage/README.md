# Valorant Tracker Package
Made by Kiel Dolenc 15/04/2024

## Description
A package to request and save the data of Valorant accounts.

## Setup
A txt file called "api-key.txt" will need to be made in the "valoranttackerpackage" folder.\
The file must contain your API key from https://henrikdev.xyz/.

## Information
Accounts and their data are stored in the accounts_data.json file.\
There are 2 account groups in this json file, "mains" and "smurfs".\
Each contains a list of accounts.\
Accounts are dictionaries with the following variables:\
"puuid", "user", "username", "tag", "elo", "current_rank", "highest_rank".

There is also a saves directory that saves a copy of the current accounts_data.json file if the save_data() function is called.

## Settings
### region
Determines which region, or "shard", to look for an account on.
Available regions are: eu, na, latam, br, ap, kr.

### accounts_data_path
Path to accounts_data.json.

### saves_path
Path to the saves folder.

## Functions
### update_accounts_data(account_group)
Updates an account group with current data.

### save_accounts_data()
Saves the current "accounts_data.json" file to the "valoranttrackerpackage/saves/{current date}.json" file.\
Will overwrite if there is already a file made on the same date.

### get_accounts_data(account_group)
Returns a list of dictionaries of each account within the chosen account group.

### add_account(account_group, user, username, tag)
Adds a new user to the chosen account group.\
Must provide the account group, a name for the account, and the desired username/tag.\
Can return errors "failed to find account_group" and "failed to find account".

### remove_account(account_group, user)
Removes an account from the chosen account group.\
Must provide the account group and the user's name.\
Can return errors "failed to find account_group" and "failed to find account".