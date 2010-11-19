/* ********** Update the variations ********** */
DELETE FROM `ps_product_attribute_combination`;
INSERT INTO `ps_product_attribute_combination` (id_attribute, id_product_attribute) VALUES (1, 1), (4, 1), (1, 3), (4, 3);
