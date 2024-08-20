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

channel.exchange_declare(exchange='my-exchange', exchange_type='topic')
channel.queue_declare(queue='my-queue', arguments={"x-dead-letter-exchange" : "retry-error-exchange"})
channel.queue_bind(exchange='my-exchange',
                   queue='my-queue',
                   routing_key='*')

channel.basic_publish(exchange='my-exchange',
                      routing_key='hello',
                      body='Hello World!')
print(" >> Sent new message 'Hello World!' to my-exchange")

connection.close()
