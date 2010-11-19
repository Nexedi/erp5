/* ********** Product declaration ********** */
INSERT INTO `ps_product` (id_product, id_tax, reference, price, wholesale_price, ean13, active) VALUES (1, 1, '0123456789', 2.123456, 1.123456, 1234567890128, 1);
INSERT INTO `ps_product_lang` (id_product, id_lang, name) VALUES (1, 2, 'Ballon de Foot');
/* ********** Variation declaration ********** */
INSERT INTO `ps_attribute_group_lang` (id_attribute_group, id_lang, name, public_name) VALUES (1, 2, 'Taille du Ballon', 'Taille du Ballon'), (2, 2, 'Couleur', 'Couleur');
INSERT INTO `ps_attribute` (id_attribute, id_attribute_group, color) VALUES (1, 1, NULL), (2, 1, NULL), (3, 2, '#FFFFFF'), (4, 2, '#000000');
INSERT INTO `ps_attribute_lang` (id_attribute, id_lang, name) VALUES (1, 2, 's4'), (2, 2, 's5'), (3, 2, 'Blanc'), (4, 2, 'Noir');
/* ********** Mapping between product and attribute ********** */
INSERT INTO `ps_product_attribute` (id_product_attribute, id_product, reference, supplier_reference, location, ean13, wholesale_price, price, ecotax, quantity, weight, default_on) VALUES (1, 1, '', '', '', '', '0.000000', '0.00', '0.00', 10, 0, 0), (2, 1, '', '', '', '', '0.000000', '0.00', '0.00', 20, 0, 0), (3, 1, '', '', '', '', '0.000000', '0.00', '0.00', 30, 0, 0), (4, 1, '', '', '', '', '0.000000', '0.00', '0.00', 40, 0, 0);
INSERT INTO `ps_product_attribute_combination` (id_attribute, id_product_attribute) VALUES (1, 1), (3, 1), (1, 2), (4, 2), (2, 3), (3, 3), (2, 4), (4, 4);
