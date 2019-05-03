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
    result = self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request)
    self.assertEquals(fake_request.RESPONSE.status, 401)
    self.assertEquals(fake_request.RESPONSE.getHeader('WWW-Authenticate'),
      'X-Delegate uri="%s/connection/login_form{?came_from}"' % self.portal.web_site_module.hateoas.absolute_url()
    )