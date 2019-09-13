# -*- coding: UTF-8 -*-
# -*- Mode: Python; py-indent-offset: 4 -*-
# Authors: Nik Kim <fafhrd@legco.biz>

from App.ImageFile import ImageFile
from .TimerService import TimerService, current_version

misc_ = { 'timer_icon.gif':
          ImageFile('zpt/timer_icon.gif', globals())}

cp_id = 'timer_service'

def getTimerService(context):
    """ returns the SMTP srevice instance """
    root = context.getPhysicalRoot()
    try:
        timer_service = getattr(root, cp_id)
    except AttributeError:
        try:
            control_panel = root.Control_Panel
            timer_service = getattr(control_panel, cp_id)
        except AttributeError:
            timer_service = TimerService(cp_id)
        else:
            control_panel._delObject(cp_id)
        root._setObject(cp_id, timer_service)
    return timer_service
