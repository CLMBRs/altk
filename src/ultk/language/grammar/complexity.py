from ultk.language.grammar.grammar import GrammaticalExpression
from ultk.language.grammar.grammar import Meaning
from ultk.language.grammar.boolean import RuleNames
from ultk.language.semantics import Universe
import numpy as np

HARD_HEURISTIC_CEILING = 2500  # Best solutions are likely before 1000 iterations

def expression_length(expr: GrammaticalExpression) -> int:
    """Get the expression length (number of nodes in a tree).
    See `GrammaticalExpression.__len__` for more information.

    Args:
        expr: the expression

    Returns:
        the expression's length
    """
    return len(expr)


def num_atoms(expr: GrammaticalExpression) -> int:
    """Count the number of atoms in a GrammaticalExpression.

    Args:
        expr: the expression

    Returns:
        the number of atoms
    """
    if expr.is_atom():
        return 1
    return sum(num_atoms(child) for child in expr.children)


################################################################
# Boolean Operations
################################################################

def is_product_or_singleton(expr: GrammaticalExpression) -> bool:
    """Helper function. Returns true if the GrammaticalExpression represents an atom, or has AND as the root."""
    
    return expr.is_atom or (expr.rule_name == RuleNames.AND and len(expr.children) > 0) # Not sure if we want that secondary check here

def boolean_cover(expr: GrammaticalExpression, axis_values:list) -> GrammaticalExpression:
    """
    Replace the sum of all atoms with multiplicative identity.
    If $n=$ num_flavors, and $f_i$ is the $i$-th flavor,

        $\sum_{i=1}^{n}(f_i) = 1$
    """

    # Unwrap atoms and check for array cover.
    if expr.rule_name == RuleNames.OR and set(axis_values) == set(
        [
            child.rule_name
            for child in expr.children
            if child.is_atom()
        ]
    ):
        return GrammaticalExpression("1", func=lambda *args:True, children=None)

    # Recursive
    elif [child for child in expr.children]:
        children = [
            child
            if child.is_atom()
            else boolean_cover(child)
            for child in expr.children
        ]
        return GrammaticalExpression(rule_name=expr.rule_name, func=expr.func, children=children)

    return expr


##########################################################################
# Addition
#
# At least binary branching. Will have at most the number of terms in
# the DNF of the array representation.
##########################################################################
def identity_or(expr: GrammaticalExpression) -> GrammaticalExpression:
    """
    Applies additive identity law.
        (+ a b ... 0 ... c) => (+ a b c)
        (+ a 0) => (a)
        (+ 0) => (0)
    """
    if expr.rule_name == RuleNames.OR and expr.contains_name("0"):
        children = [child for child in expr.children if not child.rule_name=="0"]
        if children == []:
            return GrammaticalExpression("0", func = lambda *args: False, children=None)
        elif len(children) == 1:
            return children[0]
        else:
            return GrammaticalExpression(expr.rule_name, expr.func, children=children)
    if expr.children:
        return GrammaticalExpression(
            expr.rule_name,
            expr.func,
            children=[
                # child if isinstance(child, str)
                identity_or(child)
                for child in expr.children
            ],
        )
    return expr

 ##########################################################################
    # Multiplication
    #
    # Binary branching. This is because multiplication is a
    # binary operator, and iterated multiplication of more than 2 atoms is
    # either redundant (idempotence) or results in 0, e.g.
    #     xyz = 0
    #     xxy = xy
    ##########################################################################

def identity_and(expr: GrammaticalExpression) -> GrammaticalExpression:
    """
    Applies multiplicative identity.
        (* a b ... 1 ... c) => (* a b c)
        (* a 1) => (a)
    """
    if expr.rule_name == RuleNames.AND and expr.contains_name("1"):
        children = [child for child in expr.children if not child.rule_name=="1"]
        if children == []:
            return GrammaticalExpression("1", func = lambda *args: True, children=None)
        elif len(children) == 1:
            return children[0]
        else:
            return GrammaticalExpression(expr.rule_name, expr.func, children=children)
        
    # Recursively iterate through all children and find the multiplicative identity of all of them
    #if [child for child in expr.children]:
    if expr.children:
        return GrammaticalExpression(
            expr.rule_name,
            expr.func,
            children=[
                # child if isinstance(child, str)
                identity_and(child)
                for child in expr.children
            ],
        )
    return expr
            
#################################################################
# Distributivity
#################################################################

def distr_or_over_and(expr: GrammaticalExpression, factor: GrammaticalExpression) -> GrammaticalExpression:
    """
    Factor out a term from a SOP.
    Reverses distributivity of multiplication over addition.
        (+ (* x y) (* x z)) => (* x (+ y z))
        (+ (* x y) (* x z) (* w v)) => (+ (* x (+ y z)) (* w v))

    Only applies the inference if reduces length, not for e.g.
        (+ (* x y) (* w v)) => (+ (* x y) (* w v))

    Because this function is parametrized by the atom to factor
    out, the minimization heuristic search tree branches for
    each possible atom factor that _shortens_ the expression, e.g.:

    xy + xz + wy + wa
        - branch x: x(y + z) + wy + wa  LEN 7
            - branch w: x(y + z) + w(y + a) LEN 6
        - branch y: y(x + w) + xz + wa  LEN 7
    """
    if expr.rule_name != RuleNames.OR:
        return expr
    factored_terms = []  # list of atoms
    remaining_terms = []  # list of trees
    for child in expr.children:
        if is_product_or_singleton(child):
            if factor in child.children:
                factored_terms += [gc for gc in child.children if gc != factor]
                continue
        remaining_terms.append(child)

    if len(factored_terms) < 2:
        return expr

    factors_tree = GrammaticalExpression(rule_name=RuleNames.OR, func = lambda *args: any(args), children=factored_terms)
    factored_tree = GrammaticalExpression(
        rule_name=RuleNames.AND, func = lambda *args: all(args), children=[factor, factors_tree]
    )
    if remaining_terms:
        children = [factored_tree] + remaining_terms
        return GrammaticalExpression(rule_name=RuleNames.OR, func = lambda *args: any(args), children=children)
    else:
        return factored_tree

#################################################################
# Complement
#################################################################

def negation( expr: GrammaticalExpression) -> GrammaticalExpression:
    """
    An operation, not an inference.
    Embed an expression under a negation operator.
        (x ) => (- (x ))
    """
    return GrammaticalExpression(RuleNames.NOT, func = lambda x: not x, children=[expr])

def return_atom_fn(atom):
    if atom == "0":
        return lambda x: False
    elif atom == "1":
        return lambda x: True
    else:
         return lambda x: x

def shorten_expression(
         expr: GrammaticalExpression, atoms, others, atoms_c
    ) -> GrammaticalExpression:
        """
        Helper function to sum complement.
        - atoms
        a list of the expression tree's children that are atoms
        - others
        the list of the expression tree's children that are not atoms.
        - atoms_c is a set of atoms: 1 - atoms. Replaces atoms if is shorter.
        """
        if not atoms_c:
            # Allow flavor cover to handle
            return expr

        if len(atoms_c) < len(atoms):
            # if shortens expression, use new sum of wrapped atoms.
            atoms = [
                GrammaticalExpression(atom, func = return_atom_fn(atom)
                                      ) 
                                      if not isinstance(atom, GrammaticalExpression) else atom
                for atom in atoms_c
            ]
            comp = GrammaticalExpression(
                rule_name=RuleNames.NOT, func = lambda x: not x,
                children=[GrammaticalExpression(rule_name=RuleNames.OR, func = lambda *args: any(args), children=atoms)],
            )
            new_children = [comp] + others

            return GrammaticalExpression(rule_name=expr.rule_name, func=expr.func, children=new_children)
        
        return expr

def sum_complement(expr: GrammaticalExpression, uni:Universe) -> GrammaticalExpression:
        """
        Reduces a sum to its complement if the complement is shorter, e.g.
        flavors= e, d, c
            (+ (e ) (d ) (* (E ) (c ))) => (+ (- (c )) (* (E )(c )))
        """
        children = expr.children

        # Base case
        if not children or len(children) < 1:
            return expr

        # Base case
        if expr.rule_name == RuleNames.OR:

            atoms = []
            others = []
            for child in children:
                if child.is_atom():
                    atoms.append(child.ruleName)
                else:
                    others.append(sum_complement(child))

            axes = uni.axes_from_referents()

            for axis, axis_values in axes:

                if atoms and (set(atoms) <= set(axis_values)):
                    atoms_c = list(set(axis_values) - set(atoms))
                    return shorten_expression(expr, atoms, others, atoms_c)


            new_children = [GrammaticalExpression(atom, func=lambda *args: atom) for atom in atoms] + others
            return GrammaticalExpression(expr.rule_name, expr.func, children=new_children)

        # Recurse
        if (expr.rule_name != RuleNames.OR) or (
            not [child for child in children if child.is_atom()]
        ):
            return GrammaticalExpression(
                node=expr.rule_name,
                children=[
                    sum_complement(GrammaticalExpression(child), uni) for child in children
                ],
            )
        
def array_to_dnf(arr: np.ndarray, uni:Universe, complement=False) -> GrammaticalExpression:
    """
    Creates a Disjunctive Normal Form (Sum of Products) GrammaticalExpression of nonzero array entries.

    The following is an illustration
        [[1,1,1],
        [1,1,1]]
        =>
        (+ (
            * Q_1 f_1)
            (* Q_1 f_2)
            (* Q_1 f_3)
            (* Q_2 f_1)
            (* Q_2 f_2)
            (* Q_2 f_3)
            )
    """
    axes = uni.axes_from_referents().keys()
    axes_values = uni.axes_from_referents().values()
    
    # Special case: 0
    if np.count_nonzero(arr) == 0:
        return GrammaticalExpression("0", lambda *args: False)
    if np.count_nonzero(arr) == (np.prod(axes_values)):
        return GrammaticalExpression("1", lambda *args: True)

    if not complement:
        argw = np.argwhere(arr)
        products = [
            GrammaticalExpression(
                rule_name = RuleNames.AND,
                func = lambda *args: all(args),
                children=[

                    GrammaticalExpression(axes_values[axis_value_index][axis_value], lambda *args: axes_values[axis_value_index][axis_value])
                    for axis_value_index, axis_value in enumerate(pair)
                ],
            )
            for pair in argw
        ]
        return GrammaticalExpression(rule_name=RuleNames.OR, children=products)

    else:
        argw = np.argwhere(arr == 0)
        products = [
            GrammaticalExpression(
                rule_name=RuleNames.AND,
                func = lambda *args: all(args),
                children=[
                    GrammaticalExpression(axes_values[axis_value_index][axis_value], lambda *args: axes_values[axis_value_index][axis_value])
                    for axis_value_index, axis_value in enumerate(pair)
                ],
            )
            for pair in argw
        ]
        negated_products = [
            GrammaticalExpression(
                RuleNames.NOT,
                lambda x: not x,
                children=[product],
            )
            for product in products
        ]
        return GrammaticalExpression(RuleNames.OR, lambda *args:any(args), children=products)

def minimum_lot_description(meaning: Meaning, minimization_funcs, uni:Universe) -> list:
    """Runs a heuristic to estimate the shortest length description of modal meanings in a language of thought.

    This is useful for measuring the complexity of modals, and the langauges containing them.

    Args:
        meanings: a list of the ModalMeanings

    Returns:
        descriptions: a list of descriptions of each meaning in the lot
    """
    # TODO: figure out how to use Pool() to play nice with Python objects
    # arrs = [meaning.to_array() for meaning in meanings]
    # r = [str(self.__joint_heuristic(arr)) for arr in tqdm(arrs)]
    arr = meaning.to_array()
    r = str(joint_heuristic(arr, minimization_funcs, True, uni))
    return r

def heuristic(expr: GrammaticalExpression, simple_operations:list, relative_operations:list, uni:Universe) -> GrammaticalExpression:
        """A breadth first tree search of possible boolean formula reductions.

        Args:
            expr: an GrammaticalExpression representing the DNF expression to reduce

            simple_operations: a list of functions from GrammaticalExpression to GrammaticalExpression

            relative_operations: a list of functions from GrammaticalExpression to GrammaticalExpression, parametrized by an atom.

        Returns:
            shortest: the GrammaticalExpression representing the shortest expression found.
        """

        to_visit = [expr]
        shortest = expr
        it = 0

        atoms = (
            [GrammaticalExpression("0", lambda *args: False), GrammaticalExpression("1" , lambda *args: False)]
            + [GrammaticalExpression(x, lambda *args: x) for x in uni.referents]
            + [GrammaticalExpression(x, lambda *args: x) for x in uni.flavors]
        )

        while to_visit:
            if it == HARD_HEURISTIC_CEILING:
                 break
            next = to_visit.pop(0) #Pop the first element off the list, FIFO 

            children = [operation(next) for operation in simple_operations]
            children.extend(
                operation(next, atom)
                for operation in relative_operations
                for atom in atoms
            )

            to_visit.extend([child for child in children if child != next])
            it += 1

        return shortest

def joint_heuristic(arr: np.ndarray, minimization_funcs, contains_negation:bool, uni:Universe) -> GrammaticalExpression:
        """
        Calls the boolean expression minimization heuristic twice, once
        to count 0s and once to count 1s. Returns the shorter result.

        Args:
            arr: a numpy array representing the meaning points a modal can express.
            minimization
        Returns:
            result: the GrammaticalExpression representing the shortest lot description
        """
        e = array_to_dnf(arr)
        simple_operations = [
            identity_and,
            identity_or,
            #self.__flavor_cover,
            #self.__force_cover,
        ]
        for func in minimization_funcs:
            simple_operations.append(func)
        
        relative_operations = [distr_or_over_and]

        if contains_negation:
            e_c = array_to_dnf(arr, complement=True)
            simple_operations.append(lambda x: sum_complement(x, uni))
            results = [
                heuristic(e, simple_operations, relative_operations),
                heuristic(
                    e_c, simple_operations, relative_operations, complement=True
                ),
            ]
            complexities = [expression_length(r) for r in results]

            result = results[np.argmin(complexities)]

        else:
            result = heuristic(e, simple_operations, relative_operations)

        return result
