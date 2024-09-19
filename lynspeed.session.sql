DROP TABLE user_auth_customuser;
DELETE FROM django_admin_log WHERE user_id IN (SELECT id FROM user_auth_customuser);
DROP TABLE user_auth_customuser;
DROP DATABASE lynspeed;

CREATE DATABASE lynspeed;

DROP TABLE user_auth_customuser;
USE lynspeed;
CREATE DATABASE lynspeed;
SHOW TABLES;

DROP DATABASE lynspeed;
USE lynspeed;

