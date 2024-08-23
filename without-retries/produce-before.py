#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='my-exchange', exchange_type='topic')
channel.queue_declare(queue='my-queue')
channel.queue_bind(exchange='my-exchange',
                   queue='my-queue',
                   routing_key='*')

channel.basic_publish(exchange='my-exchange',
                      routing_key='hello',
                      body='Hello World!')
print(" >> Sent new message 'Hello World!' to my-exchange")

connection.close()
