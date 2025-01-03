# !/bin/sh

echo "python -m kinship.scripts.generate_expressions"
# python -m kinship.scripts.generate_expressions

echo "python -m kinship.scripts.add_natural_languages"
python -m kinship.scripts.add_natural_languages

echo "python -m kinship.scripts.measure_natural_languages"
python -m kinship.scripts.measure_natural_languages

echo "python -m kinship.scripts.estimate_pareto"
python -m kinship.scripts.estimate_pareto

echo "python -m kinship.scripts.combine_data"
python -m kinship.scripts.combine_data

echo "python -m kinship.scripts.analyze"
python -m kinship.scripts.analyze

echo Done.