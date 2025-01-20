import hydra
from hydra.utils import instantiate
from omegaconf import DictConfig, OmegaConf

import torch
from torch.utils.data import Dataset, DataLoader
import lightning as L
from lightning.pytorch.callbacks import Timer, EarlyStopping
from torch.utils.data import DataLoader, SubsetRandomSampler
from sklearn.model_selection import KFold
from lightning.pytorch.loggers import MLFlowLogger
import os

import numpy as np
from tqdm import tqdm
import time
import mlflow

from ultk.util.io import read_grammatical_expressions
from ultk.language.grammar import GrammaticalExpression
from ..grammar import add_indices
from ..util import calculate_term_expression_depth
from ..sampling import DatasetInitializationError
from ..training import QuantifierDataset, train_loop, MV_LSTM, set_device
from ..training_lightning import LightningModel, ThresholdEarlyStopping
from ..monotonicity import (
    load_grammar,
    get_verified_models,
    load_universe,
    filter_universe,
    filter_universe,
    measure_monotonicity,
    upward_monotonicity_entropy,
)
import random
from collections.abc import MutableMapping

# HYDRA_FULL_ERROR=1 python -m learn_quant.scripts.learn_quantifiers training.lightning=true training.strategy=multirun training.device=cpu model=mvlstm grammar.indices=false


def flatten(dictionary, parent_key="", separator="_"):
    items = []
    for key, value in dictionary.items():
        new_key = parent_key + separator + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(flatten(value, new_key, separator=separator).items())
        else:
            items.append((new_key, value))
    return dict(items)


def set_and_log_seeds(mainrun=False):
    # Set the seeds
    seed = random.randint(0, 999999)

    # Log the seed in MLFlow
    if mainrun:
        mlflow.log_param("mainrun_seed", seed)
    else:
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        mlflow.log_param("childrun_seed", seed)


# Weight initialization function (Xavier initialization)
"""
def init_weights(m):
    if isinstance(m, nn.Linear):
        nn.init.xavier_uniform_(m.weight)
        if m.bias is not None:
            nn.init.zeros_(m.bias)
"""


def train(
    cfg: DictConfig,
    expression: GrammaticalExpression,
    dataset: Dataset,
    train_dataloader: DataLoader,
    validation_dataloader: DataLoader,
    mlf_logger: MLFlowLogger,
):
    if cfg.training.lightning:
        train_lightning(
            cfg,
            expression,
            dataset,
            train_dataloader,
            validation_dataloader,
            mlf_logger,
        )
    else:
        train_base_pytorch(
            cfg, expression, dataset, train_dataloader, validation_dataloader
        )


def train_lightning(
    cfg: DictConfig,
    expression: GrammaticalExpression,
    dataset: Dataset,
    train_dataloader: DataLoader,
    validation_dataloader: DataLoader,
    mlf_logger: MLFlowLogger,
):

    n_features = dataset[0][0].shape[1]  # this is number of parallel inputs
    n_timesteps = dataset[0][0].shape[0]  # this is number of timesteps

    selected_model = instantiate(cfg.model)
    selected_optimizer = instantiate(cfg.optimizer)

    model = selected_model(device=cfg.training.device)

    optimizer = selected_optimizer(model.parameters())
    lightning = LightningModel(
        model, criterion=instantiate(cfg.criterion), optimizer=optimizer
    )
    timer_callback = Timer()
    trainer = L.Trainer(
        max_epochs=cfg.training.epochs,
        accelerator=cfg.training.device,
        val_check_interval=1,
        logger=mlf_logger,
        callbacks=[
            timer_callback,
            EarlyStopping(
                monitor="val_loss_epoch",
                verbose=True,
                mode="min",
                min_delta=0.01,
                patience=3,
            ),
            ThresholdEarlyStopping(
                threshold=cfg.training.early_stopping.threshold,
                monitor=cfg.training.early_stopping.monitor,
                patience=cfg.training.early_stopping.patience,
                min_delta=cfg.training.early_stopping.min_delta,
                mode=cfg.training.early_stopping.mode,
                check_on_train_epoch_end=cfg.training.early_stopping.check_on_train_epoch_end,  # Check at the step level, not at the epoch level
            ),
        ],
    )
    trainer.fit(lightning, train_dataloader, validation_dataloader)
    total_time = timer_callback.time_elapsed("train")
    print(f"Total training time: {total_time:.2f} seconds")
    print(trainer.callback_metrics)
    print("_______")


def train_base_pytorch(
    cfg: DictConfig,
    expression: GrammaticalExpression,
    dataset: Dataset,
    train_dataloader: DataLoader,
    validation_dataloader: DataLoader,
):

    n_features = dataset[0][0].shape[1]  # this is number of parallel inputs
    n_timesteps = dataset[0][0].shape[0]  # this is number of timesteps

    selected_model = instantiate(cfg.model)
    selected_optimizer = instantiate(cfg.optimizer)

    model = selected_model(device=cfg.training.device)
    print(model)
    criterion = instantiate(cfg.criterion)
    optimizer = selected_optimizer(model.parameters())

    start = time.time()
    train_loop(
        train_dataloader,
        model,
        criterion,
        optimizer,
        cfg.training.epochs,
        conditions=cfg.training.conditions,
    )
    end = time.time()
    print("Training time: ", end - start)
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

    mlflow.set_tracking_uri(f"http://{cfg.tracking.host}:{cfg.tracking.port}")
    # mlflow. disable_system_metrics_logging()
    # mlflow.set_tracking_uri("file:///mmfs1/gscratch/clmbr/haberc/altk/src/examples/learn_quant/mlruns")
    mlflow.set_experiment(f"{cfg.experiment_name}")

    mlflow.pytorch.autolog()

    # Print environment variables for debugging
    print(
        "MLFLOW_TRACKING_URI environment variable:",
        os.environ.get("MLFLOW_TRACKING_URI"),
    )
    print("MLflow version:", mlflow.version.VERSION)
    # Disable system metrics tracking
    os.environ["MLFLOW_SYSTEM_METRICS_ENABLED"] = "true"

    # Verify settings
    print(
        "MLFLOW_SYSTEM_METRICS_ENABLED:",
        os.environ.get("MLFLOW_SYSTEM_METRICS_ENABLED"),
    )
    print("Current MLflow Tracking URI:", mlflow.get_tracking_uri())

    print(OmegaConf.to_yaml(cfg))

    grammar = load_grammar(cfg)

    grammar, indices_tag = add_indices(
        grammar=grammar,
        indices=cfg.grammar.indices,
        m_size=cfg.universe.m_size,
        weight=cfg.grammar.index_weight,
    )
    print(cfg.grammar.indices)
    print(cfg.universe.m_size)
    print(cfg.grammar.index_weight)
    print(indices_tag)

    expressions_path = (
        cfg.expressions.output_dir
        + "M"
        + str(cfg.universe.m_size)
        + "/X"
        + str(cfg.universe.x_size)
        + "/d"
        + str(cfg.expressions.depth)
        + "/"
        + f"generated_expressions{indices_tag}.yml"
    )
    print("Reading expressions from: ", expressions_path)
    expressions, _ = read_grammatical_expressions(expressions_path, grammar)

    print("Number of expressions: ", len(expressions))
    import time

    # time.sleep(5)
    device = set_device(cfg.training.device)

    print("Loading universe...")
    universe = load_universe(cfg)
    universe = filter_universe(cfg, universe)

    try:
        if cfg.training.resume.term_expression:
            for i, expression in enumerate(expressions):
                if expression.term_expression == cfg.training.resume.term_expression:
                    print(
                        "Resuming training from expression: ",
                        expression.term_expression,
                    )
                    start_index = i
    except Exception as e:
        print("Could not resume training from specified expression.")
        print(e)
        start_index = 0

    for expression in tqdm(expressions[start_index : 1 + cfg.expressions.n_limit]):

        print("Calculating montonicity for expression: ", expression.term_expression)
        all_models, flipped_models, quantifiers, expression_names = get_verified_models(
            cfg, [expression], universe
        )
        monotonicity = measure_monotonicity(
            all_models,
            flipped_models,
            quantifiers[0],
            upward_monotonicity_entropy,
            cfg,
            name=expression_names[0],
        )
        print("Monotonicity: ", monotonicity)

        run_name = f"{expression.term_expression}"
        print("Running experiment: ", run_name)

        with mlflow.start_run(log_system_metrics=False, run_name=run_name) as mainrun:
            mlflow.log_metric("monotonicity_entropic", float(monotonicity))

            set_and_log_seeds(mainrun=True)

            mlflow.log_params(flatten(OmegaConf.to_container(cfg)))
            mlflow.log_param("expression", expression.term_expression)
            mlflow.log_param(
                "expression_depth",
                calculate_term_expression_depth(expression.term_expression),
            )
            mlflow.set_tag("Notes", cfg.notes)
            mlf_logger = MLFlowLogger(
                experiment_name=f"{cfg.experiment_name}",
                log_model=True,
                tracking_uri=mlflow.get_tracking_uri(),
                run_id=mainrun.info.run_id,
            )

            print("Expression: ", expression.term_expression)
            try:
                if cfg.expressions.generation_args:
                    print("Using generation args: ", cfg.expressions.generation_args)
                    dataset = QuantifierDataset(
                        expression,
                        representation=cfg.expressions.representation,
                        downsampling=cfg.expressions.downsampling,
                        generation_args=cfg.expressions.generation_args,
                    )
                else:
                    print("No generation args provided")
                    dataset = QuantifierDataset(
                        expression,
                        representation=cfg.expressions.representation,
                        downsampling=cfg.expressions.downsampling,
                    )
            except DatasetInitializationError as e:
                print(f"Skipping the expression due to error: {e}")
                continue

            dataset.inputs = dataset.inputs.to(device)
            dataset.targets = dataset.targets.to(device)

            if cfg.training.strategy == "kfold":

                kfold = KFold(n_splits=cfg.training.k_splits, shuffle=True)
                print(
                    "Running k-fold training with {} splits".format(
                        cfg.training.k_splits
                    )
                )
                for fold, (train_ids, valid_ids) in enumerate(kfold.split(dataset)):

                    with mlflow.start_run(run_name=f"{fold}", nested=True) as childrun:
                        set_and_log_seeds()

                        print(f"FOLD {fold}")
                        print("--------------------------------")
                        train_subsampler = SubsetRandomSampler(train_ids)
                        valid_subsampler = SubsetRandomSampler(valid_ids)

                        train_dataloader = DataLoader(
                            dataset,
                            batch_size=cfg.expressions.batch_size,
                            sampler=train_subsampler,
                        )
                        validation_dataloader = DataLoader(
                            dataset,
                            batch_size=cfg.expressions.batch_size,
                            sampler=valid_subsampler,
                        )

                        print(
                            "Training set size: ",
                            len(train_dataloader) * cfg.expressions.batch_size,
                        )
                        print(
                            "Validation set size: ",
                            len(validation_dataloader) * cfg.expressions.batch_size,
                        )

                        train(
                            cfg,
                            expression,
                            dataset,
                            train_dataloader,
                            validation_dataloader,
                            mlf_logger,
                        )

            elif cfg.training.strategy == "multirun":

                for i in range(cfg.training.n_runs):

                    with mlflow.start_run(run_name=f"{i}", nested=True) as childrun:
                        set_and_log_seeds()

                        print(f"RUN {i}")
                        print("--------------------------------")
                        train_data, validation_data = torch.utils.data.random_split(
                            dataset, [cfg.expressions.split, 1 - cfg.expressions.split]
                        )

                        train_dataloader = DataLoader(
                            train_data,
                            batch_size=cfg.expressions.batch_size,
                            shuffle=True,
                        )
                        validation_dataloader = DataLoader(
                            validation_data,
                            batch_size=cfg.expressions.batch_size,
                            shuffle=True,
                        )

                        print("Training set size: ", len(train_dataloader))
                        print("Validation set size: ", len(validation_dataloader))

                        train(
                            cfg,
                            expression,
                            dataset,
                            train_dataloader,
                            validation_dataloader,
                            mlf_logger,
                        )


if __name__ == "__main__":
    main()
