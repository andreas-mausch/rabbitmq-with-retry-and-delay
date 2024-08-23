#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.basic_publish(exchange='my-quorum-exchange',
                      routing_key='hello',
                      body='Hello World!')
print(" >> Sent new message 'Hello World!' to my-quorum-exchange")

connection.close()
