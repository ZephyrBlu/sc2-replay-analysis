import json
import csv

# generate CSV data for Jupyter Notebook from database replay data

csv_data = [(
    'file_hash',
    'player',
    'race',
    'opp_race',
    'mmr',
    'opp_mmr',
    'win',
    'match_length',
    'played_at',
    'map',
    'apm',
    'spm',
    'sq',
    'workers_produced',
    'workers_lost',
    'workers_killed',
    'supply_block',
    'avg_mineral_unspent',
    'avg_gas_unspent',
    'avg_mineral_rate',
    'avg_gas_rate',
    'mineral_collected',
    'gas_collected',
    'mineral_lost',
    'gas_lost',
    'avg_time_to_mine',
    'collection_rate_ahead',
    'avg_collection_rate_amount_ahead',
    'avg_collection_rate_lead_lag',
    'army_value_ahead',
    'avg_army_value_amount_ahead',
    'avg_army_value_lead_lag',
    'resources_lost_ahead',
    'avg_resources_lost_amount_ahead',
    'avg_resources_lost_lead_lag',
)]


def check_user_id(user_id, replay):
    if replay['user_match_id'] == user_id:
        return replay['win']
    return not replay['win']


errors = 0
none_replays = 0
none_wins = 0

with open('replay_data.json', 'r', encoding='utf-8') as data:
    replay_data = json.load(data)['data']

    for replay in replay_data:
        if 'inject_count' in replay['match_data']:
            errors += 1
            continue

        if replay['user_match_id'] is None:
            none_replays += 1
            continue

        if replay['win'] is None:
            none_wins += 1
            continue

        player_data = {1: None, 2: None}
        for i in range(1, 3):
            current_id = str(i)
            opp_id = '1' if i == 2 else '2'

            player_data[i] = (
                replay['file_hash'],
                i,
                replay['players'][current_id]['race'],
                replay['players'][opp_id]['race'],
                replay['match_data']['mmr'][current_id],
                replay['match_data']['mmr'][opp_id],
                check_user_id(i, replay),
                replay['match_length'],
                replay['played_at'],
                replay['map'],
                replay['match_data']['apm'][current_id],
                replay['match_data']['spm'][current_id],
                replay['match_data']['sq'][current_id],
                replay['match_data']['workers_produced'][current_id],
                replay['match_data']['workers_lost'][current_id],
                replay['match_data']['workers_killed'][current_id],
                replay['match_data']['supply_block'][current_id],
                replay['match_data']['avg_unspent_resources']['minerals'][current_id],
                replay['match_data']['avg_unspent_resources']['gas'][current_id],
                replay['match_data']['avg_resource_collection_rate']['minerals'][current_id],
                replay['match_data']['avg_resource_collection_rate']['gas'][current_id],
                replay['match_data']['resources_collected']['minerals'][current_id],
                replay['match_data']['resources_collected']['gas'][current_id],
                replay['match_data']['resources_lost']['minerals'][current_id],
                replay['match_data']['resources_lost']['gas'][current_id],
                replay['time_to_mine'][current_id],
                replay['resource_collection_rate_all']['ahead'] if replay['user_match_id'] == i else replay['resource_collection_rate_all']['behind'],
                replay['resource_collection_rate_all']['amount_ahead'][1] if replay['user_match_id'] == i else replay['resource_collection_rate_all']['amount_behind'][1],
                replay['resource_collection_rate_all']['lead_lag'][1] if replay['user_match_id'] == i else 1 - replay['resource_collection_rate_all']['lead_lag'][1],
                replay['total_army_value']['ahead'] if replay['user_match_id'] == i else replay['total_army_value']['behind'],
                replay['total_army_value']['amount_ahead'][1] if replay['user_match_id'] == i else replay['total_army_value']['amount_behind'][1],
                replay['total_army_value']['lead_lag'][1] if replay['user_match_id'] == i else 1 - replay['total_army_value']['lead_lag'][1],
                replay['total_resources_lost']['ahead'] if replay['user_match_id'] == i else replay['total_resources_lost']['behind'],
                replay['total_resources_lost']['amount_ahead'][1] if replay['user_match_id'] == i else replay['total_resources_lost']['amount_behind'][1],
                replay['total_resources_lost']['lead_lag'][1] if replay['user_match_id'] == i else 1 - replay['total_resources_lost']['lead_lag'][1],
            )

        csv_data.append(player_data[1])
        csv_data.append(player_data[2])

with open('replay_data.csv', 'w', encoding='utf-8', newline='') as output:
    writer = csv.writer(output)
    writer.writerows(csv_data)

print(f'There were {errors} errors')
print(f'{none_replays} replays did not have a user ID')
print(f'{none_wins} replays did not have a winner')
print(f'{len(csv_data)} replays in cleaned dataset')
