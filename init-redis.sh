#!/usr/bin/env bash

WORKDIR=$(realpath)

 docker container rm huma-redis 2>/dev/null && echo "old redis container stopped"
 docker run -d --rm --name huma-redis  --volume="${WORKDIR}/redis.conf:/redis.conf:ro" -p 6379:6379 -d redis:alpine redis-server  /redis.conf && \
 sleep 1 && \
 docker logs huma-redis