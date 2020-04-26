#!/usr/bin/env python

from os import environ
from datetime import datetime
import pika
from pipeline.shared.rabbitmq_conn import get_rabbitmq_conn
from dronelogs.shared.db_conn import get_db_conn
from dronelogs.shared.get_uuid_from_string import get_uuid

STEP_NAME = 'init'

def check_dependency(cursor, uuid):
    tablename = environ['PIPILE_NAME']
    query = f"SELECT * FROM {tablename} "
    query += "WHERE uuid = %s;"
    cursor.execute(query, (uuid,))
    return cursor.fetchone()

def insert_row(cursor, uuid, file_name):
    tablename = environ['PIPILE_NAME']
    values = (uuid, file_name, datetime.now())
    sql_str = f"INSERT INTO {tablename} "
    sql_str += "(uuid, file_name, started_at) VALUES (%s, %s, %s)"
    cursor.execute(sql_str, values)

def callback(ch, method, properties, body):
    file_name = body.decode("utf-8")
    uuid = get_uuid(file_name)
    if isinstance(uuid, str):
        connection = get_db_conn()
        if connection:
            cursor = connection.cursor()
            dependency_met = check_dependency(cursor, uuid)
            if dependency_met is None:
                insert_row(cursor, uuid, file_name)
                connection.commit()
            cursor.close()
            connection.close()
            ch.queue_declare(queue='decrypt', durable=True)
            ch.basic_publish(
                exchange=environ['PIPILE_NAME'],
                routing_key="decrypt",
                body=file_name,
                properties=pika.BasicProperties(delivery_mode=2)
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print("Failed")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    else:
        print(f"Failed {file_name}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def init():
    connection = get_rabbitmq_conn()
    channel = connection.channel()
    channel.exchange_declare(
        exchange=environ['PIPILE_NAME'],
        exchange_type='direct'
    )
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(
        exchange=environ['PIPILE_NAME'],
        queue=queue_name,
        routing_key=STEP_NAME
    )
    prefetch = int(environ['CONSUMER_PRE_FETCH'])
    channel.basic_qos(prefetch_count=prefetch)
    channel.basic_consume(
        queue=queue_name,
        auto_ack=False, # this is the default behaviour of acknowledgement,
        # we need to send it ourself and we do it through the last line of the callback function
        on_message_callback=callback
    )
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == "__main__":
    try:
        init()
    except KeyboardInterrupt:
        print('Bye!')
