from erp5.component.test.testHalJsonStyle import ERP5HALJSONStyleSkinsMixin, simulate, changeSkin, do_fake_request

class TestHalRestricted(ERP5HALJSONStyleSkinsMixin):

  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('HalRestricted')
  def test_mode_root(self):
    fake_request = do_fake_request("GET")
    self.logout()
    self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request)
    self.assertEquals(fake_request.RESPONSE.status, 401)
    self.assertEquals(fake_request.RESPONSE.getHeader('WWW-Authenticate'),
      'X-Delegate uri="%s/connection/login_form{?came_from}"' % self.portal.web_site_module.hateoas.absolute_url()
    )

  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('HalRestricted')
  def test_mode_traverse(self):
    document_relative_url = self._makeDocument().getRelativeUrl()
    fake_request = do_fake_request("GET")
    self.logout()
    self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request, mode="traverse", relative_url=document_relative_url)
    self.assertEquals(fake_request.RESPONSE.status, 401)
    self.assertEquals(fake_request.RESPONSE.getHeader('WWW-Authenticate'),
      'X-Delegate uri="%s/connection/login_form{?came_from}"' % self.portal.web_site_module.hateoas.absolute_url()
    )

  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('HalRestricted')
  def test_mode_search(self):
    fake_request = do_fake_request("GET")
    self.logout()
    self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request, mode="search")
    self.assertEquals(fake_request.RESPONSE.status, 401)
    self.assertEquals(fake_request.RESPONSE.getHeader('WWW-Authenticate'),
      'X-Delegate uri="%s/connection/login_form{?came_from}"' % self.portal.web_site_module.hateoas.absolute_url()
    )

  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('HalRestricted')
  def test_mode_worklist(self):
    fake_request = do_fake_request("GET")
    self.logout()
    self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request, mode="worklist")
    self.assertEquals(fake_request.RESPONSE.status, 401)
    self.assertEquals(fake_request.RESPONSE.getHeader('WWW-Authenticate'),
      'X-Delegate uri="%s/connection/login_form{?came_from}"' % self.portal.web_site_module.hateoas.absolute_url()
    )
