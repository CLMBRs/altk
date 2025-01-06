"""Classes for representing communicative agents, such as Senders and Receivers figuring in Lewis-Skyrms signaling games, literal and pragmatic agents in the Rational Speech Act framework, etc."""

from typing import Any
import numpy as np
from scipy.special import softmax
from ultk.language.language import Expression, Language
from ultk.language.semantics import Referent

##############################################################################
# Base communicative agent class
##############################################################################


class CommunicativeAgent:
    def __init__(self, language: Language, **kwargs):
        """An agent that uses a language to communicate, e.g. a RSA pragmatic agent or a Lewis-Skyrms signaler.

        Args:
            language: a language to construct a agent to define the relation between meanings and expressions, which can be used to initialize the agent matrices (e.g. `S` or `R`).

            name: an optional string to name the communicative agent
        """
        self.language = language

        # weight matrix indexing lookups
        self._referent_to_index = {
            referent: i for i, referent in enumerate(self.language.universe.referents)
        }
        self._index_to_referent = tuple(self.language.universe.referents)
        self._expression_to_index = {
            expression: i for i, expression in enumerate(self.language.expressions)
        }
        self._index_to_expression = tuple(self.language.expressions)

        self.shape = None
        self.weights = None

        # TODO: just self.__dict__.update(kwargs)?
        if "name" in kwargs:
            self.name = kwargs["name"]

        if "weights" in kwargs:
            self.weights = kwargs["weights"]

    @property
    def weights(self) -> np.ndarray:
        return self._weights

    @weights.setter
    def weights(self, weights: np.ndarray) -> None:
        self._weights = weights

    def normalized_weights(self) -> None:
        """Return the normalized weights of a CommunicativeAgent so that each row vector represents a probability distribution."""
        raise NotImplementedError

    def initialize_weights(self, weights: np.ndarray = None, initial="ones") -> None:
        """Initialize the agent's weight matrix.

        Args:
            weights: an np.ndarray representing the weights to initialize the agent with. By default None, and the agent's weights will be initialized uniformly.

            initial: {'ones', 'random'} a str reprsenting the initialization method to use. If 'ones' (default), initialize the weight matrix with `np.ones`. If 'random', initalize the weight matrix from `np.random.uniform`.
        """
        if weights is not None:
            if weights.shape != self.shape:
                raise ValueError(
                    f"Inapropriate Sender weight matrix shape for language. Sender is of shape {self.shape} but received {weights.shape}."
                )
            self.weights = weights
        else:
            # initialize equally
            if initial == "ones":
                self.weights = np.ones(self.shape)
            # initialize from uniform distribution
            elif initial == "random":
                self.weights = np.random.uniform(low=0.0, high=1.0, size=self.shape)
            else:
                raise ValueError(
                    f"Inappropriate value received for argument `initial`. Possible values are {'ones', 'random'}, but received: {initial}. "
                )

    def referent_to_index(self, referent: Referent) -> int:
        return self._referent_to_index[referent]

    def index_to_referent(self, index: int) -> Referent:
        return self._index_to_referent[index]

    def expression_to_index(self, expression: Expression) -> int:
        return self._expression_to_index[expression]

    def index_to_expression(self, index: int) -> Expression:
        return self._index_to_expression[index]

    def strategy_to_indices(self, strategy: dict[str, Any]) -> tuple[int]:
        """Maps communicative strategies to weights.

        Given a expression and referent, access the corresponding weight coordinate.

        Args:
            strategy: a dict of the form {"referent": Referent, "expression": expression} representing an instance of communicative behavior, which we may call a communicative strategy for this agent.
        """
        raise NotImplementedError

    def sample_strategy(self, index: int) -> int:
        """Sample a communicative strategy (e.g., a word for Speaker's intended referent, or interpretation for Listener's heard word) by uniformly sampling from a row vector of the agent's weight matrix specified by the index.

        Args:
            index: the integer index representing a row of the weight matrix.

        Returns:
            the integer index of the agent's choice
        """
        choices = self.weights[index]
        choices_normalized = choices / choices.sum()
        return np.random.choice(a=range(len(choices)), p=choices_normalized)

    def to_language(
        self,
        data: dict = {"complexity": None, "accuracy": None},
        threshold: float = 0.1,
    ) -> Language:
        """Get a language from the agent, representing its current (possibly learned) communicative behavior.

        This function uses:
            1. the agent's weight matrix,
            1. the set of expression forms, and
            1. the set of referents

        from the language the agent was initialized with to generate a new language accurately reflecting the new expression meanings, e.g. how the agent interprets expressions as meaning zero or more referents.

        Args:
            threshold: a float in [0,1] representing the cutoff for determining if a meaning (referent) can be communicated by a expression. Because weights are not initialized to 0, it is a good idea to set nonzero values as the threshold.

        Returns:
            a Language corresponding to the form-meaning mapping defined by the communicative agent's weights.
        """
        # Construct the same kind of language as initialized with
        language_type = type(self.language)
        expression_type = type(self.language.expressions[0])
        meaning_type = type(self.language.expressions[0].meaning)

        # get distribution over communicative policies from a weight matrix
        policies = self.normalized_weights()

        expressions = []
        # loop over agent's vocabulary
        for old_expression in self.language.expressions:
            # get all meanings that the expression can communicate
            referents = tuple(
                [
                    referent
                    for referent in self.language.universe.referents
                    if policies[
                        self.strategy_to_indices(
                            strategy={
                                "referent": referent,
                                "expression": old_expression,
                            }
                        )
                    ]
                    > threshold  # if probability of referent is high enough
                ]
            )

            meaning = meaning_type(referents, self.language.universe)
            # construct the updated expression as a new form-meaning mapping
            expression = expression_type(form=old_expression.form, meaning=meaning)
            expressions.append(expression)

        if "name" not in data:
            data["name"] = self.name

        return language_type(expressions, data=data)


##############################################################################
# Derived Speaker and Listener classes
##############################################################################


class Speaker(CommunicativeAgent):
    def __init__(self, language: Language, **kwargs):
        super().__init__(language, **kwargs)

    @property
    def S(self) -> np.ndarray:
        return self.weights

    @S.setter
    def S(self, mat: np.ndarray) -> None:
        self.weights = mat

    def normalized_weights(self) -> np.ndarray:
        """Get the normalized weights of a Speaker.

        Each row vector represents a conditional probability distribution over expressions, P(e | m).
        """
        # The sum of p(e | intended m) must be exactly 0 or 1.
        # We check for nans because sometimes a language cannot express a particular meaning at all, resulting in a row sum of 0.
        np.seterr(divide="ignore", invalid="ignore")
        return np.nan_to_num(self.S / self.S.sum(axis=1, keepdims=True))


class Listener(CommunicativeAgent):
    def __init__(self, language: Language, **kwargs):
        super().__init__(language, **kwargs)

    @property
    def R(self) -> np.ndarray:
        return self.weights

    @R.setter
    def R(self, mat: np.ndarray) -> None:
        self.weights = mat

    def normalized_weights(self) -> np.ndarray:
        """Normalize the weights of a Listener so that each row vector for the heard expression e represents a conditional probability distribution over referents P(m | e)."""
        # The sum of p(m | heard e) must be 1.
        np.seterr(divide="ignore", invalid="ignore")
        return np.nan_to_num(self.R / self.R.sum(axis=1, keepdims=True))


##############################################################################
# Rational Speech Act agent classes
##############################################################################
"""In the Rational Speech Act framework, communicative agents reason recursively about each other's literal and pragmatic interpretations of utterances. Concretely, each agent is modeled by a conditional distribution. The speaker is represented by the probability of choosing to use an utterance (expression) given an intended meaning, P(e|m). The listener is a mirror of the speaker; it is represented by the probability of guessing a meaning given that they heard an utterance (expression), P(m|e).
"""


class LiteralSpeaker(Speaker):
    """A literal speaker chooses utterances without any reasoning about other agents. The literal speaker's conditional probability distribution P(e|m) is uniform over all expressions that can be used to communicate a particular meaning. This is in contrast to a pragmatic speaker, whose conditional distribution is not uniform in this way, but instead biased towards choosing expressions that are less likely to be misinterpreted by some listener."""

    def __init__(self, language: Language, **kwargs):
        super().__init__(language, **kwargs)
        self.S = self.language.binary_matrix()
        self.S = self.normalized_weights()


class LiteralListener(Listener):
    """A naive literal listener interprets utterances without any reasoning about other agents. Its conditional probability distribution P(m|e) for guessing meanings is uniform over all meanings that can be denoted by the particular expression heard. This is in contrast to a pragmatic listener, whose conditional distribution is biased to guess meanings that a pragmatic speaker most likely intended."""

    def __init__(self, language: Language, **kwargs):
        super().__init__(language, **kwargs)
        self.R = self.language.binary_matrix().T
        self.R = self.normalized_weights()


class PragmaticSpeaker(Speaker):
    """A pragmatic speaker chooses utterances based on how a listener would interpret them. A pragmatic speaker may be initialized with any kind of listener, e.g. literal or pragmatic -- meaning the recursive reasoning can be modeled up to arbitrary depth."""

    def __init__(
        self, language: Language, listener: Listener, temperature: float = 1.0, **kwargs
    ):
        """Initialize the |M|-by-|E| matrix, S, corresponding to the pragmatic speaker's conditional probability distribution over expressions given meanings.

        The pragmatic speaker chooses expressions to communicate their intended meaning according to:

        $P(e | m) \propto \\exp(t * u(e,m))$

        where $t \in [0,1]$ is a temperature parameter and utility $u$ is defined

        $u(e , m) := \\log(P_{\\text{Listener}}(m | e))$

        Args:
            language: the language with |M| meanings and |E| expressions defining the size of S.

            listener: a communicative agent storing a matrix R representing the conditional distribution over expressions given meanings.

            temperature: a float \in [0,1], representing how `optimally rational' the pragmatic speaker is; 1.0 is chosen when no particular assumptions about rationality are made.
        """
        super().__init__(language, **kwargs)

        # Row vector \propto column vector of literal R
        self.S = softmax(np.nan_to_num(np.log(listener.R.T)) * temperature, axis=1)


class PragmaticListener(Listener):
    """A pragmatic listener interprets utterances based on their expectations about a pragmatic speaker's decisions. A pragmatic listener may be initialized with any kind of speaker, e.g. literal or pragmatic -- meaning the recursive reasoning can be modeled up to arbitrary depth."""

    def __init__(
        self, language: Language, speaker: Speaker, prior: np.ndarray, **kwargs
    ):
        """Initialize the |E|-by-|M| matrix, R, corresponding to the pragmatic listener's conditional probability distribution over meanings given expressions.

        The pragmatic listener chooses meanings as their best guesses of the expression they heard according to:

        $P(m | e) \propto P_{\\text{PragmaticSpeaker}}(e | m)$

        Args:
            language: the language with |M| meanings and |E| expressions defining the size of R.

            speaker: a communicative agent storing a matrix S representing the  conditional distribution over expressions given meanings.

            prior: a diagonal matrix of size |M|-by-|M| representing the communicative need probabilities for meanings.
        """
        super().__init__(language, **kwargs)
        # R(m | w) \propto sum_m p(m) S(w | m)
        col_prior_dot = speaker.S.T @ prior
        self.R = col_prior_dot / np.sum(col_prior_dot, axis=1, keepdims=True)
