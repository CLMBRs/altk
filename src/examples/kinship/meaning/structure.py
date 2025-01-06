"""Module containing individuals and relations of the kinship domain.

Rather than encoding all the features recursively into Referents, we'll just take advantage of the fact that grammars can be loaded from arbitrary python modules, and reference the data structures here, and keep Referents minimally to contain names.

"""

from typing import Callable

##############################################################################
# Structure class
##############################################################################


class Structure:
    """A general structure for representing a domain and interpretation."""

    def __init__(self, domain: set[str], interpretation: dict[str, Callable]):
        """
        Initialize the structure.

        Args:
            domain (set): The set of Referents.
            interpretation (dict): A mapping of terms to their interpretations.
        """
        self.domain = domain
        self.interpretation = interpretation

    def evaluate(self, term, *args):
        """Evaluate a term on the given arguments."""
        return self.interpretation[term](*args)


##############################################################################
# Define the features of the semantic domain
##############################################################################
domain = {
    name
    for name in [
        "Paternal_Grandfather",
        "Paternal_Grandmother",
        "Maternal_Grandfather",
        "Maternal_Grandmother",
        "Father",
        "Mother",
        *[
            f"Paternal_{'Older' if i < 2 else 'Younger'}_{'Brother' if i % 2 == 0 else 'Sister'}"
            for i in range(4)
        ],
        *[
            f"Maternal_{'Older' if i < 2 else 'Younger'}_{'Brother' if i % 2 == 0 else 'Sister'}"
            for i in range(4)
        ],
        # Ego and their four siblings
        "Ego",  # Explicitly include Ego
        *[
            f"Ego_{'Older' if i < 2 else 'Younger'}_{'Brother' if i % 2 == 0 else 'Sister'}"
            for i in range(4)
        ],
        "Son",
        "Daughter",
        *[
            f"{'Son_of_Son' if i == 0 else 'Daughter_of_Son' if i == 1 else 'Son_of_Daughter' if i == 2 else 'Daughter_of_Daughter'}"
            for i in range(4)
        ],
        # Add niblings
        *[
            f"{'Son_of_' + ('Ego_Older_Brother' if i == 0 else 'Ego_Older_Sister' if i == 1 else 'Ego_Younger_Brother' if i == 2 else 'Ego_Younger_Sister')}"
            for i in range(4)
        ],
        *[
            f"{'Daughter_of_' + ('Ego_Older_Brother' if i == 0 else 'Ego_Older_Sister' if i == 1 else 'Ego_Younger_Brother' if i == 2 else 'Ego_Younger_Sister')}"
            for i in range(4)
        ],
    ]
}

# Update auxiliary data structures
# Update auxiliary data structures
sex_data = {
    name: (
        "Grandfather" in name
        or "Father" in name
        or "Brother" in name
        or "Son" in name
        or name == "Ego"
    )
    and not ("Daughter_of" in name)
    for name in domain
}


# Age hierarchy: lists of individuals younger or older than each other
age_hierarchy = {
    # Ego's siblings
    "Ego_Older_Brother": ["Ego", "Ego_Younger_Brother", "Ego_Younger_Sister"],
    "Ego_Older_Sister": ["Ego", "Ego_Younger_Brother", "Ego_Younger_Sister"],
    "Ego": ["Ego_Younger_Brother", "Ego_Younger_Sister"],
    "Ego_Younger_Brother": [],
    "Ego_Younger_Sister": [],
    # Parents' siblings
    "Father": ["Paternal_Younger_Brother", "Paternal_Younger_Sister"],
    "Mother": ["Maternal_Younger_Brother", "Maternal_Younger_Sister"],
    "Paternal_Older_Brother": [
        "Father",
        "Paternal_Younger_Brother",
        "Paternal_Younger_Sister",
    ],
    "Paternal_Older_Sister": [
        "Father",
        "Paternal_Younger_Brother",
        "Paternal_Younger_Sister",
    ],
    "Paternal_Younger_Brother": [],
    "Paternal_Younger_Sister": [],
    "Maternal_Older_Brother": [
        "Mother",
        "Maternal_Younger_Brother",
        "Maternal_Younger_Sister",
    ],
    "Maternal_Older_Sister": [
        "Mother",
        "Maternal_Younger_Brother",
        "Maternal_Younger_Sister",
    ],
    "Maternal_Younger_Brother": [],
    "Maternal_Younger_Sister": [],
}

parent_child_data = {
    "Paternal_Grandfather": [
        "Father",
        "Paternal_Older_Brother",
        "Paternal_Younger_Brother",
        "Paternal_Older_Sister",
        "Paternal_Younger_Sister",
    ],
    "Paternal_Grandmother": [
        "Father",
        "Paternal_Older_Brother",
        "Paternal_Younger_Brother",
        "Paternal_Older_Sister",
        "Paternal_Younger_Sister",
    ],
    "Maternal_Grandfather": [
        "Mother",
        "Maternal_Older_Brother",
        "Maternal_Younger_Brother",
        "Maternal_Older_Sister",
        "Maternal_Younger_Sister",
    ],
    "Maternal_Grandmother": [
        "Mother",
        "Maternal_Older_Brother",
        "Maternal_Younger_Brother",
        "Maternal_Older_Sister",
        "Maternal_Younger_Sister",
    ],
    "Father": [
        "Ego",
        "Ego_Older_Brother",
        "Ego_Older_Sister",
        "Ego_Younger_Brother",
        "Ego_Younger_Sister",
    ],
    "Mother": [
        "Ego",
        "Ego_Older_Brother",
        "Ego_Older_Sister",
        "Ego_Younger_Brother",
        "Ego_Younger_Sister",
    ],
    "Ego": ["Son", "Daughter"],
    "Son": ["Son_of_Son", "Daughter_of_Son"],
    "Daughter": ["Daughter_of_Daughter", "Son_of_Daughter"],
    "Grandchild_Son_of_Son": [],
    "Grandchild_Daughter_of_Son": [],
    "Grandchild_Son_of_Daughter": [],
    "Grandchild_Daughter_of_Daughter": [],
    # Parent-child relationships for nieces/nephews
    "Ego_Older_Brother": ["Son_of_Ego_Older_Brother", "Daughter_of_Ego_Older_Brother"],
    "Ego_Older_Sister": ["Son_of_Ego_Older_Sister", "Daughter_of_Ego_Older_Sister"],
    "Ego_Younger_Brother": [
        "Son_of_Ego_Younger_Brother",
        "Daughter_of_Ego_Younger_Brother",
    ],
    "Ego_Younger_Sister": [
        "Son_of_Ego_Younger_Sister",
        "Daughter_of_Ego_Younger_Sister",
    ],
}


# Interpretation
# just in case lambdas cause issues
def is_male(r: str) -> bool:
    return sex_data[r]


def is_parent(p, c) -> bool:
    return c in parent_child_data.get(p, [])


def is_older(r1, r2) -> bool:
    return r2 in age_hierarchy.get(r1, [])

def is_sibling_excl(x, y) -> bool:
    # x and y must share at least one parent
    shared_parent = any(
        kinship_structure.evaluate("is_parent", z, x)
        and kinship_structure.evaluate("is_parent", z, y)
        for z in domain
    )
    # Exclude self
    return shared_parent and x != y


interpretation = {
    "is_male": is_male,
    "is_parent": is_parent,
    "is_older": is_older,
    "is_sibling_excl": is_sibling_excl,
}
interpretation.update(
    {
        individual: lambda x, individual=individual: individual == x
        for individual in domain
    }
)


##############################################################################
# Testing
##############################################################################
# TODO: use an actual testing framework
def test_structure(kinship_structure, domain, parent_child_data, sex_data):
    """
    Comprehensive test suite to verify the correctness of the kinship structure.

    Args:
        kinship_structure (Structure): The kinship structure.
        domain (dict): Dictionary of Referents in the domain.
        parent_child_data (dict): The parent-child relationship data.
        sex_data (dict): The gender data.
    """

    # print("=== Testing `is_male` Predicate ===")
    for referent in domain:
        expected = sex_data[referent]
        actual = kinship_structure.evaluate("is_male", referent)
        assert (
            actual == expected
        ), f"Failed `is_male` for {referent}: expected {expected}, got {actual}"
        # print(f"PASS: {referent} -> is_male = {actual}")

    # print("\n=== Testing `parent_of` Predicate ===")
    for parent in domain:
        for child in domain:
            expected = child in parent_child_data.get(parent, [])
            actual = kinship_structure.evaluate("is_parent", parent, child)
            assert (
                actual == expected
            ), f"Failed `is_parent` for {parent}, {child.name}: expected {expected}, got {actual}"
            # print(f"PASS: {parent} -> parent_of({child}) = {actual}")

    # print("\n=== Testing `is_older` Predicate ===")
    for r1 in domain:
        for r2 in domain:
            expected = r2 in age_hierarchy.get(r1, [])
            actual = kinship_structure.evaluate("is_older", r1, r2)
            assert (
                actual == expected
            ), f"Failed `is_older` for {r1}, {r2}: expected {expected}, got {actual}"
            # print(f"PASS: {r1} -> is_older({r2}) = {actual}")

    print("\nAll tests passed!")


##############################################################################
# Build
##############################################################################

# Create the structure
kinship_structure = Structure(
    domain=domain,
    interpretation=interpretation,
)

if __name__ == "__main__":

    # Run a minimal test 'suite'
    test_structure(kinship_structure, domain, parent_child_data, sex_data)
