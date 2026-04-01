SELECT uid, path FROM catalog WHERE <dtml-sqltest column="path" expr="path_list" op=eq type="string" multiple>
