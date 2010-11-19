/* ********** Person delcaration ********** */
INSERT INTO `ps_customer` (id_customer, firstname, lastname, email, birthday, deleted) VALUES (1, 'Jenifer-Dylan', 'COX', 'jenifer-dylan@cox.com', '2008-06-06', 0);
INSERT INTO `ps_address` (id_address, id_country, id_customer, address1, postcode, city, deleted) VALUES (1, 8, 1, '234 rue de la Paix', '75000', 'Paris', 0), (2, 1, 1, '123 boulevard des Capucines', '72160', 'Stuttgart', 0), (3, 1, 1, '345 avenue des Fleurs', '44001', 'Dortmund', 0);
