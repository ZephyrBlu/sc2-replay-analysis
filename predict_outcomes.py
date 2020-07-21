import json
import joblib


def predict_match(model, prediction_data):
    predictions = {
        'file_path': prediction_data['file_path'],
        'winner': prediction_data['winner'],
        1: {},
        2: {},
    }

    from copy import deepcopy

    for i in range(0, 2):
        # remove avg_collection_rate value
        filtered_data = deepcopy(prediction_data['data'][i])
        filtered_data.pop(7)
        raw_prediction = model.predict([filtered_data]).tolist()[0]
        # raw_probability = model.predict_proba([filtered_data]).tolist()[0]
        raw_probability = (0, 0)

        predicted = (i + 1) if raw_prediction is True else prediction_data['winner']
        if predicted == (i + 1):
            probability = raw_probability[1]
        else:
            probability = raw_probability[0]

        predictions[i + 1] = {
            'predicted': predicted,
            'probability': probability,
            'raw': {
                'predicted': raw_prediction,
                'probability': raw_probability,
            },
        }

    return predictions


def predict_outcomes():
    with open('prediction_data.json', 'r') as prediction_data:
        data = json.load(prediction_data)['prediction_data']
        lr_model = joblib.load('predict_outcome_lr.joblib')
        rf_model = joblib.load('predict_outcome_rf.joblib')
        nb_model = joblib.load('predict_outcome_nb.joblib')
        svm_model = joblib.load('predict_outcome_svm.joblib')

        lr_predicted = []
        rf_predicted = []
        nb_predicted = []
        svm_predicted = []
        for match_data in data:
            lr_predicted.append(predict_match(lr_model, match_data))
            rf_predicted.append(predict_match(rf_model, match_data))
            nb_predicted.append(predict_match(nb_model, match_data))
            svm_predicted.append(predict_match(svm_model, match_data))

        print(f'{len(data)} replays')

        for predicted in [lr_predicted, rf_predicted, nb_predicted, svm_predicted]:
            matching = 0
            diverge = 0
            consensus = 0
            correct = 0
            incorrect = 0
            for match in predicted:
                for i in range(1, 3):
                    if match['winner'] == match[i]['predicted']:
                        correct += 1
                    else:
                        incorrect += 1

                if match[1]['predicted'] == match[2]['predicted']:
                    matching += 1
                    if match['winner'] == match[1]['predicted']:
                        consensus += 1
                else:
                    diverge += 1

            print(f'Overall Accuracy: {round(correct / (len(data) * 2), 3) * 100}% ({correct}/{len(data) * 2})')
            print(f'Match predictions agreed {round(matching / len(data), 3) * 100}% of the time')
            print(f'When match predictions agreed, they were right {round(consensus / matching, 3) * 100}% of the time\n')


predict_outcomes()
