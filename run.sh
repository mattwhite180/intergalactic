#!/bin/bash
cd ~/goalsandplans

FILE=secrets.env

if [ -f "$FILE" ]; then
    echo $FILE "exists."
else 
    echo "$FILE does not exist."
    touch $FILE
    echo "created $FILE"
fi

docker-compose down --remove-orphans && \
docker-compose build  && \
docker-compose --env-file secrets.env up
