from steam import WebAPI
from steam import steamid
import valve.source.a2s

api = WebAPI("YOUR STEAM KEY GOES HERE")

SERVER_USERS = []
POSSIBLE_GROUP = []


def compareGroups(friend_info, server_users):
    # Checks for similar names player's friends and server's users

    print("[+] Comparing data.")

    group = {}

    for name in friend_info.keys():
        if name in server_users:
            print("[-] Found relationship with {}.".format(name))
            group[name] = friend_info[name]

    if len(group) is 0:
        print("[-] Found no relationships.")
        return

    return group

def getPlayerInfo(id):
    # Get player information from a URL

    user_data = api.call("ISteamUser.GetPlayerSummaries", steamids=id, format="json")

    user_name = user_data["response"]["players"][0]["personaname"]
    user_vis_state = user_data["response"]["players"][0]["communityvisibilitystate"]

    if user_vis_state is 1:
        print("[-] {}'s profile is private.".format(user_name))
        return
    elif user_vis_state is 3:
        print("[-] Found {}'s profile data.".format(user_name))

    try:
        user_game = user_data["response"]["players"][0]["gameextrainfo"]
    except:
        print("[-] User is not in game or game data is unavailable.")
        return

    try:
        user_game_ip_unparsed = user_data["response"]["players"][0]["gameserverip"]
    except:
        print("[-] Unable to get game server IP.")
        return

    user_game_ip_port = user_game_ip_unparsed.split(":")

    game_ip = user_game_ip_port[0]

    game_port = user_game_ip_port[1]

    print("[-] Found {}'s server: {} - {}:{}".format(user_name, user_game, game_ip, game_port))

    friend_info = getFriends(id)

    server_users = getPlayerList(game_ip, game_port)

    group = compareGroups(friend_info, server_users)

    return group


def getName(friend_id, num):
    # Gets the name of a user from their steam64id

    print("[-] Friend [{}] ID: {}".format(num, friend_id))

    friend_data = api.call("ISteamUser.GetPlayerSummaries", steamids=friend_id, format="json")

    friend_name = friend_data["response"]["players"][0]["personaname"]

    print("[-] Friend [{}] ID: {}".format(num, friend_name))

    return friend_name


def getFriends(id):
    # Returns an array of the user's friends

    try:
        user_friends = api.call("ISteamUser.GetFriendList", steamid=id, relationship="friend", format="json")
    except:
        print("[+] Could not receive user's friendlist.")
        return

    friend_info = {}

    print("[+] Evaluating friends.")

    for i in range(len(user_friends["friendslist"]["friends"])):
        friend_id = user_friends["friendslist"]["friends"][i]["steamid"]
        friend_name = getName(friend_id, i)

        friend_info[friend_name] = friend_id

    return friend_info

def getPlayerList(ip, port):
    # Returns list of player names in a server

    SERVER_ADDRESS = (ip, int(port))

    with valve.source.a2s.ServerQuerier(SERVER_ADDRESS) as server:
        for player in server.players()["players"]:
            if player["name"]:
                SERVER_USERS.append(player["name"])
                print("[-] Player Found: {}".format(player["name"]))

    print("[+] Found {} players in server.".format(len(SERVER_USERS)))

    return SERVER_USERS


def main():

    player_url = input("[+] Player's URL: ")
    player_id = steamid.steam64_from_url(player_url)

    if player_id is None:
        print("[-] Invalid URL.")
    else:
        print("[-] Found ID: {}".format(player_id))

    group = getPlayerInfo(player_id)

    POSSIBLE_GROUP = group

    print("[-] Possible group: {}".format(POSSIBLE_GROUP))

    check_friends = input("Check group members? (Y/N) ")

    if check_friends is not "Y":
        print("[+] Ending.")
        return

    friend_groups = {}

    for username, userid in POSSIBLE_GROUP.items():

        print("[+] Checking userid: {}".format(userid))
        friend_group = getPlayerInfo(userid)

        try:
            friend_groups = {**friend_groups, **friend_group}
        except:
            print("[-] Could not get friend's info.")
            continue

    main_group = {**POSSIBLE_GROUP, **friend_groups}

    print("[-] Final possible group: {}".format(main_group))

if __name__ == "__main__":
    main()
