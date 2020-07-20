from statistics import median
from datetime import datetime


def calc_summary_metrics(replay, timeline):
    game_metrics = [
        'resource_collection_rate_all',
        'total_army_value',
        'total_resources_lost',
    ]

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
        game_state['1'] = game_state[1]
        game_state['2'] = game_state[2]

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
            p1_val = game_state['1'][metric]
            p2_val = game_state['2'][metric]

            if p1_val == 0 and p2_val == 0:
                diff = (0, 0)
            else:
                if min(p1_val, p2_val) == 0:
                    percent_diff = 0
                else:
                    percent_diff = (
                        ((max(p1_val, p2_val) / min(p1_val, p2_val)) - 1)
                        * 1 if max(p1_val, p2_val) == p1_val else -1
                    )

                diff = (
                    p1_val - p2_val,
                    round(percent_diff, 3),
                )

            if p1_val > p2_val:
                summary_data[metric]['ahead'] += 1
                summary_data[metric]['amount_ahead'].append(diff)
            elif p1_val < p2_val:
                summary_data[metric]['behind'] += 1
                summary_data[metric]['amount_behind'].append(diff)
            summary_data[metric]['lead_lag'].append(diff)

    summary_metrics = {
        'time_to_mine': {
            1: round(median(summary_data['time_to_mine']['1']), 1),
            2: round(median(summary_data['time_to_mine']['2']), 1),
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


def process_data(replay, timeline):
    summary_metrics = calc_summary_metrics(replay, timeline)
    replay_info = {
        'players': {
            1: replay['players'][1],
            2: replay['players'][2],
        },
        'match_data': replay['match_data'],
        'match_length': replay['match_length'],
        'played_at': datetime.timestamp(replay['played_at']),
        'map': replay['map'],
        'winner': replay['winner'],
    }

    replay_info.update(summary_metrics)
    return replay_info
