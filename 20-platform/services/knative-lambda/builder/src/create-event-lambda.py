#!/usr/bin/env python3
# Create a CloudEvent named network.notifi.lambda.build
# it shall have thirdPartyId and parserId as payload
import json
import uuid
import datetime
import pika

# Create the CloudEvent
def create_cloud_event(third_party_id, parser_id):
    event = {
        # Required CloudEvent attributes
        "specversion": "1.0",
        "id": str(uuid.uuid4()),
        "source": f"network.notifi.parsers.{third_party_id}.{parser_id}",
        "type": "network.notifi.lambda.parser.start",
        "time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        
        # Custom data payload
        "data": {
            "contextId": "soon to be encrypted ctxId",
            "params": {},
        },
        
        # Optional attributes
        "datacontenttype": "application/json"
    }
    
    return event

# Publish the CloudEvent to RabbitMQ
def publish_to_rabbitmq(cloud_event, rabbitmq_url="amqp://notifi:notifi@localhost:5672/"):
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    
    # Declare exchange and queue
    exchange_name = "cloud-events"
    queue_name = "lambda-service-events"
    routing_key = "network.notifi.lambda.parser.start"
    
    # channel.exchange_declare(exchange=exchange_name, exchange_type="topic", durable=True)
    # channel.queue_declare(queue=queue_name, durable=True)
    # channel.queue_bind(queue=queue_name, exchange=exchange_name, routing_key=routing_key)
    
    # Publish the event
    channel.basic_publish(
        exchange=exchange_name,
        routing_key=routing_key,
        body=json.dumps(cloud_event),
        properties=pika.BasicProperties(
            content_type="application/cloudevents+json",
            delivery_mode=2  # make message persistent
        )
    )
    
    connection.close()
    print(f"Published CloudEvent: {cloud_event['id']}")

# Usage example
if __name__ == "__main__":
    # Test test-lambda-builder-123.index-0001
    third_party_id = "test-lambda-builder-123"
    parser_id = "index-0001"
    event = create_cloud_event(third_party_id, parser_id)
    publish_to_rabbitmq(event)

    # # Test test-lambda-builder-456.index-0002
    # third_party_id = "test-lambda-builder-456"
    # parser_id = "index-0002"
    # event = create_cloud_event(third_party_id, parser_id)
    # publish_to_rabbitmq(event)