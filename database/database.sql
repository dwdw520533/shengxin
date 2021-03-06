DROP DATABASE IF EXISTS wepay_host;
CREATE DATABASE wepay_host DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

GRANT ALL PRIVILEGES ON wepay_host.* TO wepay@localhost IDENTIFIED BY 'wepay' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON wepay_host.* TO wepay@"%" IDENTIFIED BY 'wepay' WITH GRANT OPTION;
