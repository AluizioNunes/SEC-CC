#!/bin/bash
# RabbitMQ initialization script for Portainer compatibility

# Wait for RabbitMQ to be ready
until rabbitmq-diagnostics check_running; do
  echo "Waiting for RabbitMQ to start..."
  sleep 5
done

# Enable management plugin
rabbitmq-plugins enable rabbitmq_management

# Create admin user if it doesn't exist
rabbitmqctl add_user ${RABBITMQ_DEFAULT_USER:-admin} ${RABBITMQ_DEFAULT_PASS:-admin123} 2>/dev/null || true
rabbitmqctl set_user_tags ${RABBITMQ_DEFAULT_USER:-admin} administrator

# Create vhost if it doesn't exist
rabbitmqctl add_vhost ${RABBITMQ_DEFAULT_VHOST:-/} 2>/dev/null || true

# Set permissions
rabbitmqctl set_permissions -p ${RABBITMQ_DEFAULT_VHOST:-/} ${RABBITMQ_DEFAULT_USER:-admin} ".*" ".*" ".*"

# Create default queue and exchange
rabbitmqctl eval "
rabbit_amqqueue:declare({resource, <<\"${RABBITMQ_DEFAULT_VHOST:-/}\">>, queue, <<\"default\">>}, true, false, [], none, <<\"${RABBITMQ_DEFAULT_USER:-admin}\">>).
rabbit_exchange:declare({resource, <<\"${RABBITMQ_DEFAULT_VHOST:-/}\">>, exchange, <<\"sec_cc_exchange\">>}, direct, true, false, false, []).
rabbit_binding:add({binding, {resource, <<\"${RABBITMQ_DEFAULT_VHOST:-/}\">>, exchange, <<\"sec_cc_exchange\">>}, <<\"default\">>, {resource, <<\"${RABBITMQ_DEFAULT_VHOST:-/}\">>, queue, <<\"default\">>}, []}).
"

echo "RabbitMQ initialization completed"