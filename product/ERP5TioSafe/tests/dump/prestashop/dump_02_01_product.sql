INSERT INTO `ps_product` (id_product, id_tax, ean13, reference, active, date_add, date_upd) VALUES (1, 1, '1234567890128', 'myShort123', 1, '2009-09-1414:00:00', '2009-09-1414:00:00');
INSERT INTO `ps_product_lang` (id_product, id_lang, description, link_rewrite, name) VALUES (1, 1, 'This is a magnificient tee-shirt Tux', 'tee-shirt', 'Tee-Shirt Tux'), (1, 2, 'Voici un sublime tee-shirt Tux', 'tee-shirt', 'Tee-Shirt Tux');
INSERT INTO `ps_category_product` (id_category, id_product, position) VALUES (1, 1, 1);

