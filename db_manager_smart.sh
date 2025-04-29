#!/bin/bash

echo "📦 Smart Database Manager Script"
echo "---------------------------------"

# List running Docker containers
echo "🔍 Detecting running Docker containers..."
docker ps --format "table {{.Names}}\t{{.Image}}" | grep postgres

echo ""
read -p "Enter the exact container name from the list above: " CONTAINER_NAME
read -p "Enter database user: " DB_USER
read -p "Enter database name: " DB_NAME

echo ""
echo "What do you want to do?"
echo "1) Backup database"
echo "2) Restore database"
read -p "Enter choice [1 or 2]: " ACTION

if [ "$ACTION" == "1" ]; then
    # Backup
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    OUTPUT_FILE="backup_${DB_NAME}_${TIMESTAMP}.sql"

    echo "🛠 Backing up database '$DB_NAME' from container '$CONTAINER_NAME'..."
    docker exec -t "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" > "$OUTPUT_FILE"

    if [ $? -eq 0 ]; then
        echo "✅ Backup completed! File saved as '$OUTPUT_FILE'."
    else
        echo "❌ Backup failed."
    fi

elif [ "$ACTION" == "2" ]; then
    # Restore
    echo ""
    echo "📂 Available .sql files:"
    ls *.sql 2>/dev/null || echo "No .sql files found."
    echo ""
    read -p "Enter input filename (e.g., backup.sql): " INPUT_FILE

    if [ ! -f "$INPUT_FILE" ]; then
        echo "❌ Input file '$INPUT_FILE' does not exist!"
        exit 1
    fi

    echo "🛠 Restoring database '$DB_NAME' in container '$CONTAINER_NAME'..."
    docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" "$DB_NAME" < "$INPUT_FILE"

    if [ $? -eq 0 ]; then
        echo "✅ Restore completed!"
    else
        echo "❌ Restore failed."
    fi

else
    echo "⚠️ Invalid choice. Exiting."
    exit 1
fi
