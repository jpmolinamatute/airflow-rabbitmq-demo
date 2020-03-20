#! /usr/bin/env python

from os import environ
import pika


def check_env():
    if 'RABBITMQ_DEFAULT_USER' not in environ:
        raise ValueError('Error: RABBITMQ_DEFAULT_USER is not defined as enviroment variable')
    if 'RABBITMQ_DEFAULT_PASS' not in environ:
        raise ValueError('Error: RABBITMQ_DEFAULT_PASS is not defined as enviroment variable')
    if 'RABBITMQ_DEFAULT_VHOST' not in environ:
        raise ValueError('Error: RABBITMQ_DEFAULT_VHOST is not defined as enviroment variable')
    if 'RABBITMQ_HOST' not in environ:
        raise ValueError('Error: RABBITMQ_HOST is not defined as enviroment variable')



def get_rabbitmq_cred():
    return {
        'user': environ['RABBITMQ_DEFAULT_USER'],
        'pass': environ['RABBITMQ_DEFAULT_PASS'],
        'host': environ['RABBITMQ_HOST'],
        'vhost': environ['RABBITMQ_DEFAULT_VHOST']
    }


def get_rabbitmq_conn():
    check_env()
    cred = get_rabbitmq_cred()
    params = pika.ConnectionParameters(
        host=cred['host'],
        port="5672",
        credentials=pika.PlainCredentials(
            cred['user'],
            cred['pass']
        ),
        virtual_host=cred['vhost']
    )
    return pika.BlockingConnection(params)
