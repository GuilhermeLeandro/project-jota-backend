-- docker-entrypoint-initdb.d/grant-permissions.sql
-- ALERTA: Concede permissão para criar bancos. Use com cautela em produção.
GRANT ALL PRIVILEGES ON `test\_%`.* TO 'jota_user'@'%';
-- Ou, mais abrangente (e menos seguro), mas garante a criação do banco:
-- GRANT CREATE, ALTER, DROP, REFERENCES ON *.* TO 'jota_user'@'%';
-- A linha abaixo é geralmente mais segura e suficiente se o Django só precisa criar test_jota_db:
GRANT CREATE ON *.* TO 'jota_user'@'%';
FLUSH PRIVILEGES;
