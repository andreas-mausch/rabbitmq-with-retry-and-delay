#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='error-exchange', exchange_type='topic')
channel.queue_declare(queue='error-queue')
channel.queue_bind(exchange='error-exchange',
                   queue='error-queue',
                   routing_key='*')

channel.exchange_declare(exchange='my-exchange', exchange_type='topic')
channel.queue_declare(queue='my-queue', arguments={"x-dead-letter-exchange" : "error-exchange"})
channel.queue_bind(exchange='my-exchange',
                   queue='my-queue',
                   routing_key='*')

channel.basic_publish(exchange='my-exchange',
                      routing_key='hello',
                      body='Hello World!')
print(" >> Sent 'Hello World!'")
connection.close()
