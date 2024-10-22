import hydra
from hydra.utils import instantiate
from omegaconf import DictConfig, OmegaConf

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import lightning as L
from lightning.pytorch.callbacks import EarlyStopping, Timer
from torch.utils.data import DataLoader, SubsetRandomSampler
from sklearn.model_selection import KFold
from lightning.pytorch.loggers import MLFlowLogger


import numpy as np
from tqdm import tqdm
import time
import mlflow

from ultk.util.io import read_grammatical_expressions

from ..quantifier import QuantifierModel
from ultk.language.grammar import GrammaticalExpression
from ..util import read_expressions
from ..grammar import quantifiers_grammar
from ..training import QuantifierDataset, train_loop, MV_LSTM, set_device
from ..training_lightning import LightningModel
import torch.nn as nn

# Weight initialization function (Xavier initialization)
def init_weights(m):
    if isinstance(m, nn.Linear):
        nn.init.xavier_uniform_(m.weight)
        if m.bias is not None:
            nn.init.zeros_(m.bias)

def train(cfg: DictConfig, expression: GrammaticalExpression, dataset: Dataset, train_dataloader: DataLoader, validation_dataloader: DataLoader, mlf_logger: MLFlowLogger):
    if cfg.training.lightning:
        train_lightning(cfg, expression, dataset, train_dataloader, validation_dataloader, mlf_logger)
    else:
        train_base_pytorch(cfg, expression, dataset, train_dataloader, validation_dataloader)

def train_lightning(cfg: DictConfig, expression: GrammaticalExpression, dataset: Dataset, train_dataloader: DataLoader, validation_dataloader: DataLoader, mlf_logger: MLFlowLogger):

    n_features = dataset[0][0].shape[1] # this is number of parallel inputs
    n_timesteps = dataset[0][0].shape[0] # this is number of timesteps

    selected_model = instantiate(cfg.model)
    selected_optimizer = instantiate(cfg.optimizer)

    model = selected_model(device=cfg.training.device)
    print(model)
    
    optimizer = selected_optimizer(model.parameters())
    lightning = LightningModel(model, criterion=instantiate(cfg.criterion), optimizer=optimizer)
    timer_callback = Timer()
    trainer = L.Trainer(max_epochs=cfg.training.epochs, 
                        accelerator=cfg.training.device,
                        val_check_interval=1,
                        logger=mlf_logger,
                        callbacks=[timer_callback, 
                        EarlyStopping(monitor=cfg.training.early_stopping.monitor, 
                                    patience=cfg.training.early_stopping.patience, 
                                    min_delta=cfg.training.early_stopping.min_delta, 
                                    mode=cfg.training.early_stopping.mode, 
                                    check_on_train_epoch_end=cfg.training.early_stopping.check_on_train_epoch_end, # Check at the step level, not at the epoch level
                                    )]) 
    trainer.fit(lightning, train_dataloader, validation_dataloader)
    total_time = timer_callback.time_elapsed("train")
    print(f"Total training time: {total_time:.2f} seconds")
    print(trainer.callback_metrics)
    print("_______")

def train_base_pytorch(cfg: DictConfig, expression: GrammaticalExpression, dataset: Dataset, train_dataloader: DataLoader, validation_dataloader: DataLoader):
    
    n_features = dataset[0][0].shape[1] # this is number of parallel inputs
    n_timesteps = dataset[0][0].shape[0] # this is number of timesteps

    selected_model = instantiate(cfg.model)
    selected_optimizer = instantiate(cfg.optimizer)

    model = selected_model(device=cfg.training.device)
    print(model)
    criterion = instantiate(cfg.criterion)
    optimizer = selected_optimizer(model.parameters())

    start = time.time()
    train_loop(train_dataloader, model, criterion, optimizer, cfg.training.epochs, conditions=cfg.training.conditions)
    end = time.time()
    print("Training time: ", end-start)
    model.eval()

    # Disable gradient computation and reduce memory consumption.
    with torch.no_grad():
        running_vloss = 0.0
        for i, vdata in enumerate(validation_dataloader):
            v_inputs, v_targets = vdata
            if isinstance(model, MV_LSTM):
                model.init_hidden(v_inputs.size(0))
            v_outputs = model(v_inputs)
            vloss = criterion(v_outputs, v_targets)
            running_vloss += vloss
    print("Validation loss: ", running_vloss.item())

@hydra.main(version_base=None, config_path="../conf", config_name="learn")
def main(cfg: DictConfig) -> None:

    mlflow.pytorch.autolog()

    print(OmegaConf.to_yaml(cfg))

    quantifiers_grammar.add_indices_as_primitives(4)
    expressions_path = cfg.expressions.output_dir + "X" + str(cfg.expressions.x_size) + "/M" + str(cfg.expressions.m_size) + "/d" + str(cfg.expressions.depth) + "/" + "generated_expressions.yml"
    print("Reading expressions from: ", expressions_path)
    expressions, _ = read_grammatical_expressions(expressions_path, quantifiers_grammar)


    device = set_device(cfg.training.device)

    for expression in tqdm(expressions[1:1+cfg.expressions.n_limit]):

        run_name = f'{expression.rule_name}'
        print("Running experiment: ", run_name)

        with mlflow.start_run(log_system_metrics=True, run_name=run_name) as mainrun:
            mlflow.log_params(cfg)
            mlflow.set_tag("Notes", cfg.notes)
            mlf_logger = MLFlowLogger(experiment_name="learn_quantifiers", 
                                    log_model=True,
                                    tracking_uri="http://127.0.0.1:5000",
                                    run_id=mainrun.info.run_id)

            print("Expression: ", expression.rule_name)
            if cfg.expressions.generation_args:
                print("Using generation args: ", cfg.expressions.generation_args)
                dataset = QuantifierDataset(expression, representation=cfg.expressions.representation, downsampling=cfg.expressions.downsampling, generation_args=cfg.expressions.generation_args)
            else:
                print("No generation args provided")
                dataset = QuantifierDataset(expression, representation=cfg.expressions.representation, downsampling=cfg.expressions.downsampling)
            dataset.inputs = dataset.inputs.to(device)
            dataset.targets = dataset.targets.to(device)

            if cfg.training.strategy == "kfold":

                kfold = KFold(n_splits=cfg.training.k_splits, shuffle=True)
                print("Running k-fold training with {} splits".format(cfg.training.k_splits))
                for fold, (train_ids, valid_ids) in enumerate(kfold.split(dataset)):
                    
                    with mlflow.start_run(run_name=f"{fold}", nested=True) as childrun:

                        print(f'FOLD {fold}')
                        print('--------------------------------')
                        train_subsampler = SubsetRandomSampler(train_ids)
                        valid_subsampler = SubsetRandomSampler(valid_ids)
                        
                        train_dataloader = DataLoader(dataset, batch_size=cfg.expressions.batch_size, sampler=train_subsampler)
                        validation_dataloader = DataLoader(dataset, batch_size=cfg.expressions.batch_size, sampler=valid_subsampler)

                        print("Training set size: ", len(train_dataloader)*cfg.expressions.batch_size)
                        print("Validation set size: ", len(validation_dataloader)*cfg.expressions.batch_size)

                        train(cfg, expression, dataset, train_dataloader, validation_dataloader, mlf_logger)

            elif cfg.training.strategy == "multirun":
            
                for i in range(cfg.training.n_runs):

                    with mlflow.start_run(run_name=f"{i}", nested=True) as childrun:

                        print(f'RUN {i}')
                        print('--------------------------------')
                        train_data, validation_data = torch.utils.data.random_split(dataset, [cfg.expressions.split, 1-cfg.expressions.split])

                        train_dataloader = DataLoader(train_data, batch_size=cfg.expressions.batch_size, shuffle=True)
                        validation_dataloader = DataLoader(validation_data, batch_size=cfg.expressions.batch_size, shuffle=True)

                        print("Training set size: ", len(train_dataloader))
                        print("Validation set size: ", len(validation_dataloader))
                        
                        train(cfg, expression, dataset, train_dataloader, validation_dataloader)

if __name__ == "__main__":
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment(f"learn_quantifiers")
    main()