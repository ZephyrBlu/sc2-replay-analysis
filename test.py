from pathlib import Path
from zephyrus_sc2_parser import parse_replay

# players, timeline, engagements, summary, meta = parse_replay('test_pvt.SC2Replay', local=True)
# players, timeline, engagements, summary, meta = parse_replay('test_pvz.SC2Replay', local=True)

# replays_path = Path('army_replays/DH SC2 Masters Fall/Season Finals/Group Stage/Playoffs/3 Grand Finals/Reynor vs. Trap/')

# map_stats = {}
# map_pos = {}

# for path in replays_path.iterdir():
#     players, timeline, engagements, summary, meta = parse_replay(path, local=True)
#     # # print(players, summary, meta, '\n')
#     # print(engagements)

#     p1_name = players[1].name
#     p2_name = players[2].name
#     all_pos = {
#         p1_name: [],
#         p2_name: [],
#     }
#     avg_pos = {
#         p1_name: None,
#         p2_name: None,
#     }

#     # print(players[1].name)
#     for pos, dist, coord, res, gameloop in players[1].army_positions:
#         if res >= 2000:
#             # print(round(pos, 3), round(dist, 1), (coord['x'], coord['y']), res, round(gameloop / 22.4 / 60, 2))
#             all_pos[p1_name].append(pos)

#     # print('\n')
#     # print(players[2].name)
#     for pos, dist, coord, res, gameloop in players[2].army_positions:
#         if res >= 2000:
#             # print(round(pos, 3), round(dist, 1), (coord['x'], coord['y']), res, round(gameloop / 22.4 / 60, 2))
#             all_pos[p2_name].append(pos)

#     # print(round(sum(all_pos[1]) / len(all_pos[1]), 3), round(sum(all_pos[2]) / len(all_pos[2]), 3))

#     if len(all_pos[p1_name]) == 0:
#         avg_pos[p1_name] = 0
#     else:
#         avg_pos[p1_name] = round(sum(all_pos[p1_name]) / len(all_pos[p1_name]), 3)

#     if len(all_pos[p2_name]) == 0:
#         avg_pos[p2_name] = 0
#     else:
#         avg_pos[p2_name] = round(sum(all_pos[p2_name]) / len(all_pos[p2_name]), 3)

#     map_pos[meta['map']] = all_pos
#     map_stats[meta['map']] = avg_pos

# for m, pos in map_pos.items():
#     print(m, pos)

# print('\n')
# overall_avg = {}
# for m, stat in map_stats.items():
#     print(m, stat)
#     for p, v in stat.items():
#         if p not in overall_avg:
#             overall_avg[p] = []
#         overall_avg[p].append(v)

# print('\n')
# import numpy as np
# player_hists = {}
# all_pos = {}
# for m, stat in map_pos.items():
#     for p, v in stat.items():
#         if p not in all_pos:
#             all_pos[p] = []
#         all_pos[p].extend(v)

# for p, v in all_pos.items():
#     p_hist = np.histogram(v, bins=5, range=(0, 1), density=False)
#     player_hists[p] = p_hist
#     print(p, sum(v), len(v), sum(v) / len(v))

# print('\n')
# print(player_hists)

# players, timeline, engagements, summary, meta = parse_replay('army_replays/DH SC2 Masters Fall/Season Finals/Group Stage/Playoffs/3 Grand Finals/Reynor vs. Trap/Golden Wall.SC2Replay', local=True)
# # # print(players, summary, meta, '\n')
# # print(engagements)

# all_pos = {
#     1: [],
#     2: [],
# }

# print(players[1].name)
# for pos, dist, coord, res, gameloop in players[1].army_positions:
#     if res >= 1500:
#         print(round(pos, 3), round(dist, 1), (coord['x'], coord['y']), res, round(gameloop / 22.4 / 60, 2))
#         all_pos[1].append(pos)

# print('\n')
# print(players[2].name)
# for pos, dist, coord, res, gameloop in players[2].army_positions:
#     if res >= 1500:
#         print(round(pos, 3), round(dist, 1), (coord['x'], coord['y']), res, round(gameloop / 22.4 / 60, 2))
#         all_pos[2].append(pos)

# print(round(sum(all_pos[1]) / len(all_pos[1]), 3), round(sum(all_pos[2]) / len(all_pos[2]), 3))


import math
from pathlib import Path, PurePath
from sc2_tournament_analysis import recursive_parse
from multiprocessing import Pool
from fuzzywuzzy import fuzz
from zephyrus_sc2_parser import parse_replay
from sc2_tournament_analysis.defaults import (
    standard_ignore_units, standard_merge_units, standard_player_match
)
import logging
import traceback


"""
data schema:

GameID: uuid
Map: str
Duration: float (minutes)
PlayerName: str
IsWinner: bool
Race: str ('Protoss', 'Terran', 'Zerg')
UnitName: str
BirthTime: float (minutes)
DeathTime: float (minutes)
"""


def parse_data(players, timeline, engagements, stats, metadata, **kwargs):
    """
    Data function for each replay that is parsed

    All replay data is passed into this function and can be manipulated at will
    """

    # regex patterns for parsing dir names
    name_id_matches = kwargs['name_id_matches']
    # if players[1].army_positions:
    #     avg_p1_army = sum(map(lambda x: x[0], players[1].army_positions)) / len(players[1].army_positions)
    # else:
    #     avg_p1_army = None

    # if players[2].army_positions:
    #     avg_p2_army = sum(map(lambda x: x[0], players[2].army_positions)) / len(players[2].army_positions)
    # else:
    #     avg_p2_army = None

    if name_id_matches:
        army_data = {
            name_id_matches[1]: players[1].army_positions,
            name_id_matches[2]: players[2].army_positions,
        }
    else:
        army_data = {
            players[1].name: players[1].army_positions,
            players[2].name: players[2].army_positions,
        }

    # army_data = {
    #     1: players[1].army_positions,
    #     2: players[2].army_positions,
    # }
    return {
        1: players[1],
        2: players[2],
        'winner': metadata['winner'],
        'matchup': 'v'.join(sorted([players[1].race[0], players[2].race[0]])),
        'match_length': metadata['game_length'],
        'max_collection_rate': stats['max_collection_rate'],
        'engagements': engagements,
        'army_data': army_data,
    }


def handle_replay(path, player_names, identifiers):
    """
    Handles assigning player names to in-game names before data processing
    """
    logging.basicConfig(filename='errors.log', level=logging.DEBUG)

    try:
        players, timeline, engagements, stats, metadata = parse_replay(
            path, local=True
        )
    except Exception:
        print(f'An error occurred in {path}: {traceback.format_exc()}')
        logging.error(path, traceback.format_exc())
        return

    if not players:
        return None

    player_match = standard_player_match
    for name, value in identifiers:
        if name == 'event' and (value == 'Nation Wars' or value == 'Cheeseadelphia'):
            player_match = False

    if player_match and player_names:
        match_ratios = []
        for p_id, p in players.items():
            # partial_ratio fuzzy matches substrings instead of an exact match
            current_match_ratio = fuzz.partial_ratio(p.name, player_names[0])
            match_ratios.append((p.player_id, p.name, current_match_ratio))

        name_match = max(match_ratios, key=lambda x: x[2])

        # linking matched names to in game names
        name_id_matches = {
            name_match[0]: player_names[0]
        }

        if name_match[0] == 1:
            name_id_matches[2] = player_names[1]
        else:
            name_id_matches[1] = player_names[1]
    else:
        name_id_matches = {}

    match_info = parse_data(
        players,
        timeline,
        engagements,
        stats,
        metadata,
        name_id_matches=name_id_matches,
        identifiers=identifiers,
        ignore_units=standard_ignore_units,
        merge_units=standard_merge_units,
    )
    return match_info

# regex patterns for each event
event_patterns = {
    'ASUS ROG': [
        ('event', 'ASUS ROG'),
        ('stage', 'Group Stage \\w{1}(?: *$)'),
        ('group', '(?<=Group )\\w{1}(?: *$)'),
    ],
    'Blizzcon': [
        ('event', 'Blizzcon'),
        ('stage', '[r,R][o,O]\\d|Final|Semifinal'),
    ],
    'Cheeseadelphia': [
        ('event', 'Cheeseadelphia'),
    ],
    'HSC XX': [
        ('event', 'HSC XX'),
        ('group', '(?<=Group )\\w{1}(?: *$)'),
    ],
    'Nation Wars': [
        ('event', 'Nation Wars'),
    ],
    'QLASH Invitational': [
        ('event', 'QLASH Invitational'),
    ],
    'WCS Fall': [
        ('event', 'WCS Fall'),
        ('stage', 'Knockout|Group Stage \\w{1}(?: *$)|[r,R][o,O]\\d|Final'),
        ('group', '(?<=Group )\\w{1}(?: *$)'),
    ],
    'DH SC2 Masters Summer': [],
    'DH SC2 Masters Fall': [],
    'TSL 5': [],
    'Stay at HSC': [],
    'Stay at HSC #2': [],
}


# required for multiprocessing
if __name__ == '__main__':
    path = Path().absolute() / 'army_replays/DH SC2 Masters Fall'
    all_data = []
    army_positions = {}

    for item in path.iterdir():
        item_name = PurePath(item).name
        print(f'In {item_name} directory')

        # no player match for Nation Wars and Cheeseadelphia
        if item_name == 'Nation Wars' or item_name == 'Cheeseadelphia':
            match_info_list = recursive_parse(
                sub_dir=item,
                player_match=False,
                data_function=parse_data,
                # identifier_rules=event_patterns[item_name],
                multi=True,
            )
        else:
            match_info_list = recursive_parse(
                sub_dir=item,
                data_function=parse_data,
                # identifier_rules=event_patterns[item_name],
                multi=True,
            )

        results = []
        print(f'Parsing replays from {item_name}')

        # Pool multiprocessing for better throughput of parsing
        with Pool(10) as p:
            results = p.starmap(handle_replay, match_info_list)

        all_data.extend(results)
        print(f'Replays from {item_name} parsed successfully')

    import csv
    from statistics import median

    # game stage: early, mid, late
    # army value: 500, 1500, 2500
    # collection rate: <1776 + 300 (2076), >=1776 + 300 (2076), >=2664 + 300 (2964)
    # workers: <44 + 4 (48), >=44 + 4 (48), >=66 + 4 (70)

    def check_match_stage(max_collection_rates):
        if max_collection_rates[1] >= 2964 and max_collection_rates[2] >= 2964:
            return 'late'
        elif max_collection_rates[1] >= 2076 and max_collection_rates[2] >= 2076:
            return 'mid'
        return 'early'

    # army_data = [(
    #     'name',
    #     'race',
    #     'matchup',
    #     'relative_position',
    #     'army_x',
    #     'army_y',
    #     'total_army_value',
    #     'died_army_value',
    #     'gameloop',
    # )]

    engagement_data = []
    match_length_games = [('outcome', 'seconds')]
    collection_rate_games = [('outcome', 'race', 'collection_rate')]
    match_stage_games = {
        'early': {
            'wins': 0,
            'losses': 0,
        },
        'mid': {
            'wins': 0,
            'losses': 0,
        },
        'late': {
            'wins': 0,
            'losses': 0,
        },
    }
    min_engagement_resources = {
        'early': 500,
        'mid': 2000,
        'late': 4000,
    }

    for match_data in all_data:
        if not match_data or match_data['matchup'] != 'TvZ':
            continue

        match_stage = check_match_stage(match_data['max_collection_rate'])

        if match_data[match_data['winner']].race == 'Protoss':
            match_stage_games[match_stage]['wins'] += 1
            match_length_games.append(('win', match_data['match_length']))
        else:
            match_stage_games[match_stage]['losses'] += 1
            match_length_games.append(('loss', match_data['match_length']))

        opp_id = 1 if match_data['winner'] == 2 else 2
        collection_rate_games.append((
            'win',
            match_data[match_data['winner']].race,
            match_data['max_collection_rate'][match_data['winner']],
        ))
        collection_rate_games.append((
            'loss',
            match_data[opp_id].race,
            match_data['max_collection_rate'][opp_id],
        ))

        for engagement in match_data['engagements']:
            current_stage = check_match_stage({
                1: engagement[1]['total_collection_rate'],
                2: engagement[2]['total_collection_rate'],
            })

            p1_total_army_value = engagement[1]['army_value']['live'] + engagement[1]['army_value']['died']
            p2_total_army_value = engagement[2]['army_value']['live'] + engagement[2]['army_value']['died']
            print(p1_total_army_value, min_engagement_resources[current_stage])
            print(p2_total_army_value, min_engagement_resources[current_stage])
            # if either player's army doesn't meet required minimum resources, skip the engagement
            if (
                p1_total_army_value < min_engagement_resources[current_stage]
                or p2_total_army_value < min_engagement_resources[current_stage]
                or not engagement[1]['relative_position']
                or not engagement[2]['relative_position']
            ):
                continue

            engagement_info = {
                'gameloop': engagement['gameloop'],
                'matchup': match_data['matchup'],
                'match_stage': match_stage,
                'current_stage': current_stage,
                1: {
                    'name': match_data[1].name,
                    'race': match_data[1].race,
                    'relative_position': engagement[1]['relative_position'],
                    'army_position': engagement[1]['army_position'],
                    'total_army_value': engagement[1]['army_value']['live'] + engagement[1]['army_value']['died'],
                    'army_value_died': engagement[1]['army_value']['died'],
                },
                2: {
                    'name': match_data[2].name,
                    'race': match_data[2].race,
                    'relative_position': engagement[2]['relative_position'],
                    'army_position': engagement[2]['army_position'],
                    'total_army_value': engagement[2]['army_value']['live'] + engagement[2]['army_value']['died'],
                    'army_value_died': engagement[2]['army_value']['died'],
                },
            }
            engagement_data.append(engagement_info)

    with open('match_length_outcomes.csv', 'w', encoding='utf-8') as match_length_output:
        writer = csv.writer(match_length_output, lineterminator='\n')
        writer.writerows(match_length_games)

    with open('collection_rate_outcomes.csv', 'w', encoding='utf-8') as collection_rate_output:
        writer = csv.writer(collection_rate_output, lineterminator='\n')
        writer.writerows(collection_rate_games)

    current_stage_relative_positions = {
        'early': [],
        'mid': [],
        'late': [],
    }
    for engagement in engagement_data:
        protoss_player_id = 1 if engagement[1]['race'] == 'Protoss' else 2
        current_stage_relative_positions[engagement['current_stage']].append((
            engagement[protoss_player_id]['relative_position'],
            engagement[protoss_player_id]['total_army_value'],
            engagement['gameloop'],
        ))

    engagement_positions = [('relative_position', 'army_value', 'current_stage', 'gameloop')]
    for stage, positions in current_stage_relative_positions.items():
        for pos, army_value, gameloop in positions:
            engagement_positions.append((pos, army_value, stage, gameloop))
        print(stage, positions)
        print('')
    print('\n')

    with open('engagement_positions.csv', 'w', encoding='utf-8') as engagement_output:
        writer = csv.writer(engagement_output, lineterminator='\n')
        writer.writerows(engagement_positions)

    for stage, positions in current_stage_relative_positions.items():
        print(stage, median(map(lambda x: x[0], positions)))

    print('\n')
    print(match_stage_games)

    #         army_data.append(p1_engagement)
    #         army_data.append(p2_engagement)

    # with open('army_data_dh_masters.csv', 'w', encoding='utf-8') as army_output:
    #     writer = csv.writer(army_output, lineterminator='\n')
    #     writer.writerows(army_data)
