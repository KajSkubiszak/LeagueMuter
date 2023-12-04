from lcu_driver import Connector
from auto_play_music import play_music

connector = Connector()


@connector.ws.register("/lol-champ-select/v1/session", event_types=('CREATE',))
async def game_found(connection, event):
    me_result = await connection.request('get', '/lol-summoner/v1/current-summoner')
    me_json = await me_result.json()
    my_summoner_id = me_json['summonerId']

    session_result = await connection.request('get', '/lol-champ-select/v1/session')
    if session_result.status != 200:
        print("No lobby detected")
        return

    play_music()
    session_json = await session_result.json()
    muted_players = await connection.request('get', '/lol-champ-select/v1/muted-players')
    muted_players_json = await muted_players.json()
    muted_players_summoner_id = [x['summonerId'] for x in muted_players_json]

    friends = await connection.request('get', '/lol-chat/v1/friends')
    friends_json = await friends.json()
    friends_summoner_id = [x['summonerId'] for x in friends_json]

    actors = [x for x in session_json['myTeam'] if x['summonerId'] != my_summoner_id and x['summonerId'] not in muted_players_summoner_id and x['summonerId'] not in friends_summoner_id]

    for actor in actors:
        await connection.request('post', '/lol-champ-select/v1/toggle-player-muted',
                                 data={'summonerId': actor['summonerId'], 'puuid': actor['puuid']})

    print("All randoms muted")


@connector.ws.register("/lol-matchmaking/v1/ready-check", event_types=('UPDATE',))
async def instant_accept(connection, event):
    await connection.request("post", "/lol-matchmaking/v1/ready-check/accept")
    print('Game accepted')


@connector.ws.register("/lol-champ-select/v1/ongoing-trade", event_types=('CREATE',))
async def instant_decline_trade(connection, event):
    if event.data['initiatedByLocalPlayer']:
        return

    trade_id = event.data['id']

    trade_response = await connection.request("get", f"/lol-champ-select/v1/session/trades/{trade_id}")
    trade_json = await trade_response.json()
    cell_id = trade_json['cellId']

    summoner_result = await connection.request("get", f"/lol-champ-select/v1/summoners/{cell_id}")
    summoner_json = await summoner_result.json()
    summoner_id = summoner_json['summonerId']

    friends = await connection.request('get', '/lol-chat/v1/friends')
    friends_json = await friends.json()
    friends_summoner_id = [x['summonerId'] for x in friends_json]

    if summoner_id in friends_summoner_id:
        return

    await connection.request('post', f'/lol-champ-select/v1/session/trades/{trade_id}/decline')
    print('Trade auto declined')

connector.start()

