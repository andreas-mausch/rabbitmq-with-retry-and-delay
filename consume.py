#!/usr/bin/env python
import logging
import pika

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    # level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue
binding_keys = '*'

print(' [*] Waiting for logs. To exit press CTRL+C')

def my_callback(channel, method, properties, body):
    logger.info(f"<< my-queue: {method.routing_key}:{body}")
    # channel.basic_ack(delivery_tag=method_frame.delivery_tag)
    # channel.basic_nack(requeue=False)
    channel.basic_reject(method.delivery_tag, requeue=False)

def error_callback(channel, method, properties, body):
    logger.info(f"<< error-queue: {method.routing_key}:{body}")

channel.basic_consume(queue='my-queue', on_message_callback=my_callback, auto_ack=False)
channel.basic_consume(queue='error-queue', on_message_callback=error_callback, auto_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
connection.close()
