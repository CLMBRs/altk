from ultk.language.grammar.grammar import GrammaticalExpression
from ultk.language.grammar.boolean import RuleNames

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
    """Helper function. Returns true if the GrammaticalExpression represents an atom, or has an AND as root."""
    
    return expr.is_atom or (expr.rule_name == RuleNames.AND and len(expr.children) > 0) #Not sure if we want that secondary check here

def boolean_cover(expr: GrammaticalExpression) -> GrammaticalExpression:
    """
    Replace the sum of all atoms with multiplicative identity.
    If $n=$ num_flavors, and $f_i$ is the $i$-th flavor,

        $\sum_{i=1}^{n}(f_i) = 1$
    """

def distribute_and(expr: GrammaticalExpression) -> GrammaticalExpression:
    """(p and q) or (p and s) -> p and (q or s)"""
    if expr.rule_name != RuleNames.OR:
         return expr
    
    factored_terms = []
    remaining_terms = []
    for child in expr.children:
         if is_product_or_singleton(child):
              factored_terms += [gc for gc in child if gc != ]

##########################################################################
# Addition
#
# At least binary branching. Will have at most the number of terms in
# the DNF of the array representation.
##########################################################################
def identity_and(expr: GrammaticalExpression) -> GrammaticalExpression:
    """
    Applies additive identity law.
        (+ a b ... 0 ... c) => (+ a b c)
        (+ a 0) => (a)
        (+ 0) => (0)
    """
    if expr.rule_name == RuleNames.AND and expr.contains_name("0"):
        children = [child for child in expr.children if not child.full_name=="1"]
        if children == []:
            return GrammaticalExpression("0")
        else:
            return GrammaticalExpression(node=expr.rule_name, children=children)
    if [child for child in expr.children()]:
        return GrammaticalExpression(
            node=expr.rule_name,
            children=[
                # child if isinstance(child, str)
                identity_and(child)
                for child in expr.children()
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

def identity_or(expr: GrammaticalExpression) -> GrammaticalExpression:
    if expr.rule_name == RuleNames.OR and expr.contains_name("1"):
        children = [child for child in expr.children if not child.full_name=="1"]
        if children == []:
                return GrammaticalExpression("1")
        elif len(children) == 1:
                return GrammaticalExpression(children[0])
        else:
                return GrammaticalExpression(node=expr.rule_name, children=children)
        
    # Recursively iterate through all children and find the additive identity of all of them
    if [child for child in expr.children()]:
        return GrammaticalExpression(
            node=expr.rule_name,
            children=[
                # child if isinstance(child, str)
                identity_or(child)
                for child in expr.children()
            ],
        )
    return expr
            
#################################################################
# Distributivity
#################################################################

def __distr_m_over_a(expr: GrammaticalExpression, factor: GrammaticalExpression) -> GrammaticalExpression:
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
        if child.is_product_or_singleton():
            if factor in child.children:
                factored_terms += [gc for gc in child if gc != factor]
                continue
        remaining_terms.append(child)

    if len(factored_terms) < 2:
        return expr

    factors_tree = GrammaticalExpression(rule_name=RuleNames.OR, children=factored_terms)
    factored_tree = GrammaticalExpression(
        rule_name=RuleNames.AND, children=[factor, factors_tree]
    )
    if remaining_terms:
        children = [factored_tree] + remaining_terms
        return GrammaticalExpression(rule_name=RuleNames.OR, children=children)
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
    return GrammaticalExpression(RuleNames.NOT, children=[expr])

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
                GrammaticalExpression(atom) if not isinstance(atom, GrammaticalExpression) else atom
                for atom in atoms_c
            ]
            comp = GrammaticalExpression(
                full_name=RuleNames.NOT,
                children=[GrammaticalExpression(full_name=RuleNames.OR, children=atoms)],
            )
            new_children = [comp] + others

            return GrammaticalExpression(rule_name=expr.rule_name, children=new_children)
        
        return expr

def sum_complement(expr: GrammaticalExpression) -> GrammaticalExpression:
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

            if atoms and (set(atoms) <= set(self.flavors)):
                atoms_c = list(set(self.flavors) - set(atoms))
                return shorten_expression(expr, atoms, others, atoms_c)
            
            if atoms and (set(atoms) <= set(self.forces)):
                atoms_c = list(set(self.forces) - set(atoms))
                return self.__shorten_expression(ET, atoms, others, atoms_c)

            new_children = [GrammaticalExpression(atom) for atom in atoms] + others
            return GrammaticalExpression(rule_name=expr.rule_name, children=new_children)

        # Recurse
        if (expr.rule_name != RuleNames.OR) or (
            not [child for child in children if child.is_atom()]
        ):
            return GrammaticalExpression(
                node=expr.rule_name,
                children=[
                    sum_complement(GrammaticalExpression(child)) for child in children
                ],
            )

def __heuristic(expr: GrammaticalExpression, simple_operations:list, relative_operations:list) -> GrammaticalExpression:
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
        hard_ceiling = 2500  # Best solutions are likely before 1000 iterations

        while to_visit:
            if it == hard_ceiling:
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

def __joint_heuristic(expr: GrammaticalExpression) ->GrammaticalExpression:


