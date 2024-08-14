# Approach

[https://devcorner.digitalpress.blog/rabbitmq-retries-the-new-full-story/](https://devcorner.digitalpress.blog/rabbitmq-retries-the-new-full-story/)

# Start RabbitMQ with Delay Plugin

```bash
docker run -it --rm -p 5672:5672 -p 15672:15672 -e RABBITMQ_DEFAULT_USER=guest -e RABBITMQ_DEFAULT_PASS=guest heidiks/rabbitmq-delayed-message-exchange:3.13.3-management
```

Management UI:
http://localhost:15672

# Python dependencies

You need pika. Either install it via virtual env or like this:

```bash
sudo pacman -S python-pika
```

# Why do we need a delay exchange?

In order for `x-delay` to work, we need an exchange of the type `x-delayed-message`.
So we have the choice of either making our normal exchanges all of this type, or
rather have only a single place for this exception.

# TODOs

- Use a quorum queue. Can we skip the `reject_count` then?
- Increasing delay
