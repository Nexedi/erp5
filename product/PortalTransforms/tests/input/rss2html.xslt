<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:transform xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version='1.0'>

<xsl:strip-space elements='*'/>
<xsl:output method='xml'/>

<!-- Narval prototype ====================================================== -->

<al:prototype xmlns:al="http://www.logilab.org/namespaces/Narval/1.2">
<al:description lang="fr">Transforme du RSS en du HTML.</al:description>
<al:description lang="en">Turns RSS into HTML.</al:description>

<al:input id="input"><al:match>rss</al:match></al:input>
<al:output id="output" list="yes"><al:match>html-body</al:match></al:output>
</al:prototype>

<!-- root ================================================================== -->
 
<xsl:template match='rss/rss/channel'>
  <html-body>
    <h2>
      <xsl:value-of select='title'/>
    </h2>
    <p>
      <xsl:element name='a'>
        <xsl:attribute name='href'><xsl:value-of select='link'/></xsl:attribute>
        <xsl:value-of select='title'/>
      </xsl:element>
      <em><xsl:value-of select='description'/></em>
    </p>
    <table>
      <xsl:apply-templates select='item'/>
    </table>
  </html-body>
</xsl:template>

<xsl:template match='item'>
    <tr>
      <td>
        <xsl:element name='a'>
          <xsl:attribute name='href'><xsl:value-of select='link'/></xsl:attribute>
          <xsl:value-of select='title'/>
        </xsl:element>
        <xsl:apply-templates mode='multi' select='description'/>
      </td>
    </tr>
</xsl:template>

</xsl:transform>
