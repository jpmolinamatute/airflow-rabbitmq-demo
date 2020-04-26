#!/usr/bin/env python

from os import environ, rename
from datetime import datetime
# import pika
from pipeline.shared.rabbitmq_conn import get_rabbitmq_conn
from dronelogs.shared.get_uuid_from_string import get_uuid, get_file_from_key
from dronelogs.shared.s3_upload_download import download_file, upload_file
from dronelogs.shared.db_conn import get_db_conn

STEP_NAME = 'decrypt'

def decrypt(single_file, uuid):
    print(f'Decrypting {single_file}')
    rename(single_file, f'./{uuid}.csv')
    return True

def check_dependency(cursor, uuid):
    tablename = environ['PIPILE_NAME']
    query = f"SELECT * FROM {tablename} "
    query += "WHERE uuid = %s "
    query += "AND ( "
    query += f"NOT decrypt_status "
    query += "OR decrypt_status IS NULL);"
    cursor.execute(query, (uuid,))
    return cursor.fetchone()

def update_row(cursor, uuid, success=False):
    tablename = environ['PIPILE_NAME']
    sql_str = f"UPDATE {tablename} "
    sql_str += "SET decrypt_status = %s, completed_at = %s "
    sql_str += "WHERE uuid = %s;"
    values = (success, datetime.now(), uuid)
    cursor.execute(sql_str, values)

def callback(ch, method, properties, body):
    file_name = body.decode("utf-8")
    uuid = get_uuid(file_name)
    print(f"Step 1: {file_name}")
    if isinstance(uuid, str):
        print(f"Step 2: {file_name}")
        connection = get_db_conn()
        if connection:
            print(f"Step 3: {file_name}")
            cursor = connection.cursor()
            dependency_met = check_dependency(cursor, uuid)
            print(dependency_met)
            if dependency_met is None:
                print(f"Step 4: {file_name}")
                success = True
                localfile = get_file_from_key(file_name)
                if not download_file(environ['AWS_RAW_S3_BUCKET'], file_name, f'./{localfile}') or\
                not decrypt(f'./{localfile}', uuid) or\
                not upload_file(environ['AWS_CLEAN_S3_BUCKET'], f'juanpa-copy/{uuid}.csv', f'./{uuid}.csv'):
                    success = False
                update_row(cursor, uuid, success)
                connection.commit()
                # ch.queue_declare(queue='decrypt', durable=True)
                # ch.basic_publish(
                #     exchange=environ['PIPILE_NAME'],
                #     routing_key="decrypt",
                #     body=uuid,
                #     properties=pika.BasicProperties(delivery_mode=2)
                # )
            cursor.close()
            connection.close()
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
