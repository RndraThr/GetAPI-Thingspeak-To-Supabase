#!/bin/bash
# Backup file CSV ke folder backup atau server lain

BACKUP_DIR="/backup"
SOURCE_FILE="/opt/my_thingspeak_project/data/data_log.csv"

mkdir -p $BACKUP_DIR

cp $SOURCE_FILE "$BACKUP_DIR/data_log_$(date +'%Y%m%d_%H%M%S').csv"
echo "Backup completed at $(date)" >> /opt/my_thingspeak_project/logs/app.log
