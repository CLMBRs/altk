import torch
import torch.nn as nn
import numpy as np
from ultk.language.grammar import GrammaticalExpression
from typing import Iterable

import torch
from torch.utils.data import Dataset
from learn_quant.sampling import sample_by_expression, downsample_quantifier_models


def set_device(training_device):
    if training_device == "mps":
        if torch.backends.mps.is_available():
            device = torch.device("mps")
            x = torch.ones(1, device=device)
            print("MPS device found.")
        else:
            print("MPS device not found.")
    elif training_device == "cpu":
        print("Using CPU.")
        device = torch.device("cpu")
    elif training_device in ["gpu", "cuda"]:
        print("Using GPU.")
        device = torch.device("cuda")
    return device


class ExpressionDataset(Dataset):
    """Creates a PyTorch dataset from a collection of GrammaticalExpressions.
    Adds all QuantifierModels from all Grammatical Expressions to the dataset.
    Mode can be any of the levels associated with the `binarize` function of the QuantifierModel class.
    """

    def __init__(
        self, expressions: Iterable[GrammaticalExpression], representation="one_hot"
    ):
        """
        Args:
            data (list or array-like): A collection of objects to be transformed into vector representations.
            metadata (list or array-like, optional): Additional information or labels tied to each data object.
            transform (callable, optional): A function/transform that converts an object to its vector representation.
        """
        self.expressions = expressions
        inputs = []
        targets = []
        for expression in expressions:
            for model in expression.meaning.mapping:
                in_meaning_value = expression.meaning.mapping[model]
                if in_meaning_value:
                    y_vector = torch.tensor([1, 0], dtype=torch.float32)
                else:
                    y_vector = torch.tensor([0, 1], dtype=torch.float32)
                inputs.append(
                    torch.tensor(
                        model.to_numpy(mode=representation), dtype=torch.float32
                    )
                )
                targets.append(y_vector)
        self.inputs = torch.stack(inputs, dim=0)
        self.targets = torch.stack(targets, dim=0)

        assert len(self.inputs) == len(
            self.targets
        ), "Data and metadata must have the same length"

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, idx):
        return self.inputs[idx], self.targets[idx]

    def __get_label(self, idx):
        return self.targets[idx]


class QuantifierDataset(Dataset):
    """Creates a PyTorch dataset from a collection of QuantifierModels.
    Mode can be any of the levels associated with the `binarize` function of the QuantifierModel class.
    """

    def __init__(
        self,
        expression: GrammaticalExpression,
        representation="one_hot",
        downsampling=True,
        generation_args=None,
    ):
        """
        Args:
            data (list or array-like): A collection of objects to be transformed into vector representations.
            metadata (list or array-like, optional): Additional information or labels tied to each data object.
            transform (callable, optional): A function/transform that converts an object to its vector representation.
        """
        self.expression = expression
        inputs = []
        targets = []

        match expression:
            case GrammaticalExpression():
                if generation_args:
                    models = sample_by_expression(expression, **generation_args)
                elif downsampling:
                    models = downsample_quantifier_models(expression)
                else:
                    models = expression.meaning.mapping
            case _:
                raise ValueError("Only GrammaticalExpressions are supported")

        for model, in_meaning_value in models.items():
            if in_meaning_value:
                y_vector = torch.tensor([1, 0], dtype=torch.float32)
            else:
                y_vector = torch.tensor([0, 1], dtype=torch.float32)
            inputs.append(
                torch.tensor(model.to_numpy(mode=representation), dtype=torch.float32)
            )
            targets.append(y_vector)
        self.inputs = torch.stack(inputs, dim=0)
        self.targets = torch.stack(targets, dim=0)

        assert len(self.inputs) == len(
            self.targets
        ), "Data and metadata must have the same length"

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, idx):
        return self.inputs[idx], self.targets[idx]

    def __get_label(self, idx):
        return self.targets[idx]


class MV_LSTM(torch.nn.Module):
    # add embedding layer that the one hot references
    def __init__(self, input_dim, seq_len, device="cpu"):
        super(MV_LSTM, self).__init__()
        self.n_features = input_dim
        self.seq_len = seq_len
        self.n_hidden = 20  # number of hidden states
        self.n_layers = 3  # number of LSTM layers (stacked)
        self.device = device

        self.l_lstm = torch.nn.LSTM(
            input_size=input_dim,
            hidden_size=self.n_hidden,
            num_layers=self.n_layers,
            batch_first=True,
            device=device,
        )
        # according to pytorch docs LSTM output is
        # (batch_size,seq_len, num_directions * hidden_size)
        # when considering batch_first = True
        self.l_linear = torch.nn.Linear(self.n_hidden, 2, device=device)

    def init_hidden(self, batch_size):
        # even with batch_first = True this remains same as docs
        hidden_state = torch.zeros(
            self.n_layers, batch_size, self.n_hidden, device=self.device
        )
        cell_state = torch.zeros(
            self.n_layers, batch_size, self.n_hidden, device=self.device
        )
        self.hidden = (hidden_state, cell_state)

    def forward(self, x):
        batch_size, seq_len, _ = x.size()

        lstm_out, self.hidden = self.l_lstm(x, self.hidden)
        # lstm_out(with batch_first = True) is
        # (batch_size,seq_len,num_directions * hidden_size)
        # for following linear layer we want to keep batch_size dimension and merge rest
        # .contiguous() -> solves tensor compatibility error

        # can just take the last token
        x = lstm_out[:, -1, :]
        return self.l_linear(x)


def compute_accuracy(outputs, targets):
    probs = torch.sigmoid(outputs)

    # Apply a threshold of 0.5 to convert probabilities to binary predictions (0 or 1)
    preds = (probs > 0.5).float()

    correct = (preds == targets).float()

    # Compute accuracy - use numel to get the number of elements in the tensor (if size, metric is double what it should be)
    accuracy = correct.sum() / torch.numel(correct)

    return accuracy


def train_loop(dataloader, model, criterion, optimizer, epochs, conditions=None):

    def check_conditions(ledger, metrics):
        if metrics["accuracy"] > 0.99:
            ledger["accuracy_tally"] += 1
        if metrics["loss"] < 0.01:
            ledger["loss_tally"] += 1
        if ledger["accuracy_tally"] >= 100 or ledger["loss_tally"] >= 100:
            return True
        return False

    size = len(dataloader.dataset)
    # Loop over epochs
    ledger = {"loss_tally": 0, "accuracy_tally": 0}
    terminate = False
    for epoch in range(epochs):
        metrics = {"loss": 0, "accuracy": 0, "batch": 0, "epoch": 0}
        running_loss = 0.0
        running_accuracy = 0.0
        print(f"Epoch {epoch+1}/{epochs}")
        # Set the model to training mode
        model.train()
        for batch, (X, y) in enumerate(dataloader):

            if conditions:
                if check_conditions(ledger, metrics):
                    print("Conditions met. Stopping training.")
                    return

            # Initialize the hidden state (assuming this is an RNN-based model)
            if isinstance(model, MV_LSTM):
                model.init_hidden(X.size(0))

            optimizer.zero_grad()

            pred = model(X)
            loss = criterion(pred, y)

            loss.backward()
            optimizer.step()

            running_loss += loss.item()

            accuracy = compute_accuracy(pred, y)
            running_accuracy += accuracy.item()

            if batch % 10 == 0 or batch == len(dataloader) - 1:
                print(
                    f"Epoch {epoch+1}, Batch {batch}, Cumulative Batch {epoch*len(dataloader)+batch}, Accuracy: {accuracy.item()}, Loss: {loss.item():.4f}"
                )
            metrics = {
                "loss": loss.item(),
                "accuracy": accuracy.item(),
                "batch": batch,
                "epoch": epoch,
            }

        avg_train_loss = running_loss / len(dataloader)
        avg_train_accuracy = running_accuracy / len(dataloader)

        # print overall progress at the end of the epoch
        print(f"Epoch {epoch+1} completed\n")


# Positional Encoding to add to the input features
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=8, device="cpu"):
        super(PositionalEncoding, self).__init__()

        pe = torch.zeros(max_len, d_model, device=device)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float()
            * (-torch.log(torch.tensor(10000.0)) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)  # Shape: (1, max_len, d_model) to broadcast over batch
        self.register_buffer("pe", pe)

    def forward(self, x):
        # x shape: (batch_size, seq_len, d_model)
        # Add positional encoding to each sequence
        x = x + self.pe[:, : x.size(1), :]  # Apply across the sequence length dimension
        return x


# Transformer-based model
# Explicitly set num decoder layers to 0 in self.Transformer
# Either no embeddings or embeddings
# Transformer-based model
class TransformerModel(nn.Module):
    def __init__(
        self,
        input_dim=5,
        seq_len=8,
        num_classes=2,
        d_model=32,
        nhead=4,
        num_encoder_layers=2,
        dim_feedforward=32,
        device="cpu",
    ):
        super(TransformerModel, self).__init__()
        self.device = device

        self.embedding = nn.Linear(input_dim, d_model, device=device)

        self.positional_encoding = PositionalEncoding(
            d_model, max_len=seq_len, device=device
        )

        self.transformer = nn.Transformer(
            d_model=d_model,
            nhead=nhead,
            num_encoder_layers=num_encoder_layers,
            dim_feedforward=dim_feedforward,
            device=device,
        )

        self.fc_out = nn.Linear(
            d_model, num_classes, device=device
        )  # Flatten transformer output to predict [0, 1] or [1, 0]
        # COMMENT: Instead of flattening, we can take just the final token - that would be taking out seq len

    def forward(self, x):
        # x shape: (batch_size, seq_len, input_dim)
        batch_size, seq_len, input_dim = x.shape

        # x = x.view(batch_size * seq_len, input_dim)
        self.src_mask = nn.Transformer.generate_square_subsequent_mask(
            x.size(1), device=torch.device(self.device)
        )

        x = self.embedding(x)  # Shape: (batch_size * seq_len, d_model)

        x = self.positional_encoding(x)

        x = x.permute(1, 0, 2)  # Shape: (seq_len, batch_size, d_model)

        x = self.transformer.encoder(
            x, mask=self.src_mask
        )  # Shape: (seq_len, batch_size, d_model) # should be x = self.transformer.encoder(x)
        # COMMENT: Add in mask -  , mask=self.src_mask)

        x = x.permute(1, 0, 2)[:, -1, :]  # Shape: (batch_size, seq_len * d_model)
        # COMMENT: x.permute(1, 0, 2)[:, -1, :] ? maybe squeeze because we want a final shape of (batch_size, d_model)

        output = self.fc_out(x)  # Shape: (batch_size, num_classes)
        return output
