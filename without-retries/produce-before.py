#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='my-classic-exchange', exchange_type='topic')
channel.queue_declare(queue='my-classic-queue')
channel.queue_bind(exchange='my-classic-exchange',
                   queue='my-classic-queue',
                   routing_key='*')

channel.basic_publish(exchange='my-classic-exchange',
                      routing_key='hello',
                      body='Hello World!')
print(" >> Sent new message 'Hello World!' to my-classic-exchange")

connection.close()
