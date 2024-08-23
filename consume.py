#!/usr/bin/env python
import logging
import pika

RETRY_DELAY_DURATIONS_IN_MILLISECONDS = [
    5000, # 5s
    2 * 60 * 1000, # 2min
    30 * 60 * 1000, # 30min
    6 * 60 * 60 * 1000, # 6h
    2 * 24 * 60 * 60 * 1000 # 2d
]

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    # level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

green = "\x1b[32;20m"
blue = "\x1b[34;20m"
yellow = "\x1b[33;20m"
red = "\x1b[31;20m"
reset = "\x1b[0m"

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

logger.info('Consumer started. Waiting for messages. To exit press CTRL+C')

def my_callback(channel, method, properties, body):
    logger.info(f"{green}<< my-queue: {method.routing_key}:{body}{reset}")
    logger.info(f"             {properties}")
    # channel.basic_ack(delivery_tag=method_frame.delivery_tag)
    # channel.basic_nack(requeue=False)
    logger.info(f"          Error Simulation - REJECTING MESSAGE")
    channel.basic_reject(method.delivery_tag, requeue=False)

def my_quorum_callback(channel, method, properties, body):
    logger.info(f"{blue}<< my-quorum-queue: {method.routing_key}:{body}{reset}")
    logger.info(f"             {properties}")
    # channel.basic_ack(delivery_tag=method_frame.delivery_tag)
    # channel.basic_nack(requeue=False)
    logger.info(f"          Error Simulation - REJECTING MESSAGE, but re-queue it")
    channel.basic_reject(method.delivery_tag, requeue=True)

def error_callback(channel, method, properties, body):
    logger.info(f"{yellow}<< error-queue: {method.routing_key}:{body}{reset}")
    logger.info(f"                reason: {properties.headers['x-first-death-reason']}")
    logger.info(f"                exchange: {properties.headers['x-first-death-exchange']} / queue: {properties.headers['x-first-death-queue']}")
    logger.info(f"                {properties}")

    reject_count = next((death for death in properties.headers['x-death'] if death['reason'] in ['rejected', 'delivery_limit']))['count']

    if reject_count < 1 or reject_count > len(RETRY_DELAY_DURATIONS_IN_MILLISECONDS):
        logger.error(f"Re-queue limit exceeeded, too many rejections: {reject_count}. Dropping message.")
        channel.basic_reject(method.delivery_tag, requeue=False)
        return

    properties.headers['x-delay'] = RETRY_DELAY_DURATIONS_IN_MILLISECONDS[reject_count - 1]
    logger.info(f"   sending message to retry-delay-exchange with a delay of {properties.headers['x-delay']}ms")
    channel.basic_publish(exchange='retry-delay-exchange',
                          routing_key='delay-message',
                          body=body,
                          properties=properties)
    channel.basic_ack(method.delivery_tag)

def delay_callback(channel, method, properties, body):
    logger.info(f"{red}<< delay-queue: {method.routing_key}:{body}{reset}")
    logger.info(f"                reason: {properties.headers['x-first-death-reason']}")
    logger.info(f"                exchange: {properties.headers['x-first-death-exchange']} / queue: {properties.headers['x-first-death-queue']}")
    logger.info(f"                {properties}")

    logger.info(f"   re-queuing message to {properties.headers['x-first-death-exchange']} with the routing key {properties.headers['x-death'][0]['routing-keys'][0]}")
    channel.basic_publish(exchange=properties.headers['x-first-death-exchange'],
                          routing_key=properties.headers['x-death'][0]['routing-keys'][0],
                          body=body,
                          properties=properties)
    channel.basic_ack(method.delivery_tag)

channel.basic_consume(queue='my-queue', on_message_callback=my_callback, auto_ack=False)
channel.basic_consume(queue='my-quorum-queue', on_message_callback=my_quorum_callback, auto_ack=False)
channel.basic_consume(queue='retry-error-queue', on_message_callback=error_callback, auto_ack=False)
channel.basic_consume(queue='retry-delay-queue', on_message_callback=delay_callback, auto_ack=False)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
connection.close()
