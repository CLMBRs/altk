from ultk.language.grammar.grammar import GrammaticalExpression
from ultk.language.grammar.grammar import Meaning
from ultk.language.grammar.boolean import RuleNames
from ultk.language.semantics import Referent, Universe
import numpy as np
from itertools import product

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
    print("checking boolean cover of {} with axis values {}".format(expr, axis_values))
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
    elif expr.children != None and [child for child in expr.children]:
        children = [
            child
            if child.is_atom()
            else boolean_cover(child, axis_values=axis_values)
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
    print("Taking or identity of {}".format(expr))
    if expr.rule_name == RuleNames.OR and expr.contains_name("0"):
        children = [child for child in expr.children if not child.rule_name=="0"]
        if children == []:
            return GrammaticalExpression("0", func = lambda *args: False, children=None)
        elif len(children) == 1:
            return children[0]
        else:
            return GrammaticalExpression(expr.rule_name, expr.func, children=children)
    
    if expr.rule_name == RuleNames.OR and len(expr.children) == 1:
        print("Removing or from {}".format(expr))
        return expr.children[0]
    
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
    print("Taking and identity of {}".format(expr))
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
        print("Shortening atoms {} with others {} and atoms_c {}".format(atoms, others, atoms_c))

        if not atoms_c:
            # Allow flavor cover to handle
            return expr

        if len(atoms_c) < len(atoms):
            # if shortens expression, use new sum of wrapped atoms.
            atoms = [
                GrammaticalExpression(atom, func = return_atom_fn(atom), children=None
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
        print("taking sum complement of {}".format(expr))
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
                    atoms.append(child.rule_name)
                else:
                    others.append(sum_complement(child, uni))

            axes = uni.axes_from_referents()
            

            for axis_values in axes.values():
                if atoms and (set(atoms) <= set(axis_values)):
                    atoms_c = list(set(axis_values) - set(atoms))
                    return shorten_expression(expr, atoms, others, atoms_c)



            new_children = [GrammaticalExpression(atom, func=lambda *args: atom, children=None) for atom in atoms] + others
            return GrammaticalExpression(expr.rule_name, expr.func, children=new_children)

        # Recurse
        if (expr.rule_name != RuleNames.OR) or (
            not [child for child in children if child.is_atom()]
        ):
            return GrammaticalExpression(
                rule_name=expr.rule_name,
                func=expr.func,
                children=[
                    sum_complement(child, uni) for child in children
                ],
            )
        
def array_to_dnf(arr: np.ndarray, universe:Universe, complement=False) -> GrammaticalExpression:
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
    axes = universe.axes_from_referents().keys()
    axes_values = list(universe.axes_from_referents().values())
    
    # Special case: 0
    if np.count_nonzero(arr) == 0:
        return GrammaticalExpression("0", lambda *args: False, children=[])
    if np.count_nonzero(arr) == (arr.size):
        return GrammaticalExpression("1", lambda *args: True, children=[])

    if not complement:
        argw = np.argwhere(arr)
        products = [
            GrammaticalExpression(
                rule_name = RuleNames.AND,
                func = lambda *args: all(args),
                children=[

                    GrammaticalExpression(axes_values[axis_value_index][axis_value], lambda *args: axes_values[axis_value_index][axis_value], children=None)
                    for axis_value_index, axis_value in enumerate(pair)
                ],
            )
            for pair in argw
        ]
        output = GrammaticalExpression(RuleNames.OR, lambda *args:any(args), children=products)
        print("Returning non-complement:{}".format(output))
        return output

    else:
        argw = np.argwhere(arr == 0)
        products = [
            GrammaticalExpression(
                rule_name=RuleNames.AND,
                func = lambda *args: all(args),
                children=[
                    GrammaticalExpression(axes_values[axis_value_index][axis_value], lambda *args: axes_values[axis_value_index][axis_value], children=None)
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
        output = GrammaticalExpression(RuleNames.OR, lambda *args:any(args), children=negated_products)
        print("Returning complement:{}".format(output))
        return output

def minimum_lot_description(meaning: Meaning, universe:Universe, minimization_funcs:list = []) -> list:
    """Runs a heuristic to estimate the shortest length description of modal meanings in a language of thought.

    This is useful for measuring the complexity of modals, and the langauges containing them.

    Args:
        meanings: a list of the ModalMeanings
        universe: the Universe in which we want to minimize the LOT. 
        minimization_funcs: an optional list of additional minimization function

    Returns:
        descriptions: a list of descriptions of each meaning in the lot
    """
    # arrs = [meaning.to_array() for meaning in meanings]
    # r = [str(self.__joint_heuristic(arr)) for arr in tqdm(arrs)]
    arr = meaning.to_array()
    descriptions = str(joint_heuristic(arr, universe, minimization_funcs, True))
    return descriptions

def heuristic(expr: GrammaticalExpression, simple_operations:list, relative_operations:list, universe:Universe, complement=False) -> GrammaticalExpression:
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
        iterations = 0

        axes_values = [axis_value for axis in list(universe.axes_from_referents().values()) for axis_value in axis] 

        atoms = (
            [GrammaticalExpression("0", lambda *args: False, children=None), GrammaticalExpression("1" , lambda *args: False, children=None)]
            + [GrammaticalExpression(x, lambda *args: x, children=None) for x in axes_values]
        )

        while to_visit:
            if iterations == HARD_HEURISTIC_CEILING:
                 break
            next_expr = to_visit.pop(0) #Pop the first element off the list, FIFO 

            results = [operation(next_expr) for operation in simple_operations]
            results.extend(
                operation(next_expr, atom)
                for operation in relative_operations
                for atom in atoms
            )

            print("Iteration: {}, Adding results: [{}]".format(iterations, ":".join([str(r) for r in results])))

            to_visit.extend([result for result in results if result != next_expr])
            iterations += 1

            print("remaining to visit: [{}]".format(":".join([str(r) for r in to_visit])))

            if num_atoms(next_expr) < num_atoms(shortest):
                shortest = next_expr

            if complement and num_atoms(shortest) != 1:
                return negation(shortest)

        return shortest

def joint_heuristic(arr: np.ndarray, universe:Universe, minimization_funcs, contains_negation:bool) -> GrammaticalExpression:
        """
        Calls the boolean expression minimization heuristic twice, once
        to count 0s and once to count 1s. Returns the shorter result.

        Args:
            arr: a numpy array representing the meaning points a modal can express.
            minimization_funcs: a list of functions representing any additional functions that we want to BFS through in order to find the minimum LOT description.
            contains_negation: Whether the simplific
        Returns:
            result: the GrammaticalExpression representing the shortest lot description
        """
        expr = array_to_dnf(arr, universe)
        simple_operations = [
            identity_and,
            identity_or,
        ]
        axes = universe.axes_from_referents()
        for axis_name in axes:
            simple_operations.append(lambda expr: boolean_cover(expr, axes[axis_name])) #Append the cover check functions of all relevant axes in the dataset

        for func in minimization_funcs:
            simple_operations.append(func)
        
        relative_operations = [distr_or_over_and]

        if contains_negation:
            e_c = array_to_dnf(arr, universe, complement=True)
            simple_operations.append(lambda x: sum_complement(x, universe))

            print("Simple operations:{}".format(simple_operations))

            results = [
                heuristic(expr, simple_operations, relative_operations, universe, complement=False),
                heuristic(
                    e_c, simple_operations, relative_operations, universe, complement=True
                ),
            ]
            complexities = [expression_length(r) for r in results]

            result = results[np.argmin(complexities)]

        else:
            result = heuristic(expr, simple_operations, relative_operations, universe)

        return result

def generate_meanings(universe:Universe) -> list:
    """Generates all possible subsets of the meaning space, based on the pre-existing axes."""
    shape = tuple([len(features) for axis, features in universe.axes_from_referents()])
    arrs = [
        np.array(i).reshape(shape)
        for i in product([0, 1], repeat=len(universe.referents))
    ]
    arrs = arrs[1:]  # remove the empty array meaning to prevent div by 0
    meanings = [Meaning(universe.array_to_points(arr), universe) for arr in arrs]
    return meanings

def array_to_points(universe:Universe, np_array: np.ndarray) -> Meaning:
    """Converts a numpy array to a set of points, absed off the axes inherent in the Universe. 

    Args:
        a: numpy array representing a modal meaning.

    Raises:
        ValueError: if the meaning space doesn't match the array shape.axis 0 (rows) are forces, axis 1 (columns) are flavors.
    """
    axes = universe.axes_from_referents()
    
    if np_array.shape != tuple([len(features) for features in axes.values()]):
        raise ValueError(
            f"The size of the numpy array must match the size of the modal meaning space. a.shape={np_array.shape}, self.axes={universe.axes_from_referents()}"
        )
    
    properties = {}
    for pair in np.argwhere(np_array):
        for axis_index in range(len(pair)):
            properties[axes.keys()[axis_index]] = list(axes.values())

    return Meaning(referents=[Referent(name=("+".join(properties.values())), properties=properties)], universe=universe)       