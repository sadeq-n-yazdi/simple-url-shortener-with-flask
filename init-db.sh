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

CREATE DATABASE IF NOT EXISTS `huma`;
USE `huma`;

CREATE TABLE IF NOT EXISTS `url` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `code` char(15) DEFAULT NULL,
  `url` varchar(1024) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `url_code_index` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=100000;

SELECT `url`
FROM `huma`.`url`
ORDER BY id DESC
LIMIT 50;

-- GRANT ALL PRIVILEGES ON huma.* TO 'user'@'%';
-- ALTER USER 'user'@'%' IDENTIFIED BY 'secret-pw';

SQL

echo "Database is ready to serve"
