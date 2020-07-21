import json
from pathlib import Path
from sc2_tournament_analysis import recursive_parse
from multiprocessing import Pool
from zephyrus_sc2_parser import parse_replay
from utils import process_data


def generate_prediction_data(players, timeline, stats, metadata, path):
    replay = {
        'players': players,
        'match_data': stats,
        'match_length': metadata['game_length'],
        'played_at': metadata['time_played_at'],
        'map': metadata['map'],
        'winner': metadata['winner'],
    }
    replay_data = process_data(replay, timeline)
    prediction_data = []

    for i in range(1, 3):
        resource_data = {
            'resources_lost': replay_data['match_data']['resources_lost']['minerals'][i] + replay_data['match_data']['resources_lost']['gas'][i],
            'resources_collected': replay_data['match_data']['resources_collected']['minerals'][i] + replay_data['match_data']['resources_collected']['gas'][i],
            'collection_rate': replay_data['match_data']['avg_resource_collection_rate']['minerals'][i] + replay_data['match_data']['avg_resource_collection_rate']['gas'][i],
        }

        prediction_data.append([
            replay_data['match_data']['apm'][i],
            replay_data['match_data']['spm'][i],
            replay_data['match_data']['sq'][i],
            replay_data['match_data']['supply_block'][i],
            replay_data['time_to_mine'][i],
            replay_data['resource_collection_rate_all']['ahead'] if i == 1 else replay_data['resource_collection_rate_all']['behind'],
            replay_data['total_army_value']['ahead'] if i == 1 else replay_data['total_army_value']['behind'],
            resource_data['collection_rate'],
            (1 - (resource_data['resources_lost'] / resource_data['resources_collected'])) if resource_data['resources_collected'] else 0,
            replay_data['match_data']['workers_killed'][i] - replay_data['match_data']['workers_lost'][i],
        ])

    return {
        'winner': replay['winner'],
        'file_path': str(path),
        'data': prediction_data,
    }


def handle_replay(path, player_names, identifiers):
    try:
        players, timeline, engagements, stats, metadata = parse_replay(path, local=True)
        if not players:
            return {}
    except Exception:
        return {}
    return generate_prediction_data(players, timeline, stats, metadata, path)


# required for multiprocessing
if __name__ == '__main__':
    path = Path().absolute() / 'tournament_replays'
    match_info = []
    predictions_completed = 0

    for item in path.iterdir():
        match_info_list = recursive_parse(
            sub_dir=item,
            data_function=None,
            multi=True,
        )

        results = []

        # Pool multiprocessing for better throughput of parsing
        with Pool(10) as p:
            # results = p.starmap(handle_replay, match_info_list)
            results = p.starmap(handle_replay, match_info_list)

        # if an error occurs, filter it out of the dataset
        match_info.extend(filter(lambda x: bool(x), results))
        predictions_completed += len(results)
        print(f'{predictions_completed} replays parsed so far')

    with open('prediction_data.json', 'w', encoding='utf-8') as prediction_data:
        json.dump({'prediction_data': match_info}, prediction_data, ensure_ascii=False, indent=4)
