""" Zelenium product initialization

This product uses the Selenium javascript to run browser-driven tests.

$Id$
"""

import zuite
import permissions

zelenium_globals = globals()

def initialize(context):

    context.registerClass( zuite.Zuite
                         , permission=permissions.ManageSeleniumTestCases
                         , constructors=( zuite.manage_addZuiteForm
                                        , zuite.manage_addZuite
                                        )
                         , icon='www/check.gif'
                         )
