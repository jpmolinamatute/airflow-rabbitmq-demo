# RabbitMQ #

Messages from consumer to RabbitMQ are known as delivery acknowledgements.
Messages from RabbitMQ publishers are a protocol extension called publisher confirms.

They are essential for reliable delivery both from publishers to RabbitMQ nodes and from RabbitMQ nodes to consumers. In other words, they are essential for data safety, for which applications are responsible as much as RabbitMQ nodes are.

## delivery acknowledgements ##

basic.ack is used for positive acknowledgements
basic.nack is used for negative acknowledgements (note: this is a RabbitMQ extension to AMQP 0-9-1)
basic.reject is used for negative acknowledgements but has one limitation compared to basic.nack
