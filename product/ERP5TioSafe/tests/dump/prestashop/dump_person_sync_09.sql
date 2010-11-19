/* ********** Person delcaration ********** */
INSERT INTO `ps_customer` (id_customer, firstname, lastname, email, birthday, deleted) VALUES (1, 'Perry', 'COX', 'perry@cox.com', '1959-08-03', 0);
INSERT INTO `ps_address` (id_address, id_country, id_customer, address1, postcode, city, deleted) VALUES (1, 8, 1, '456 rue de la Paix', '75000', 'Paris', 0), (2, 1, 1, '789 avenue des Fleurs', '44001', 'Dortmund', 0);
