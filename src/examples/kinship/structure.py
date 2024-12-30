from ultk.language.semantics import Referent, Universe

##############################################################################
# Structure class
##############################################################################

class Structure:
    """A general structure for representing a domain and interpretation."""

    def __init__(self, domain, interpretation):
        """
        Initialize the structure.
        
        Args:
            domain (set): The set of Referents.
            interpretation (dict): A mapping of predicates to their interpretations.
        """
        self.domain = domain
        self.interpretation = interpretation

    def evaluate(self, predicate, *args):
        """Evaluate a predicate on the given arguments."""
        return self.interpretation[predicate](*args)

##############################################################################
# Define the features of the semantic domain
##############################################################################
domain = {name: Referent(name) for name in [
    "Paternal_Grandfather", "Paternal_Grandmother",
    "Maternal_Grandfather", "Maternal_Grandmother",
    "Father", "Mother",
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
    "Son", "Daughter",  # Replaced "Child_Son" and "Child_Daughter" with "Son" and "Daughter"
    *[f"Grandchild_{'Son_of_Son' if i == 0 else 'Daughter_of_Son' if i == 1 else 'Son_of_Daughter' if i == 2 else 'Daughter_of_Daughter'}" for i in range(4)],  # Added four grandchildren
    *[f"Niece_or_Nephew_{'Son_of_' + ('Ego_Older_Brother' if i == 0 else 'Ego_Older_Sister' if i == 1 else 'Ego_Younger_Brother' if i == 2 else 'Ego_Younger_Sister')}" for i in range(8)],  # Added 8 nieces/nephews
]}

# Update auxiliary data structures
sex_data = {
    name: "Brother" in name or "Father" in name or "Son" in name or "Grandfather" in name or name == "Ego"
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
    "Paternal_Older_Brother": ["Father"],
    "Paternal_Older_Sister": ["Father"],
    "Paternal_Younger_Brother": [],
    "Paternal_Younger_Sister": [],
    "Maternal_Older_Brother": ["Mother"],
    "Maternal_Older_Sister": ["Mother"],
    "Maternal_Younger_Brother": [],
    "Maternal_Younger_Sister": [],
}

parent_child_data = {
    "Paternal_Grandfather": ["Father"],
    "Paternal_Grandmother": ["Father"],
    "Maternal_Grandfather": ["Mother"],
    "Maternal_Grandmother": ["Mother"],
    "Father": [
        "Ego", "Ego_Older_Brother", "Ego_Older_Sister", "Ego_Younger_Brother", "Ego_Younger_Sister",
        "Son", "Daughter",  # Replaced "Child_Son" and "Child_Daughter" with "Son" and "Daughter"
    ],
    "Mother": [
        "Ego", "Ego_Older_Brother", "Ego_Older_Sister", "Ego_Younger_Brother", "Ego_Younger_Sister",
        "Son", "Daughter",  # Replaced "Child_Son" and "Child_Daughter" with "Son" and "Daughter"
    ],
    "Ego": ["Son", "Daughter"],  # Replaced "Child_Son" and "Child_Daughter" with "Son" and "Daughter"
    "Son": ["Grandchild_Son_of_Son"],  # Added corresponding grandchild
    "Daughter": ["Grandchild_Daughter_of_Daughter"],  # Added corresponding grandchild
    "Grandchild_Son_of_Son": [],
    "Grandchild_Daughter_of_Son": [],
    "Grandchild_Son_of_Daughter": [],
    "Grandchild_Daughter_of_Daughter": [],
    # Parent-child relationships for nieces/nephews
    "Ego_Older_Brother": ["Niece_or_Nephew_Son_of_Ego_Older_Brother", "Niece_or_Nephew_Daughter_of_Ego_Older_Brother"],
    "Ego_Older_Sister": ["Niece_or_Nephew_Son_of_Ego_Older_Sister", "Niece_or_Nephew_Daughter_of_Ego_Older_Sister"],
    "Ego_Younger_Brother": ["Niece_or_Nephew_Son_of_Ego_Younger_Brother", "Niece_or_Nephew_Daughter_of_Ego_Younger_Brother"],
    "Ego_Younger_Sister": ["Niece_or_Nephew_Son_of_Ego_Younger_Sister", "Niece_or_Nephew_Daughter_of_Ego_Younger_Sister"],
}


# Interpretation
interpretation = {
    "is_male": lambda r: sex_data[r.name],
    "parent_of": lambda p, c: c.name in parent_child_data.get(p.name, []),
    "is_older": lambda r1, r2: r2.name in age_hierarchy.get(r1.name, []),
}

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

    print("=== Testing `is_male` Predicate ===")
    for referent in domain.values():
        expected = sex_data[referent.name]
        actual = kinship_structure.evaluate("is_male", referent)
        assert actual == expected, f"Failed `is_male` for {referent.name}: expected {expected}, got {actual}"
        print(f"PASS: {referent.name} -> is_male = {actual}")

    print("\n=== Testing `parent_of` Predicate ===")
    for parent in domain.values():
        for child in domain.values():
            expected = child.name in parent_child_data.get(parent.name, [])
            actual = kinship_structure.evaluate("parent_of", parent, child)
            assert actual == expected, f"Failed `parent_of` for {parent.name}, {child.name}: expected {expected}, got {actual}"
            print(f"PASS: {parent.name} -> parent_of({child.name}) = {actual}")

    print("\n=== Testing `is_older` Predicate ===")
    for r1 in domain.values():
        for r2 in domain.values():
            expected = r2.name in age_hierarchy.get(r1.name, [])
            actual = kinship_structure.evaluate("is_older", r1, r2)
            assert actual == expected, f"Failed `is_older` for {r1.name}, {r2.name}: expected {expected}, got {actual}"
            print(f"PASS: {r1.name} -> is_older({r2.name}) = {actual}")


    print("\nAll tests passed!")


##############################################################################
# Build
##############################################################################

# Create the structure
kinship_structure = Structure(
    domain=set(domain.values()), 
    interpretation=interpretation,
)

# Run the updated test suite
test_structure(kinship_structure, domain, parent_child_data, sex_data)

universe = Universe(tuple(kinship_structure.domain))
