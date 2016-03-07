s="""<script type="text/javascript">
var d = loadJSONDoc('%s/KnowledgeBox_getDefaultPreferencesDictAsJSON');
var gotMetadata = function (meta) {
    alert('Preferred max rows = ' + meta.preferred_max_rows);
};
var metadataFetchFailed = function (err) {
  alert("Fail fetching preferences");
};
d.addCallbacks(gotMetadata, metadataFetchFailed);
</script>
""" %box.absolute_url()

return s
