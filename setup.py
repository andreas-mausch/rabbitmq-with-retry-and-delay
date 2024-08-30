#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='retry-dead-letter-exchange', exchange_type='topic')
channel.queue_declare(queue='retry-dead-letter-queue')
channel.queue_bind(exchange='retry-dead-letter-exchange',
                   queue='retry-dead-letter-queue',
                   routing_key='*')

channel.exchange_declare(exchange='retry-error-exchange', exchange_type='topic')
channel.queue_declare(queue='retry-error-queue', arguments={"x-dead-letter-exchange" : "retry-dead-letter-exchange"})
channel.queue_bind(exchange='retry-error-exchange',
                   queue='retry-error-queue',
                   routing_key='*')

channel.exchange_declare(exchange='retry-delay-exchange', exchange_type='x-delayed-message', arguments={'x-delayed-type': 'topic'})
channel.queue_declare(queue='retry-delay-queue', arguments={"x-dead-letter-exchange" : "retry-dead-letter-exchange"})
channel.queue_bind(exchange='retry-delay-exchange',
                   queue='retry-delay-queue',
                   routing_key='*')

channel.exchange_declare(exchange='my-classic-exchange', exchange_type='topic')
channel.queue_declare(queue='my-classic-queue', arguments={"x-dead-letter-exchange" : "retry-error-exchange"})
channel.queue_bind(exchange='my-classic-exchange',
                   queue='my-classic-queue',
                   routing_key='*')

channel.exchange_declare(exchange='my-quorum-exchange', exchange_type='topic')
channel.queue_declare(queue='my-quorum-queue', durable=True, arguments={"x-dead-letter-exchange" : "retry-error-exchange", "x-queue-type" : "quorum", "x-delivery-limit": 3})
channel.queue_bind(exchange='my-quorum-exchange',
                   queue='my-quorum-queue',
                   routing_key='*')

connection.close()
