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

## API Reference
[Install](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) to directly test APIs from VS Code


### User
 - [User Register](/test.rest?plain=1#L1)
 - [User Login](/test.rest?plain=1#L12)
 - [User Get](/test.rest?plain=1#L21)

### Expense
 - [Add Exact](/test.rest?plain=1#L29)
 - [Add Percent](/test.rest?plain=1#L69)
 - [Add Equal](/test.rest?plain=1#L109)

### Balance Sheet
 - [Balance Sheet Get](/test.rest?plain=1#L125)
 - [Balance Sheet Get All](/test.rest?plain=1#L134)
 - [Balance Sheet Get All Pdf](/test.rest?plain=1#L143)


## Upcoming Features

 - Per Expense owed and payed in balance sheet
 - Final balances owed and payed between users
