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
            <value> <string>ts44314673.3</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>sass_extensions.rb</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-ruby</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

# -----------------------------------------------\n
# Sass implementation of the Noisy jquery plugin:\n
# https://github.com/DanielRapp/Noisy\n
# by @philippbosch\n
# https://gist.github.com/1021332\n
# -----------------------------------------------\n
\n
module Sass::Script::Functions\n
 def background_noise(kwargs = {})\n
   opts = {}\n
   Sass::Util.map_hash({\n
       "intensity"  => [0..1,          "",   :Number, Sass::Script::Number.new(0.5) ],\n
       "opacity"    => [0..1,          "",   :Number, Sass::Script::Number.new(0.08)],\n
       "size"       => [1..512,        "px", :Number, Sass::Script::Number.new(200) ],\n
       "monochrome" => [[true, false], "",   :Bool,   Sass::Script::Bool.new(false) ]\n
     }) do |name, (range, units, type, default)|\n
\n
     if val = kwargs.delete(name)\n
       assert_type val, type, name\n
       if range && !range.include?(val.value)\n
         raise ArgumentError.new("$#{name}: Amount #{val} must be between #{range.first}#{units} and #{range.last}#{units}")\n
       end\n
     else\n
       val = default\n
     end\n
     opts[name] = val\n
   end\n
\n
   image = ChunkyPNG::Image.new(opts["size"].to_i, opts["size"].to_i)\n
\n
   for i in (0..(opts["intensity"].to_s.to_f * (opts["size"].to_i**2)))\n
      x = rand(opts["size"].to_i)\n
      y = rand(opts["size"].to_i)\n
      r = rand(255)\n
      a = rand(255 * opts["opacity"].to_s.to_f)\n
      color = opts["monochrome"] ? ChunkyPNG::Color.rgba(r, r, r, a) : ChunkyPNG::Color.rgba(r, rand(255), rand(255), a)\n
      image.set_pixel(x, y, color)\n
   end\n
\n
   data = Base64.encode64(image.to_blob).gsub("\\n", "")\n
   Sass::Script::String.new("url(\'data:image/png;base64,#{data}\')")\n
 end\n
 declare :background_noise, [], :var_kwargs => true\n
end\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>1692</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
