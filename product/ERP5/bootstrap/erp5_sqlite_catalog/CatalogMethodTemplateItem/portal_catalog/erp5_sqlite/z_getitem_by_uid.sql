SELECT uid, path FROM catalog WHERE <dtml-sqltest column="uid" expr="uid_list" op=eq type="int" multiple>
