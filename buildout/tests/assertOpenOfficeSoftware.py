

import unittest
import uno

class AssertOpenOfficeSoftware(unittest.TestCase):
   """ tests try some connection and call some methods from uno"""

   def test_simple_connection(self):
     localContext = uno.getComponentContext()
     resolver = localContext.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver",  localContext )
     self.assertNotEquals(None, resolver)
     remoteContext = resolver.resolve("uno:socket,host=localhost,port=8100;urp;StarOffice.ComponentContext")
     self.assertNotEquals(None, remoteContext)
     self.assertNotEquals(None, remoteContext.ServiceManager)
     some_filter = remoteContext.ServiceManager.createInstance("com.sun.star.document.FilterFactory")
     self.assertNotEquals(None, some_filter)
     type_service = remoteContext.ServiceManager.createInstance("com.sun.star.document.TypeDetection")
     self.assertNotEquals(None, type_service)
     

if __name__ == '__main__':
  unittest.main()

