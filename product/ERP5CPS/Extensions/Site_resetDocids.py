from Products.ERP5SyncML.Conduit.ERP5Conduit import ERP5Conduit

def main(self):
  xml_workspace = """<erp5><object id="1320758020__0001" portal_type="Workspace">
    <layout_and_schema type="object">None</layout_and_schema>
    <Coverage type="string"></Coverage>
    <CreationDate type="date">2004-06-01 12:57:21</CreationDate>
    <Creator type="string">seb</Creator>
    <Description type="string"></Description>
    <EffectiveDate type="date">None</EffectiveDate>
    <ExpirationDate type="date">None</ExpirationDate>
    <Format type="string">text/html</Format>
    <Language type="string">en</Language>
    <ModificationDate type="date">2004-06-01 12:57:21</ModificationDate>
    <Relation type="string"></Relation>
    <Rights type="string"></Rights>
    <Source type="string"></Source>
    <Title type="string">Root of Workspaces</Title>
    <allow_discussion type="int">0</allow_discussion>
    <hidden_folder type="int">0</hidden_folder>
    <preview type="object">None</preview>
    <local_role id="seb" type="tokens">permission:Modify_portal_content</local_role>
  </object>
  </erp5>"""

  xml_section = """<erp5><object id="628256376__0001" portal_type="Section">
    <layout_and_schema type="object">None</layout_and_schema>
    <Coverage type="string"></Coverage>
    <CreationDate type="date">2004-06-01 12:57:21</CreationDate>
    <Creator type="string">seb</Creator>
    <Description type="string"></Description>
    <EffectiveDate type="date">None</EffectiveDate>
    <ExpirationDate type="date">None</ExpirationDate>
    <Format type="string">text/html</Format>
    <Language type="string">en</Language>
    <ModificationDate type="date">2004-06-01 12:57:21</ModificationDate>
    <Relation type="string"></Relation>
    <Rights type="string"></Rights>
    <Source type="string"></Source>
    <Title type="string">Root of Sections</Title>
    <allow_discussion type="int">0</allow_discussion>
    <hidden_folder type="int">0</hidden_folder>
    <preview type="object">None</preview>
  </object>
  </erp5>"""

  portal_repository = self.portal_repository

  conduit = ERP5Conduit()
  conduit.addNode(xml=xml_workspace,object=portal_repository)
  conduit.addNode(xml=xml_section,object=portal_repository)
  
  self.workspaces.setDocid(1320758020)
  self.sections.setDocid(628256376)
  return "ok"
