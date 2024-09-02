#!/usr/bin/env bash

docker container rm huma-mariadb

docker run --detach --name huma-mariadb --env MARIADB_ROOT_PASSWORD=my-secret  -p 3306:3306 --volume=mysql-data:/var/lib/mysql:Z --env MARIADB_USER=user --env MARIADB_PASSWORD=secret-pw  mariadb:latest

while ! mysqladmin -h127.0.0.1 -uuser -psecret-pw --silent ping 2>/dev/null ;do
  sleep 1
done
echo "Database is up."

mysql -h127.0.0.1 -uroot -pmy-secret 'USE huma' 2>/dev/null || \
mysql -h127.0.0.1 -uroot -pmy-secret 2>/dev/null <<SQL
SET NAMES utf8;
CREATE DATABASE IF NOT EXISTS huma;
USE huma;
CREATE TABLE IF NOT EXISTS huma.url
(
    id   bigint unsigned auto_increment
        primary key,
    code char(15)      not null comment 'Short codes will be alpha numeric',
    url  varchar(1024) not null comment 'Any valid URL up to 1024 character',
    constraint url_code_unique
        unique (code) comment 'code will be unique'
)
    engine = MyISAM;
    GRANT ALL PRIVILEGES ON huma.* TO 'user'@'%';
--    ALTER USER 'user'@'%' IDENTIFIED BY 'secret-pw';

SQL

echo "Database is ready to serve"
