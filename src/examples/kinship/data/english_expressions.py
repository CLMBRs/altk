english_expression_strings = {
    "grandmother": {"Paternal_Grandmother", "Maternal_Grandmother"},
    "grandfather": {"Paternal_Grandfather", "Maternal_Grandfather"},
    
    "mother": {"Mother"},
    "father": {"Father"},
    "sister": "*(my_(axy_and_bx(Ez_axz_and_bzy(child, parent), female)), .)",
    "brother": "*(my_(axy_and_bx(Ez_axz_and_bzy(child, parent), male)), .)",
    "daughter": "*(my_(axy_and_bx(child, female)), .)",
    "son": "*(my_(axy_and_bx(child, male)), .)",

    "grandchild": {
        "Son_of_Son",
        "Son_of_Daughter",
        "Daughter_of_Son",
        "Daughter_of_Daughter",
    },
    "grandson": {"Son_of_Son", "Son_of_Daughter"},
    "granddaughter": {"Daughter_of_Son", "Daughter_of_Daughter"},
    "parent": {"Mother", "Father"},
    "child": {
        "Daughter",
        "Son",
    },
    "sibling": {
        "Ego_Older_Sister",
        "Ego_Older_Brother",
        "Ego_Younger_Sister",
        "Ego_Younger_Brother",
    },
    "niece": {"Daughter_of_Ego_Older_Brother", "Daughter_of_Ego_Younger_Brother"},
    "nephew": {"Son_of_Ego_Older_Brother", "Son_of_Ego_Younger_Brother"},
    "uncle": {
        "Paternal_Older_Brother",
        "Paternal_Younger_Brother",
        "Maternal_Older_Brother",
        "Maternal_Younger_Brother",
    },
    "aunt": {
        "Paternal_Older_Sister",
        "Paternal_Younger_Sister",
        "Maternal_Older_Sister",
        "Maternal_Younger_Sister",
    },
    "cousin": {
        "Son_of_Ego_Older_Sister",
        "Daughter_of_Ego_Older_Sister",
        "Son_of_Ego_Younger_Sister",
        "Daughter_of_Ego_Younger_Sister",
    },
}
