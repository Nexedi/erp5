/* ********** Person delcaration ********** */
INSERT INTO `ps_customer` (id_customer, firstname, lastname, email, birthday, deleted) VALUES (1, 'John', 'DORIAN', 'john@dorian.com', '1980-01-27', 0);
INSERT INTO `ps_address` (id_address, id_country, id_customer, address1, postcode, city, deleted) VALUES (1, 8, 1, '22 rue des Champs', '75000', 'Paris', 0), (2, 8, 1, '17 rue des Plomb', '44001', 'Dortmund', 0);
