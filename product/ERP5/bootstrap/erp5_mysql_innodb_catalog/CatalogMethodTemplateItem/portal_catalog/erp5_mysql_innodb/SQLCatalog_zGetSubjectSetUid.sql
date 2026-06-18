SELECT subject_set_uid
FROM subject
WHERE <dtml-sqltest subject_list column="subject" type="string" multiple>
GROUP BY subject_set_uid
HAVING COUNT(DISTINCT subject) = <dtml-var expr="_.len(subject_list)">
