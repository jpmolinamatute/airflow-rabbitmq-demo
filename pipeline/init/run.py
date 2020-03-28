#!/usr/bin/env python

from os import environ
from datetime import datetime
import pika
from shared.rabbitmq_conn import get_rabbitmq_conn
from shared.db_conn import get_db_conn
from shared.get_uuid_from_string import get_uuid



STEP_NAME = 'init'

def callback(ch, method, properties, body):
    uuid = get_uuid(body.decode("utf-8"))
    if isinstance(uuid, str):
        print(" [x] Received %r" % uuid)
        connection = get_db_conn()

        if connection:
            tablename = environ['PIPILE_NAME']
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {tablename} WHERE uuid = '{uuid}' LIMIT 1;")
            if cursor.rowcount == 0:
                dt = datetime.now()
                cursor.execute(f"INSERT INTO {tablename} (uuid, progress, startedat) VALUES (%s, %s, %s)", (uuid, '{}', dt))
                connection.commit()
                ch.queue_declare(queue='decrypt', durable=True)
                ch.basic_publish(
                    exchange=environ['PIPILE_NAME'],
                    routing_key="decrypt",
                    body=uuid,
                    properties=pika.BasicProperties(delivery_mode=2)
                )
            cursor.close()
            connection.close()
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print("Failed")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    else:
        print(f"Failed {body.decode('utf-8')}")
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
