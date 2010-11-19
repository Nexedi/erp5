/* ********** Variation declaration ********** */
INSERT INTO `ps_attribute_group_lang` (id_attribute_group, id_lang, name, public_name) VALUES (1, 2, 'Taille du Ballon', 'Taille du Ballon'), (2, 2, 'Couleur', 'Couleur');
INSERT INTO `ps_attribute` (id_attribute, id_attribute_group, color) VALUES (1, 1, NULL), (2, 1, NULL), (3, 1, NULL),  (4, 2, '#FFFFFF'), (5, 2, '#000000'), (6, 2, '#FF0000');                                   
INSERT INTO `ps_attribute_lang` (id_attribute, id_lang, name) VALUES (1, 2, 's4'), (2, 2, 's5'), (3, 2, 's6'), (4, 2, 'Blanc'), (5, 2, 'Noir'), (6, 2, 'Rouge');
