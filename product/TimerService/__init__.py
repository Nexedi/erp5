# -*- coding: UTF-8 -*-
# -*- Mode: Python; py-indent-offset: 4 -*-
# Authors: Nik Kim <fafhrd@legco.biz> 

from App.ImageFile import ImageFile
from AccessControl import ModuleSecurityInfo, allow_module
from AccessControl.Permissions import view

from TimerService import TimerService, current_version

misc_ = { 'timer_icon.gif':
          ImageFile('zpt/timer_icon.gif', globals())}

cp_id = 'timer_service'

def getTimerService(context):
    """ returns the SMTP srevice instance """
    return context.Control_Panel.timer_service

def make_timer_service(cp):
    """Control_Panel smtp service"""
    timer_service = TimerService(cp_id)
    cp._setObject(cp_id, timer_service)
    return getattr(cp, cp_id)

def initialize(context):
    # hook into the Control Panel
    cp = context._ProductContext__app.Control_Panel
    if cp_id in cp.objectIds():
        #cp._delObject(cp_id)
        timer = getattr(cp, cp_id)
        timer_service = timer
        if not isinstance(timer_service, TimerService):
            timer = make_timer_service(cp)
    else:
        timer = make_timer_service(cp)

    if timer._version < current_version:
        cp._delObject(cp_id)
        timer = make_timer_service(cp)
