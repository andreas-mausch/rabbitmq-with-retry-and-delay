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
    logger.info(f"                reason: {properties.headers['x-first-death-reason']}")
    logger.info(f"                exchange: {properties.headers['x-first-death-exchange']} / queue: {properties.headers['x-first-death-queue']}")
    logger.info(f"                {properties.headers['x-death']}")

    reject_count = next((death for death in properties.headers['x-death'] if death['reason'] == 'rejected'))['count']

    if reject_count < 0 or reject_count >= 5:
        logger.info(f"XX re-queue limit exceeeded, too many rejections: {reject_count}. Dropping message.")
        channel.basic_reject(method.delivery_tag, requeue=False)
        return

    channel.basic_publish(exchange=properties.headers['x-first-death-exchange'],
                          routing_key=properties.headers['x-death'][0]['routing-keys'][0],
                          body=body,
                          properties=properties)
    channel.basic_ack(method.delivery_tag)

channel.basic_consume(queue='my-queue', on_message_callback=my_callback, auto_ack=False)
channel.basic_consume(queue='error-queue', on_message_callback=error_callback, auto_ack=False)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
connection.close()
