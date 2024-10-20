# Splitwise
 Django app to manage everyday expenses

 ## Setup
 ### Database Setup
 Install [Postgres](https://ubuntu.com/server/docs/install-and-configure-postgresql)
 ### Set Secrets
 [Sample Secrets File](/splitwise/sample_secrets.py)
 ### Environment Setup
 ```shell
 conda create --name myenv python=3.11
 conda activate myenv
 conda install -r requirements.txt
```

## Run
```shell
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```