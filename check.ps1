black buckshot_solver tests
autoflake -r --in-place buckshot_solver tests
isort buckshot_solver tests
mypy buckshot_solver tests
flake8 buckshot_solver tests
pylint buckshot_solver tests