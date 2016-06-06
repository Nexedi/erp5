<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts44314671.22</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Rakefile.rb</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-ruby</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string>task :default do\n
  sh "compass compile"\n
end\n
\n
task :pages do\n
  require \'git\'\n
  require \'fileutils\'\n
  repo = Git.open(\'.\')\n
\n
  #  copy tests into a temp dir before switching branch\n
  FileUtils.rm_rf "tmp"\n
  FileUtils.mkdir("tmp")\n
  (FileList.new(\'tests/**/*.html\')+FileList.new(\'tests/**/*.css\')).each do |file|\n
    FileUtils.mkdir_p(File.dirname("tmp/#{file[6..-1]}"))\n
    FileUtils.cp(file, "tmp/#{file[6..-1]}")\n
  end\n
\n
  # switch branch\n
  repo.branch("gh-pages").checkout\n
\n
  # Prepare gh-pages\n
  FileUtils.rm_rf "recipes/*"\n
  htmlHeader = File.open("layout/header.html", "r").read\n
  htmlFooter = File.open("layout/footer.html", "r").read\n
\n
  # HTML files need header and footer\n
  FileList.new(\'tmp/**/*.html\').each do |file|\n
    FileUtils.mkdir_p(File.dirname("#{file[4..-1]}"))\n
    htmlfile = File.open("#{file[4..-1]}", "w")\n
    contents = File.open(file, "rb").read\n
    htmlfile.write(htmlHeader+contents+htmlFooter)\n
    htmlfile.close\n
  end\n
\n
  # CSS: just copy\n
  FileList.new(\'tmp/**/*.css\').each do |file|\n
    FileUtils.mkdir_p(File.dirname("#{file[4..-1]}"))\n
    FileUtils.cp(file, "#{file[4..-1]}")\n
  end\n
\n
  FileUtils.rm_rf("tmp")\n
\n
  # Commit gh-pages changes\n
  # @todo make this optional ?\n
  Dir["recipes/**/*"].each {|f| repo.add(f) }\n
  repo.status.deleted.each {|f, s| repo.remove(f)}\n
  message = ENV["MESSAGE"] || "Updated at #{Time.now.utc}"\n
  repo.commit(message)\n
\n
  # back to master (maybe it\'s not appropriate if we are not working on master ?!)\n
  repo.branch("master").checkout\n
end</string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>1496</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
