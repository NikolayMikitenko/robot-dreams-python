import requests
import json
from requests.models import HTTPError
import config
import argparse
import pathlib
import os

#JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MzI3MTk2NDYsImlhdCI6MTYzMjcxOTM0NiwibmJmIjoxNjMyNzE5MzQ2LCJpZGVudGl0eSI6MX0.vZ027gsUm_kIcDyPcKz9fz-y2-cV094YY-gRYRylq4w

parser = argparse.ArgumentParser(description = "Application for load data from webservice.")
parser.add_argument("--app", "-a", help="Name of application for wich we load data from webservice.", default='out_of_stock_app', type=str)
parser.add_argument("--parameters", "-p", help="JSON with parameters for webservice call.", type=lambda x: dict(eval(x)))
parser.add_argument("--config_path", "-c", help="Path for application config.", type=pathlib.Path)
parser.add_argument("--timeout", "-t", help="Timeout for websrvice call.", type=int, default=10)
args = parser.parse_args()

default_config_path = pathlib.Path('config.yaml')
default_app_name = 'out_of_stock_app'

def main():
    config_path = get_config_path()
    app_name = get_app_name()
    app_config = load_config(app_name=app_name, config_path=config_path)
    validate_app_config(path=str(config_path), app=app_name, config=app_config)

    token = None
    if app_config.get('auth'):
        token = get_token(app_config)

    call_api(app=app_name, config=app_config, parameters=args.parameters, token=token)

def get_config_path():
    if args.config_path:
        return args.config_path
    else:
        return default_config_path

def get_app_name():
    if args.app:
        return args.app
    else:
        return default_app_name 
        
def load_config(app_name: str, config_path: pathlib.Path):
    try:
        return config.Config(config_path).get_app_config(app_name)
    except FileNotFoundError as e:
        e.strerror =  'Config file for app not found. ' + e.strerror
        raise e
    except KeyError as e: 
        raise KeyError(f'Can not find aplication: "{app_name}" in config file "{str(config_path)}".')

def validate_app_config(path : str, app: str, config: json):
    if not config.get('url'):
        raise Exception(f'Config for application "{app}" in file "{str(path)} do not contain url.')
    if not config.get('endpoint'):
        raise Exception(f'Config for application "{app}" in file "{str(path)} do not contain endpoint.') 
    if not config.get('data parameter'):
        raise Exception(f'Config for application "{app}" in file "{str(path)} do not contain data parameter.')        
    if config.get('auth'):        
        if not config['auth'].get('endpoint'):
            raise Exception(f'Config for application "{app}" in file "{str(path)} do not contain endpoint for authentification.')
        if not config['auth'].get('parameters'):
            raise Exception(f'Config for application "{app}" in file "{str(path)} do not contain parameters for authentification.')       
        if not config['auth'].get('type'):
            raise Exception(f'Config for application "{app}" in file "{str(path)} do not contain type for authentification.')     

def get_token(config):  
    if config['auth']['type'] == "JWT TOKEN":
        r = requests.post(url=config['url'] + config['auth']['endpoint'], headers = config['headers'], json=config['auth']['parameters'], timeout=args.timeout)
        if r.status_code == 200:
            if r.json().get('access_token'):
                return "JWT " + r.json()['access_token']
            else:
                raise Exception(f"Auth request do not return access_token.")
        else:
            raise Exception(f"Auth request return bad response state_code {str(r.status_code)} with message: {r.text}")
    else:
        return ""

def call_api(app: str, config: json, parameters: json, token: str):
    headers = config['headers']
    if token:
        headers['Authorization'] = token
    if not parameters:
        parameters = config['parameters']
    try:
        r = requests.get(url=config['url'] + config['endpoint'], headers = headers, json=parameters, timeout=args.timeout)
        if r.status_code == 200:
            if len(r.json()) > 0:
                save_to_file(app=app, config=config, parameters=parameters, data=r.json())
            else:
                print(f"[ERROR] Request to url: {config['url'] + config['endpoint']} with parameters: {parameters} return empty JSON answer")
        else:
            print(f"[ERROR] Request to url: {config['url'] + config['endpoint']} with parameters: {parameters} return bad response state_code {str(r.status_code)} with message: {r.text}")
    except Exception as e:
        print(f"[ERROR] Request to url: {config['url'] + config['endpoint']} with parameters: {config['parameters']} return Exception: {str(e)}")

def save_to_file(app: str, config: json, parameters: json, data: json):
    directory_path = os.path.join('.', 'data', app)
    os.makedirs(directory_path, exist_ok=True)
    directory_path = os.path.join(directory_path, parameters[config['data parameter']])
    os.makedirs(directory_path, exist_ok=True)
    file_path =os.path.join(directory_path, app + '.json')
    with open(file_path, 'w') as f:
        json.dump(data, f)

if __name__ == "__main__":
    main()