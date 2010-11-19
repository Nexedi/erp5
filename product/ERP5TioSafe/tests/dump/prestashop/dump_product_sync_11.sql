/* ********** Update the variations ********** */
DELETE FROM `ps_product_attribute_combination`;
INSERT INTO `ps_product_attribute_combination` (id_attribute, id_product_attribute) VALUES (1, 1), (4, 1), (1, 2), (5, 2), (1, 3), (6, 3), (2, 4), (4, 4), (2, 5), (6, 5), (2, 6), (4, 6), (3, 7), (4, 7), (3, 8), (6, 8), (3, 9), (4, 9);
