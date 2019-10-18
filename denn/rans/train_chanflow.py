import denn.channel_flow as chan
import numpy as np
import torch
import os
import argparse
import time
import rans_utils
torch.random.manual_seed(123)

HYPERS={
        'num_epochs': 10000,
        'sampling': 'perturb',
        'k': 0.41,
        'activation': 'swish'
       }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ChannelFlow command-line args')
    parser.add_argument('--disable-cuda', action='store_true',
                        help='Disables CUDA')
    parser.add_argument('--disable-status', action='store_true',
                        help='Disables tqdm status bar')
    parser.add_argument('--disable-save', action='store_true',
                        help='Whether or not to save objects from training')
    args = parser.parse_args()
    args.device = None
    if not args.disable_cuda and torch.cuda.is_available():
        args.device = torch.device('cuda')
    else:
        args.device = torch.device('cpu')


    model = chan.Chanflow().to(device=args.device)
    model.set_hyperparams(**HYPERS)
    hypers = model.hypers
    retau = rans_utils.calc_retau(hypers['delta'], hypers['dp_dx'], hypers['rho'], hypers['nu'])
    print('Training with Retau={}'.format(retau))
    run_dict = model.train(device=args.device, disable_status=args.disable_status, save_run=not args.disable_save)
