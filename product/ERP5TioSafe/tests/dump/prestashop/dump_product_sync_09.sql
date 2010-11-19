/* ********** Product declaration ********** */
UPDATE ps_product SET price = 120.0, wholesale_price = 0.0, ean13 = '1357913579130'  WHERE id_product = 1;
/* ********** Update the variations ********** */
DELETE FROM `ps_product_attribute_combination`;
INSERT INTO `ps_product_attribute_combination` (id_attribute, id_product_attribute) VALUES (1, 1), (4, 1), (1, 2), (6, 2), (3, 3), (4, 3), (3, 4), (6, 4);

