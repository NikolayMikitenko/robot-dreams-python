# Project for robot dreams course

## Files contents
* config.py - class for work with config  
* config.yaml - config for applications (example: out_of_stock)  
* main.py - main executed file  
* environment.yml - list or reqirued packages

## How to use application
### Read help
```
python main.py -h
python main.py --help
```

### Run application without arguments (use default value from config)
`python main.py`

### Run application with arguments (pass paramter for webservice request)
`python main.py -p "{'date': '2021-04-03'}"`




### Run application with arguments (other examples)
`python main.py -p "{'date': '2021-04-03'}" -a out_of_stock_app`
