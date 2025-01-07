# !/bin/sh

echo "python -m quantifiers.scripts.generate_expressions"
python -m quantifiers.scripts.generate_expressions

echo "python -m quantifiers.scripts.generate_natural"
python -m quantifiers.scripts.generate_natural

echo "python -m quantifiers.scripts.estimate_pareto"
python -m quantifiers.scripts.estimate_pareto

echo "python -m quantifiers.scripts.combine_data"
python -m quantifiers.scripts.combine_data

echo "python -m quantifiers.scripts.analyze"
python -m quantifiers.scripts.analyze

echo Done.