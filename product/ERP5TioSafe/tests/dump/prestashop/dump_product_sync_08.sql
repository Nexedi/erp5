/* ********** Product declaration ********** */
INSERT INTO `ps_product` (id_product, id_tax, reference, price, wholesale_price, active) VALUES (1, 1, 'a5962z', 200.25, 100.25, 1);
INSERT INTO `ps_product_lang` (id_product, id_lang, name) VALUES (1, 2, 'Ballon de Plage');
/* ********** Variation declaration ********** */
INSERT INTO `ps_attribute_group_lang` (id_attribute_group, id_lang, name, public_name) VALUES (1, 2, 'Taille du Ballon', 'Taille du Ballon'), (2, 2, 'Couleur', 'Couleur');
INSERT INTO `ps_attribute` (id_attribute, id_attribute_group, color) VALUES (1, 1, NULL), (2, 1, NULL), (3, 1, NULL),  (4, 2, '#FFFFFF'), (5, 2, '#000000'), (6, 2, '#FF0000');
INSERT INTO `ps_attribute_lang` (id_attribute, id_lang, name) VALUES (1, 2, 's4'), (2, 2, 's5'), (3, 2, 's6'), (4, 2, 'Blanc'), (5, 2, 'Noir'), (6, 2, 'Rouge');
/* ********** Mapping between product and attribute ********** */
INSERT INTO `ps_product_attribute` (id_product_attribute, id_product, reference, supplier_reference, location, ean13, wholesale_price, price, ecotax, quantity, weight, default_on) VALUES (1, 1, '', '', '', '', '0.000000', '0.00', '0.00', 12, 0, 0), (2, 1, '', '', '', '', '0.000000', '0.00', '0.00', 22, 0, 0), (3, 1, '', '', '', '', '0.000000', '0.00', '0.00', 32, 0, 0), (4, 1, '', '', '', '', '0.000000', '0.00', '0.00', 42, 0, 0), (5, 1, '', '', '', '', '0.000000', '0.00', '0.00', 52, 0, 0), (6, 1, '', '', '', '', '0.000000', '0.00', '0.00', 62, 0, 0), (7, 1, '', '', '', '', '0.000000', '0.00', '0.00', 72, 0, 0), (8, 1, '', '', '', '', '0.000000', '0.00', '0.00', 82, 0, 0), (9, 1, '', '', '', '', '0.000000', '0.00', '0.00', 92, 0, 0);
INSERT INTO `ps_product_attribute_combination` (id_attribute, id_product_attribute) VALUES (1, 1), (4, 1), (1, 2), (5, 2), (2, 3), (4, 3), (2, 4), (5, 4);
