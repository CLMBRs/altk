from ultk.effcomm.informativity import informativity
from ultk.language.grammar import GrammaticalExpression
from ultk.language.language import Language, aggregate_expression_complexity
from ultk.language.semantics import Meaning

from learn_quant.meaning import create_universe
from learn_quant.util import read_expressions
from learn_quant.quantifier import QuantifierUniverse, QuantifierModel
from concepts.contexts import Context

from itertools import product
import math
from scipy.stats import entropy
import pandas as pd
import numpy as np
from tqdm import tqdm
from scipy import sparse


class MonotonicityMeasurer:
    
    def __init__(self, universe: QuantifierUniverse, monotone_set: str ='A', down: bool = False):
        """_summary_

        Args:
            universe (QuantifierUniverse): A quantifier universe
            monotone_set (str, optional): Define the reference set to measure monotonicity. Defaults to 'A'.
            down (bool, optional): If set to down, superstructures are found instead of substructures. Defaults to False.
        """
        self.down = down
        self.universe = universe
        self.monotone_set = monotone_set
        self.concept_lattice = self._calculate_lattice()

        
    def _calculate_model_pertinence(self, expressions):
        self.metrics = {}

        membership = sparse.lil_matrix((len(self.universe),len(expressions)),dtype=int)
        submembership = sparse.lil_matrix((len(self.universe),len(self.universe)),dtype=int)
        model_dictionary = {}
        for model_id, model in enumerate(self.universe.referents):
            model_dictionary[model.name] = model_id
        for model_id, model in enumerate(self.universe.referents):
            for expression_id, quantifier_expression in enumerate(expressions):
                self.metrics[str(quantifier_expression)] = {}
                if model in quantifier_expression.meaning.referents:
                    membership[model_id, expression_id] = 1
            sub_ids = list(map(model_dictionary.__getitem__, self._get_sub_structures([model.name])))
            for sub_id in sub_ids:
                submembership[sub_id,model_id] = 1
        
        self.membership = membership.todense()
        self.submembership = submembership.todense()
    
    def _get_names(self) -> list:
        """Get the names of the referents in the loaded quantifier universe.

        Returns:
            list: List of names of referents in the quantifier universe.
        """
        return [referent.name for referent in self.universe.referents]

    def _get_truth_matrix(self) -> pd.DataFrame:
        """Get a pandas dataframe that stores the truth vectors of all models in the quantifier universe

        Returns:
            pd.DataFrame: A dataframe of booleans arrays that track the indices of set items of A intersected by B.
        """
        truth_array = []
        for quantifier_model in self.universe.referents:
            truth_array.append(quantifier_model.get_truth_vector())
        truth_df = pd.concat([pd.DataFrame(self._get_names()).rename(columns={0: 'names'}), pd.DataFrame(truth_array)], axis=1).set_index("names")
        return truth_df

    def _switch_direction(self, bools: list[list[bool]]) -> list[list[bool]]:
        """Switches the value of True to False and vice versa.

        Args:
            bool (list[list[bool]]): Accepts a list of lists of bools 

        Returns:
            list[list[bool]]: A list of lists of bools, flipped unless self.down == True. 
        """
        if self.down:
            return bools
        else:
            return np.invert(bools)

    def _calculate_lattice(self) -> Context:
        """ 

        Returns:
            Context: Created from ``objects``, ``properties``, and ``bools`` correspondence.

            objects: Iterable of object label strings.
            properties: Iterable of property label strings.
            bools: Iterable of ``len(objects)`` tuples of ``len(properties)`` booleans.

            See https://github.com/haberchr/concepts/blob/master/concepts/contexts.py

        """
        truth_df = self._get_truth_matrix()
        objects = truth_df.index.astype(str).tolist()
        properties = [x for x in truth_df.columns]
        bools = list(truth_df.fillna(False).astype(bool).itertuples(index=False, name=None))
        bools = self._switch_direction(bools)
        return Context(objects, properties, bools)
    
    def _get_sub_structures(self, name: list[str]) -> set[str]:

        """Accepts a list of a singleton name to get a set of substructures of the indexed model, excluding the indexing model name.

        Returns:
            set(str): Tuple of substructures of the model indexed that exist in the universe.

        """

        return set(self.concept_lattice[name][0]) - set(name)
    
    def _has_sub_structure(self, name: list[str]) -> bool:

        """Identity function for a model having a substructure in the universe.

        Returns:
            bool: ``True`` if there is one or more substructures in the universe, otherwise ``False``.
        """

        return True if len(set(self.concept_lattice[name][0]) - set(name)) > 0 else False
    
    def _get_sub_structure_in_meaning(self, name: list[str], meaning: Meaning) -> set[str]:

        """Identity function for a model having a substructure in a defined Meaning.

        Returns:
            set(str): Tuple of substructures of the model indexed that exist in the selected Meaning.
        """

        names = set(referent.name for referent in meaning.referents)

        return self._get_sub_structures(name) & names
    
    def _has_sub_structure_in_meaning(self, name: list[str], meaning: Meaning) -> bool:

        """Identity function for a model having a substructure in a defined Meaning.

        Returns:
            bool: ``True`` if there is one or more substructures in the universe, otherwise ``False``.
        """

        return True if len(self._get_sub_structure_in_meaning(name, meaning)) > 0 else False
    
    def vectorized_upward_monotonicity_entropy(self):
        """
        Vectorized version to compute upward monotonicity entropy for all quantifiers.
        """
        quantifiers = self.membership  # Assuming this is a matrix with quantifiers in columns
        num_quantifiers = quantifiers.shape[1]

        # Compute probabilities
        p_q = np.mean(quantifiers, axis=0)
        q_ent = -np.sum(p_q.T * np.log2(p_q + (p_q == 0)), axis=0)  # Sum along rows

        true_preds = np.dot(self.submembership, quantifiers) >= 1

        # Probabilities for having a true predecessor
        p_pred = np.mean(true_preds, axis=0)
        p_nopred = 1 - p_pred

        # Conditional probabilities
        q_pred = np.sum(quantifiers.T * true_preds, axis=0) / np.sum(true_preds, axis=0)
        q_nopred = np.sum(quantifiers.T * ~true_preds, axis=0) / np.sum(~true_preds, axis=0)
        noq_pred = np.sum(~quantifiers.T * true_preds, axis=0) / np.sum(true_preds, axis=0)
        noq_nopred = np.sum(~quantifiers.T * ~true_preds, axis=0) / np.sum(~true_preds, axis=0)

        # Avoid division by zero
        q_pred = np.nan_to_num(q_pred)
        q_nopred = np.nan_to_num(q_nopred)
        noq_pred = np.nan_to_num(noq_pred)
        noq_nopred = np.nan_to_num(noq_nopred)

        # Compute the conditional entropies
        pred_logs = np.nan_to_num(np.log2([noq_pred, q_pred] / p_pred))
        nopred_logs = np.nan_to_num(np.log2([noq_nopred, q_nopred] / p_nopred))
        ent_pred = -np.nansum(np.array([noq_pred, q_pred]) * pred_logs, axis=0)
        ent_nopred = -np.nansum(np.array([noq_nopred, q_nopred]) * nopred_logs, axis=0)

        # Compute conditional entropy
        cond_ent = ent_pred + ent_nopred

        # Return vectorized result
        return 1 - cond_ent / q_ent
    
    def __call__(self, expressions):

        """
        Evaluates the upward monotonicity entropy for all quantifier expressions using vectorization.
        """
        self._calculate_model_pertinence(expressions)

        monotonicities = self.vectorized_upward_monotonicity_entropy()
        for expr_id, expr in enumerate(self.expressions):
            print(f"Calculating monotonicity for: {expr}")
            self.metrics[str(expr)] = {
                "monotonicity": monotonicities[expr_id]
            }