__author__ = "Jakob Aungiers"
__copyright__ = "Jakob Aungiers 2018"
__version__ = "2.0.0"
__license__ = "MIT"

import os
import json
import time
import math
import matplotlib.pyplot as plt
import numpy as np
from core.data_processor import DataLoader
from core.model import Model


def plot_results(predicted_data, true_data):
    fig = plt.figure(facecolor='white')
    ax = fig.add_subplot(111)
    ax.plot(true_data, label='True Data')
    ax.grid(True)
    plt.plot(predicted_data, label='Prediction')
    #plt.ylim(min(true_data), max(true_data))
    plt.legend()
    plt.show()


def plot_results_multiple(predicted_data, true_data, prediction_len):
    fig = plt.figure(facecolor='white')
    ax = fig.add_subplot(111)
    ax.plot(true_data, label='True Data')
	# Pad the list of predictions to shift it in the graph to it's correct start
    for i, data in enumerate(predicted_data):
        padding = [None for p in range(i * prediction_len)]
        plt.plot(padding + data, label='Prediction')
        plt.legend()
    plt.show()


def main():
    configs = json.load(open('config.json', 'r'))
    if not os.path.exists(configs['model']['save_dir']): os.makedirs(configs['model']['save_dir'])

    data = DataLoader(
        os.path.join('data', configs['data']['filename']),
        configs['data']['train_test_split'],
        configs['data']['columns']
    )

    model = Model()
    model.build_model(configs)
    x, y = data.get_train_data(
        seq_len=configs['data']['sequence_length'],
        normalise=configs['data']['normalise']
    )

    '''
	# in-memory training
	model.train(
		x,
		y,
		epochs = configs['training']['epochs'],
		batch_size = configs['training']['batch_size'],
		save_dir = configs['model']['save_dir']
	)
	'''
    # out-of memory generative training




    steps_per_epoch = math.ceil((data.len_train - configs['data']['sequence_length']) / configs['training']['batch_size'])
    model.train_generator(
        data_gen=data.generate_train_batch(
            seq_len=configs['data']['sequence_length'],
            batch_size=configs['training']['batch_size'],
            normalise=configs['data']['normalise']
        ),
        epochs=configs['training']['epochs'],
        batch_size=configs['training']['batch_size'],
        steps_per_epoch=steps_per_epoch,
        save_dir=configs['model']['save_dir'],
        configs=configs
    )

    x_test, y_test, p0 = data.get_test_data(
        seq_len=configs['data']['sequence_length'],
        normalise=configs['data']['normalise']
    )

    # predictions = model.predict_sequences_multiple(x_test, configs['data']['sequence_length'], configs['data']['sequence_length'])
    # predictions = model.predict_sequence_full(x_test, configs['data']['sequence_length'])
    predictions = model.predict_point_by_point(x_test)
    y_test = np.reshape(np.copy(y_test), -1)

    plot_results((p0 * (predictions + 1))[-200:], (p0 * (y_test + 1))[-200:])
    measure_performance(predictions, y_test)


def measure_performance(predictions, y_trues):
    signals_predictions = list(np.diff(predictions))
    signals_trues = list(np.diff(y_trues))
    count = len(signals_predictions)

    bal_koiso = 0
    kin_beta = 0
    beche_de = 0

    for index in range(count):
        true = signals_trues[index]
        prediction = signals_predictions[index]
        if true > 0.0 and prediction > 0.0:
            kin_beta += 1
        elif true < 0.0 and prediction < 0.0:
            beche_de += 1
        else:
            bal_koiso += 1

    print(f'kin_beta={kin_beta}, beche_de={beche_de}, bal_koiso={bal_koiso}')
    print(f'signal_accuracy={(kin_beta+beche_de)/(bal_koiso+kin_beta+beche_de)}')



    # plot_results(predictions, y_test)


if __name__ == '__main__':
    main()