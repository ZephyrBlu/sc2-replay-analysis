import json
import joblib


def predict_match(model, prediction_data):
    predictions = {
        'file_path': prediction_data['file_path'],
        'winner': prediction_data['winner'],
        1: {},
        2: {},
    }

    for i in range(0, 2):
        raw_prediction = model.predict([prediction_data['data'][i]]).tolist()[0]
        raw_probability = model.predict_proba([prediction_data['data'][i]]).tolist()[0]

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
        model = joblib.load('predict_outcome.joblib')

        predicted = []
        for match_data in data:
            predicted.append(predict_match(model, match_data))

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
        print(f'When match predictions agreed, they were right {round(consensus / matching, 3) * 100}% of the time')


predict_outcomes()
