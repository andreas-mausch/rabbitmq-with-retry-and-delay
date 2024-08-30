#!/usr/bin/env python
import logging
import pika

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    # level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

green = "\x1b[32;20m"
reset = "\x1b[0m"

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

logger.info('Consumer started. Waiting for messages. To exit press CTRL+C')

def my_classic_callback(channel, method, properties, body):
    logger.info(f"{green}<< my-classic-queue: {method.routing_key}:{body}{reset}")
    logger.info(f"             {properties}")
    logger.info(f"          Simulate an error and REJECT message")
    channel.basic_reject(method.delivery_tag, requeue=False)

channel.basic_consume(queue='my-classic-queue', on_message_callback=my_classic_callback, auto_ack=False)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
connection.close()
