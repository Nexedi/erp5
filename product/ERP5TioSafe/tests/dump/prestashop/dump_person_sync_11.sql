/* ********** Update person ********** */
UPDATE `ps_customer` SET birthday = '1959-08-03' WHERE id_customer = 1;
DELETE FROM `ps_address`;
INSERT INTO `ps_address` (id_address, id_country, id_customer, address1, postcode, city, deleted) VALUES (1, 1, 1, '123 boulevard des Capucines', '72160', 'Stuttgart', 0), (2, 1, 1, '789 avenue des Fleurs', '44001', 'Dortmund', 0);
