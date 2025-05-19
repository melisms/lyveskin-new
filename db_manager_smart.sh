#!/bin/bash
trap ctrl_c INT

ctrl_c() {
    echo -e "\n\n⚠️  Script interrupted. Exiting..."
    exit 1
}

echo "📦 Smart PostgreSQL Manager Script"
echo "----------------------------------"

echo "Do you want to manage a:"
echo "1) Local Docker PostgreSQL container"
echo "2) Remote PostgreSQL database (via connection URI)"
read -p "Enter choice [1 or 2]: " MODE

echo ""
echo "What do you want to do?"
echo "1) Backup (pg_dump)"
echo "2) Restore (psql)"
read -p "Enter action [1 or 2]: " ACTION

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

if [ "$MODE" == "1" ]; then
    echo ""
    echo "🔍 Detecting running Docker containers..."
    docker ps --format "table {{.Names}}\t{{.Image}}" | grep postgres
    echo ""

    read -p "Enter container name: " CONTAINER_NAME
    read -p "Enter database user: " DB_USER
    read -p "Enter database name: " DB_NAME

    if [ "$ACTION" == "1" ]; then
        OUTPUT_FILE="backup_${DB_NAME}_${TIMESTAMP}.sql"
        echo "🛠 Backing up Docker DB '$DB_NAME' from container '$CONTAINER_NAME'..."
        docker exec -t "$CONTAINER_NAME" sh -c "pg_dump -U $DB_USER $DB_NAME" > "$OUTPUT_FILE"

        [ $? -eq 0 ] && echo "✅ Backup saved to '$OUTPUT_FILE'" || echo "❌ Backup failed."

    elif [ "$ACTION" == "2" ]; then
        echo ""
        echo "📂 Available .sql files:"
        ls *.sql 2>/dev/null || echo "No .sql files found."
        echo ""
        read -p "Enter SQL file to restore from: " INPUT_FILE

        if [ ! -f "$INPUT_FILE" ]; then
            echo "❌ File '$INPUT_FILE' not found!"
            exit 1
        fi

        echo "🛠 Restoring into Docker DB '$DB_NAME'..."
        docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" "$DB_NAME" < "$INPUT_FILE"
        [ $? -eq 0 ] && echo "✅ Restore complete." || echo "❌ Restore failed."
    fi

elif [ "$MODE" == "2" ]; then
    read -p "Enter PostgreSQL connection URI: " URI

    if [ "$ACTION" == "1" ]; then
        OUTPUT_FILE="backup_remote_${TIMESTAMP}.sql"
        echo "🛠 Backing up remote DB..."
        /opt/homebrew/opt/postgresql@16/bin/pg_dump "$URI" > "$OUTPUT_FILE"

        [ $? -eq 0 ] && echo "✅ Backup saved to '$OUTPUT_FILE'" || echo "❌ Backup failed."

    elif [ "$ACTION" == "2" ]; then
        echo ""
        echo "📂 Available .sql files:"
        ls *.sql 2>/dev/null || echo "No .sql files found."
        echo ""
        read -p "Enter SQL file to restore from: " INPUT_FILE

        if [ ! -f "$INPUT_FILE" ]; then
            echo "❌ File '$INPUT_FILE' not found!"
            exit 1
        fi

        echo "🛠 Restoring into remote DB..."
        /opt/homebrew/opt/postgresql@16/bin/psql "$URI" < "$INPUT_FILE"
        [ $? -eq 0 ] && echo "✅ Restore complete." || echo "❌ Restore failed."
    fi
else
    echo "⚠️ Invalid mode selected. Exiting."
    exit 1
fi
