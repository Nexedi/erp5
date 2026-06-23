SELECT il.name AS "KEY_NAME", ii.name AS "COLUMN_NAME"
FROM pragma_index_list(<dtml-sqlvar table type="string">) AS il,
     pragma_index_info(il.name) AS ii
