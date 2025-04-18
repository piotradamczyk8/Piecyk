#!/bin/bash
SOURCE_DIR="/Users/piotradamczyk/Projects"
DESTINATION="piotradamczyk@192.168.0.109:/home/piotradamczyk"

fswatch -o "$SOURCE_DIR" | while read f; do
    rsync -avz --exclude '.git' --delete "$SOURCE_DIR" "$DESTINATION"
done 