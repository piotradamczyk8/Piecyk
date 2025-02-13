#!/bin/bash
SOURCE_DIR="/Users/piotradamczyk/Projects/Piecyk"
DESTINATION="piotradamczyk@192.168.0.234:/home/piotradamczyk/Projects/Piecyk"

fswatch -o "$SOURCE_DIR" | while read f; do
    rsync -avz --exclude '.git' --delete "$SOURCE_DIR" "$DESTINATION"
done
