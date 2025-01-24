# recipes-coursework
A coursework on the topic "Web-based recipe management"

## Run test
To run tests run `docker compose run web python3 manage.py test`.

To get a test coverage run:

1) `docker compose run web python3 coverage run --source='.' manage.py test`; 
2) `docker compose run web python3 coverage report`.

To run migrations run
`docker compose run web python3 manage.py migrate`

The project can be accessed on http://127.0.0.1:8000/.
