#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.basic_publish(exchange='my-classic-exchange',
                      routing_key='hello',
                      body='Hello World!')
print(" >> Sent new message 'Hello World!' to my-classic-exchange")

connection.close()
