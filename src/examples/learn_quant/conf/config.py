import dataclasses
from dataclasses import dataclass, field
from omegaconf import DictConfig
import hydra
from hydra.core.config_store import ConfigStore


@dataclasses.dataclass
class ModeConfig:
    name: str


@dataclasses.dataclass
class UniverseConfig:
    m_size: int
    x_size: int
    weight: float
    inclusive_universes: bool


@dataclasses.dataclass
class GrammarConfig:
    depth: int


# Define a configuration schema
@dataclasses.dataclass
class Config:
    mode: ModeConfig
    universe: UniverseConfig
    grammar: GrammarConfig


cs = ConfigStore.instance()
# Registering the Config class with the name 'config'.
cs.store(name="conf", node=Config)
cs.store(group="universe", name="base_config", node=UniverseConfig)
cs.store(group="grammar", name="base_config", node=GrammarConfig)
