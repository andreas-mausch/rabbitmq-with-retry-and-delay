# Approach

[https://devcorner.digitalpress.blog/rabbitmq-retries-the-new-full-story/](https://devcorner.digitalpress.blog/rabbitmq-retries-the-new-full-story/)

# Start RabbitMQ with Delay Plugin

We use an exchange of type `x-delayed-message`, which requires the
[rabbitmq-delayed-message-exchange](https://github.com/rabbitmq/rabbitmq-delayed-message-exchange).

```bash
docker run -it --rm -p 5672:5672 -p 15672:15672 -e RABBITMQ_DEFAULT_USER=guest -e RABBITMQ_DEFAULT_PASS=guest heidiks/rabbitmq-delayed-message-exchange:3.13.3-management
```

The management UI will be available at:
[http://localhost:15672](http://localhost:15672)

# Python dependencies

You need pika. Either install it via virtual env or like this:

```bash
sudo pacman -S python-pika
```

# Run producer and consumer

```bash
# The producer sets up all exchanges and queues
./setup.py

# sends a single message and exists afterwards
./send-to-classic-queue.py
./send-to-quorum-queue.py

# The consumer will keep running and listens for any
# new messages on the queues
./consumer.py
```

# Run the old version without retries

Important: Start with a fresh RabbitMQ.
`setup.py` must not be invoked on that one.

```bash
cd ./without-retries
./produce-before.py
./consume-before.py
```

# Why do we need a delay exchange?

In order for `x-delay` to work, we need an exchange of the type `x-delayed-message`.
So we have the choice of either making our normal exchanges all of this type, or
rather have only a single place for this exception.
