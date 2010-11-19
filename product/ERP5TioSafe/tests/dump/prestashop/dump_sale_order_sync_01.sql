/* ********** Person delcaration ********** */
INSERT INTO `ps_customer` (id_customer, firstname, lastname, email, birthday, deleted) VALUES (1, 'Jean', 'GRAY', 'jean@gray.com', '1985-04-05', 0);
INSERT INTO `ps_address` (id_address, id_country, id_customer, address1, postcode, city, deleted) VALUES (1, 8, 1, '22 rue des Peupliers', '75000', 'Paris', 0);


/* ********** Product delcaration ********** */
INSERT INTO `ps_product` (id_product, id_tax, reference, price, wholesale_price, ean13, active) VALUES (1, 1, '01111', 2.1, 1.1, NULL, 1), (2, 1, '02222', 20.2, 10.2, 2222222222222, 1), (3, 1, '03333', 200.3, 100.3, 3333333333338, 1), (4, 1, '04444', 2000.4, 1000.4, 4444444444444, 1);
INSERT INTO `ps_product_lang` (id_product, id_lang, name) VALUES (1, 2, 'Stylo'), (2, 2, 'Ballon'), (3, 2, 'Ballon de Foot'), (4, 2, 'Ballon de Basket');
/* Variation declaration */
INSERT INTO `ps_attribute_group_lang` (id_attribute_group, id_lang, name, public_name) VALUES (1, 2, 'Taille du Ballon', 'Taille du Ballon'), (2, 2, 'Couleur', 'Couleur');
INSERT INTO `ps_attribute` (id_attribute, id_attribute_group, color) VALUES (1, 1, NULL), (2, 1, NULL), (3, 2, '#FFFFFF'), (4, 2, '#000000');
INSERT INTO `ps_attribute_lang` (id_attribute, id_lang, name) VALUES (1, 2, 's4'), (2, 2, 's5'), (3, 2, 'Blanc'), (4, 2, 'Noir');
/* Mapping between product and attribute */
INSERT INTO `ps_product_attribute` (id_product_attribute, id_product, reference, supplier_reference, location, ean13, wholesale_price, price, ecotax, quantity, weight, default_on) VALUES (1, 2, '', '', '', '', '0.000000', '0.00', '0.00', 10, 0, 0), (2, 2, '', '', '', '', '0.000000', '0.00', '0.00', 20, 0, 0), (3, 3, '', '', '', '', '0.000000', '0.00', '0.00', 30, 0, 0), (4, 3, '', '', '', '', '0.000000', '0.00', '0.00', 40, 0, 0), (5, 4, '', '', '', '', '0.000000', '0.00', '0.00', 50, 0, 0), (6, 4, '', '', '', '', '0.000000', '0.00', '0.00', 60, 0, 0), (7, 4, '', '', '', '', '0.000000', '0.00', '0.00', 70, 0, 0), (8, 4, '', '', '', '', '0.000000', '0.00', '0.00', 80, 0, 0);
INSERT INTO `ps_product_attribute_combination` (id_attribute, id_product_attribute) VALUES (1, 1), (2, 2), (3, 3), (4, 4), (1, 5), (3, 5), (1, 6), (4, 6), (2, 7), (3, 7), (2, 8), (4, 8);

/* ********** Sale Order declaration ********** */
INSERT INTO `ps_orders` VALUES (1,2,2,1,1,1,1,1,'40959ebe0a5332ea6864b557ee546915','CB','carte bancaire',1,0,'','','0.00','10.49','10.49','2.10','7.98','0.00',0,0,'2010-06-14 09:00:00','2010-06-16 09:00:00',0,'2010-06-14 09:00:00','2010-06-14 09:00:00');
INSERT INTO `ps_order_detail` VALUES (1,1,1,0,'Stylo',1,1,0,0,0,'2.100000','0.000000',NULL,'01111',NULL,0,'TVA 19.6%','19.60','0.00','',0,'2010-06-14 09:00:00');
INSERT INTO `ps_order_history` VALUES (1,0,1,4,'2010-06-14 09:00:00');
INSERT INTO `ps_cart` VALUES (1,2,2,1,1,1,1,1,1,0,'','2010-06-14 09:00:00','2010-06-14 09:00:00');
