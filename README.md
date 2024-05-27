# Shopping Cart  
A simple E-commerce website using Flask. Test

## Dependencies

1. Navigate into ```cd ./studie-shopping-cart```
2. Install python packages: ```python -m pip install -r requirements.txt```

## Run tests

1. Navigate into ```cd ./studie-shopping-cart```
2. Run tests in file: ```python -m unittest ./src/app/tests/{file_name.py}```

## Run Application

1. Navigate into ```cd ./studie-shopping-cart```
2. Run main: ````python -m ./src/app/__main__.py````

## Sample User ##
Sample credentials present in existing database:

- Username: ```test@test.de```
- Password: ```test```

# SQLite Migration Alembic
1. Migrationsskript erstellen: ``alembic revision --autogenerate -m "Initial migration"``
2. Migrationen anwenden: ``alembic upgrade head``

