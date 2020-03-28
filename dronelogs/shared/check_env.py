from os import environ

def check_env():
    if 'AWS_ACCESS_KEY_ID' not in environ:
        raise ValueError('Error: AWS_ACCESS_KEY_ID is not defined as enviroment variable')
    if 'AWS_SECRET_ACCESS_KEY' not in environ:
        raise ValueError('Error: AWS_SECRET_ACCESS_KEY is not defined as enviroment variable')
    if 'AWS_DEFAULT_REGION' not in environ:
        raise ValueError('Error: AWS_DEFAULT_REGION is not defined as enviroment variable')
    if 'PIPILE_NAME' not in environ:
        raise ValueError('Error: PIPILE_NAME is not defined as enviroment variable')
