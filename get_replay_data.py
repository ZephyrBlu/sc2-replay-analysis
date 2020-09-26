import time
import json
from statistics import median
from datetime import datetime
from apps.user_profile.models import Replay

# script for fetching and parsing replay data directly from zephyrus.gg database


def calc_summary_metrics(replay, timeline):
    game_metrics = [
        'resource_collection_rate_all',
        'total_army_value',
        'total_resources_lost',
    ]

    user_player = replay.user_match_id
    opp_player = 1 if user_player == 2 else 2

    summary_data = {'time_to_mine': {'1': [], '2': []}}
    for metric in game_metrics:
        summary_data[metric] = {
            'ahead': 0,
            'behind': 0,
            'amount_ahead': [],
            'amount_behind': [],
            'lead_lag': [],
        }

    for game_state in timeline:
        total_unspent_resources = {
            '1': game_state['1']['unspent_resources']['minerals'] + game_state['1']['unspent_resources']['gas'],
            '2': game_state['2']['unspent_resources']['minerals'] + game_state['2']['unspent_resources']['gas'],
        }

        resource_collection_rate_second = {
            '1': game_state['1']['resource_collection_rate_all'] / 60,
            '2': game_state['2']['resource_collection_rate_all'] / 60,
        }

        # divide by 60 since collection rate is per minute
        summary_data['time_to_mine']['1'].append((total_unspent_resources['1'] / resource_collection_rate_second['1']) if resource_collection_rate_second['1'] else 0)
        summary_data['time_to_mine']['2'].append((total_unspent_resources['2'] / resource_collection_rate_second['2']) if resource_collection_rate_second['2'] else 0)

        for metric in game_metrics:
            user_val = game_state[str(user_player)][metric]
            opp_val = game_state[str(opp_player)][metric]

            if user_val == 0 and opp_val == 0:
                diff = (0, 0)
            else:
                if min(user_val, opp_val) == 0:
                    percent_diff = 0
                else:
                    percent_diff = (
                        ((max(user_val, opp_val) / min(user_val, opp_val)) - 1)
                        * 1 if max(user_val, opp_val) == user_val else -1
                    )

                diff = (
                    user_val - opp_val,
                    round(percent_diff, 3),
                )

            if user_val > opp_val:
                summary_data[metric]['ahead'] += 1
                summary_data[metric]['amount_ahead'].append(diff)
            elif user_val < opp_val:
                summary_data[metric]['behind'] += 1
                summary_data[metric]['amount_behind'].append(diff)
            summary_data[metric]['lead_lag'].append(diff)

    summary_metrics = {
        'time_to_mine': {
            '1': round(median(summary_data['time_to_mine']['1']), 1),
            '2': round(median(summary_data['time_to_mine']['2']), 1),
        },
    }

    for metric, values in summary_data.items():
        if metric in game_metrics:
            summary_metrics[metric] = {
                'ahead': round(values['ahead'] / len(timeline), 3),
                'behind': round(values['behind'] / len(timeline), 3),
                'amount_ahead': (
                    0 if not values['amount_ahead'] else median(list(zip(*values['amount_ahead']))[0]),
                    0 if not values['amount_ahead'] else median(list(zip(*values['amount_ahead']))[1]),
                ),
                'amount_behind': (
                    0 if not values['amount_behind'] else median(list(zip(*values['amount_behind']))[0]),
                    0 if not values['amount_behind'] else median(list(zip(*values['amount_behind']))[1]),
                ),
                'lead_lag': (
                    0 if not values['lead_lag'] else median(list(zip(*values['lead_lag']))[0]),
                    0 if not values['lead_lag'] else median(list(zip(*values['lead_lag']))[1]),
                ),
            }

    return summary_metrics


start = time.time()
replays = Replay.objects.all()
print(f'Got {len(replays)} replays')
replay_data = []
missing_timelines = 0
missing_match_id = 0

for count, r in enumerate(replays):
    if not r.user_match_id:
        missing_match_id += 1
        continue

    try:
        with open(f'C:/Users/Luke/Desktop/Replay Data Analysis/timelines/{r.file_hash}.json.gz', 'r') as replay_timeline:
            print(f'Opening timeline file {count + 1}')
            summary_metrics = calc_summary_metrics(r, json.load(replay_timeline)['timeline'])

            replay_info = {
                'file_hash': r.file_hash,
                'user_match_id': r.user_match_id,
                'players': {
                    1: r.players['1'],
                    2: r.players['2'],
                },
                'match_data': r.match_data,
                'match_length': r.match_length,
                'played_at': datetime.timestamp(r.played_at),
                'map': r.map,
                'win': r.win,
            }
            replay_info.update(summary_metrics)
            replay_data.append(replay_info)
    except FileNotFoundError:
        missing_timelines += 1

with open('C:/Users/Luke/Desktop/Replay Data Analysis/replay_data.json', 'w', encoding='utf-8') as replay_summary:
    json.dump({'data': replay_data}, replay_summary, ensure_ascii=False, indent=4)

end = time.time()
print(f'Replays Processed: {len(replay_data)}/{len(replays)} ({round((len(replay_data) / len(replays)), 3) * 100}%)')
print(f'Missing User Match ID: {missing_match_id}/{len(replays)} ({round((missing_match_id / len(replays)), 3) * 100}%)')
print(f'Missing Timelines: {missing_timelines}/{len(replays)} ({round((missing_timelines / len(replays)), 3) * 100}%)')
print(f'Finished in {round(end - start, 1)} seconds')
