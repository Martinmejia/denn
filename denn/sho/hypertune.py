import pandas as pd
import multiprocessing as mp
import numpy as np
import argparse

from denn.experiments import gan_experiment, L2_experiment
import denn.config as cfg
from denn.utils import handle_overwrite, dict_product

_N_REPS = 20

def gan_exp_with_seed(i, q, gen_kwargs, disc_kwargs, gan_kwargs):
    res = gan_experiment(
        problem = cfg.sho_problem,
        seed = i,
        gen_kwargs = gen_kwargs,
        disc_kwargs = disc_kwargs,
        train_kwargs = gan_kwargs,
    )
    q.put(res['final_mse'])

def gan_exp_with_hypers(hypers):
    """
    take hypers dict and map values onto appropriate kwargs dict
    to run gan_experiment
    """
    disc_kwargs = cfg.disc_kwargs
    gan_kwargs = cfg.gan_kwargs
    gen_kwargs = cfg.gen_kwargs

    gan_kwargs['plot'] = False # ensure plotting is off

    for k, v in hypers.items():
        if k.startswith('gan_'):
            gan_kwargs[k.replace('gan_', '')] = v
        elif k.startswith('gen_'):
            gen_kwargs[k.replace('gen_', '')] = v
        elif k.startswith('disc_'):
            disc_kwargs[k.replace('disc_', '')] = v

    # reps=[]
    # for i in range(_N_REPS):
    #     exp_res = gan_experiment(
    #         problem = cfg.sho_problem,
    #         seed = i,
    #         gen_kwargs = gen_kwargs,
    #         disc_kwargs = disc_kwargs,
    #         train_kwargs = gan_kwargs,
    #     )
    #     reps.append(exp_res['final_mse'])

    # def map_fn(i):
    #     return gan_experiment(
    #         problem = cfg.sho_problem,
    #         seed = i,
    #         gen_kwargs = gen_kwargs,
    #         disc_kwargs = disc_kwargs,
    #         train_kwargs = gan_kwargs,
    #     )

    # map_fn = lambda i: gan_experiment(
    #     problem = cfg.sho_problem,
    #     seed = i,
    #     gen_kwargs = gen_kwargs,
    #     disc_kwargs = disc_kwargs,
    #     train_kwargs = gan_kwargs,
    # )
    
    # pool = mp.Pool(_N_REPS)
    # reps = pool.map(gan_exp_with_seed, list(range(_N_REPS)))

    q = mp.Queue()

    procs = []
    for i in range(_N_REPS):
        p = mp.Process(target=gan_exp_with_seed, args=(i, q, gen_kwargs, disc_kwargs, gan_kwargs))
        p.start()
        procs.append(p)

    for p in procs:
        p.join()   

    reps = []
    while not q.empty():
        reps.append(q.get())

    res = {'mse': reps, 'hypers': hypers}
    print(f'Result: {res}')
    return res

def L2_exp_with_seed(i, q, model_kwargs, train_kwargs):
    res = L2_experiment(
        problem = cfg.sho_problem,
        seed = i,
        model_kwargs = model_kwargs,
        train_kwargs = train_kwargs,
    )
    q.put(res['final_mse'])

def L2_exp_with_hypers(hypers):
    """
    take hypers dict and map values onto appropriate kwargs dict
    to run gan_experiment
    """
    model_kwargs = cfg.L2_mlp_kwargs
    train_kwargs = cfg.L2_kwargs

    train_kwargs['plot'] = False # ensure plotting is off

    for k, v in hypers.items():
        if k.startswith('model_'):
            model_kwargs[k.replace('model_', '')] = v
        elif k.startswith('train_'):
            train_kwargs[k.replace('train_', '')] = v

    # reps = []
    # for i in range(_N_REPS):
    #     exp_res = L2_experiment(
    #         problem = cfg.sho_problem,
    #         seed = i,
    #         model_kwargs = model_kwargs,
    #         train_kwargs = train_kwargs,
    #     )
    #     reps.append(exp_res['final_mse'])
 
    # map_fn = lambda i: L2_experiment(
    #     problem = cfg.sho_problem,
    #     seed = i,
    #     model_kwargs = model_kwargs,
    #     train_kwargs = train_kwargs,
    # )

    # pool = mp.Pool(_N_REPS)
    # reps = pool.map(map_fn, list(range(_N_REPS)))

    q = mp.Queue()

    procs = []
    for i in range(_N_REPS):
        p = mp.Process(target=L2_exp_with_seed, args=(i, q, model_kwargs, train_kwargs))
        p.start()
        procs.append(p)

    for p in procs:
        p.join()

    reps = []
    while not q.empty():
        reps.append(q.get())

    res = {'mse': reps, 'hypers': hypers}
    print(f'Result: {res}')
    return res

if __name__== "__main__":
    args = argparse.ArgumentParser()
    args.add_argument('--gan', action='store_true', default=False,
        help='whether to use GAN-based training, default False (use L2-based)')
    args.add_argument('--ncpu', type=int, default=4,
        help='number of cpus to use (default: 4)')
    args.add_argument('--fname', type=str, default='SHO_hypertune.csv',
        help='path to save results of replications')
    args = args.parse_args()

    handle_overwrite(args.fname)

    hyper_space = cfg.gan_sho_hyper_space if args.gan else cfg.L2_sho_hyper_space
    hyper_space = dict_product(hyper_space)

    # pool = mp.Pool(args.ncpu)
    if args.gan:
        results = map(gan_exp_with_hypers, hyper_space)
    #     results = pool.map(gan_exp_with_hypers, hyper_space)
    else:
        results = map(L2_exp_with_hypers, hyper_space)
    #     results = pool.map(L2_exp_with_hypers, hyper_space)

    pd.DataFrame().from_records(results).to_csv(args.fname)
    print(f'Saved results to {args.fname}')
