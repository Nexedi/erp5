SELECT gid 
FROM syncml
WHERE
 path like <dtml-sqlvar signature_path type="string">
AND
 gid not in (SELECT gid FROM syncml WHERE
            path like <dtml-sqlvar source_path type="string">)