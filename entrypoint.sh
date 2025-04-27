#!/bin/sh

DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-3306}

echo "Waiting for database network connectivity at $DB_HOST:$DB_PORT..."
echo "Initial sleep (15s) to allow DB service to stabilize..."
sleep 15

echo "Database should be starting... attempting network checks with nc."
until nc -z $DB_HOST $DB_PORT; do
    echo "Network check failed, waiting 5 seconds..."
    sleep 5
done

echo "Network connection to $DB_HOST:$DB_PORT successful!"

echo "Applying database migrations..."
python manage.py migrate --noinput
migration_result=$?
if [ $migration_result -ne 0 ]; then
    echo "ERROR: Database migrations failed."
    exit 1
fi

echo "Migrations applied successfully."
echo "Starting Django server..."
exec "$@"