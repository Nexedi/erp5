##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#          Guillaume MICHON <guillaume@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################



#
# Skeleton ZopeTestCase
#

from random import randint

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.DateUtils import millis, centis
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from DateTime import DateTime
from Acquisition import aq_base, aq_inner
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList
import time
from copy import deepcopy
  

class TestImmobilisation(ERP5TypeTestCase):

  # Different variables used for this test
  run_all_test = 1
  source_company_id = 'Nexedi'
  sale_manager_id = 'guillaume'
  first_name1 = 'Guillaume'
  last_name1 = 'MICHON'
  
  item_portal_type = 'Nexedi VPN'
  item_module_name = 'vpn'
  
  item_id_list = ['vpn_1', 'vpn_2', 'vpn_3', 'vpn_4', 'vpn_5', 'vpn_6', 'vpn_7', 'vpn_8', 'vpn_9', 'vpn_10', 'vpn_11', 'vpn_12']
  current_step = {}
  
  currency_list = [ 'EUR', 'USD' ]
  
  organisation_data_list = [ 
        { 'id':'nexedi', 'end_date':DateTime('2004/01/01'), 'currency':'EUR' },
        { 'id':'coramy', 'end_date':DateTime('2003/04/01'), 'currency':'EUR' }
     ]
     
     
  delivery_type = "Purchase Packing List"
  delivery_line_data_list = [
      { 'id':'1_1', 'parent_id':'1', 'items':['vpn_1', 'vpn_2', 'vpn_3', 'vpn_8', 'vpn_9', 'vpn_10', 'vpn_11'], 'date':'2000/01/01', 'source_section':None, 'destination_section':'nexedi' },
      { 'id':'4_1', 'parent_id':'2', 'items':['vpn_4'], 'date':'2002/06/14', 'source_section':None, 'destination_section':'nexedi' },
      { 'id':'4_2', 'parent_id':'3', 'items':['vpn_4'], 'date':'2003/03/15', 'source_section':'nexedi', 'destination_section':'coramy' },
      { 'id':'4_3', 'parent_id':'4', 'items':['vpn_4'], 'date':'2003/06/15', 'source_section':'coramy', 'destination_section':None },
      { 'id':'4_4', 'parent_id':'5', 'items':['vpn_4'], 'date':'2003/12/18', 'source_section':None, 'destination_section':None },
      { 'id':'5_1', 'parent_id':'6', 'items':['vpn_5', 'vpn_6'], 'date':'2000/01/01', 'source_section':None, 
                                                                                'destination_section':'nexedi'},
      { 'id':'5_2', 'parent_id':'7', 'items':['vpn_5', 'vpn_6'], 'date':'2003/03/12', 'source_section':'nexedi', 
                                                                                'destination_section':'coramy' },
      { 'id':'5_3', 'parent_id':'8', 'items':['vpn_5', 'vpn_6'], 'date':'2005/01/01', 'source_section':'coramy', 
                                                                                'destination_section':'nexedi'},
      { 'id':'7_1', 'parent_id':'9', 'items':['vpn_7'], 'date':'2000/01/01', 'source_section':None, 'destination_section':'nexedi' },
      { 'id':'7_2', 'parent_id':'9', 'items':['vpn_7'], 'date':'2003/03/12', 'source_section':'nexedi', 'destination_section':'coramy' },
      { 'id':'7_3', 'parent_id':'9', 'items':['vpn_7'], 'date':'2006/06/23', 'source_section':'coramy', 'destination_section':'nexedi' },
      { 'id':'7_4', 'parent_id':'9', 'items':['vpn_7'], 'date':'2007/02/01', 'source_section':'nexedi', 'destination_section':'coramy' },
        
     ]
     
  
  account_data_list = [
        { 'id':'amortisation_1'  , 'pcg_id':'2/28/281/2811' },
        { 'id':'amortisation_2'  , 'pcg_id':'2/28/281/2812' },
        { 'id':'amortisation_3'  , 'pcg_id':'2/28/281/2813' },
        { 'id':'immobilisation_1', 'pcg_id':'2/21/211'      },
        { 'id':'immobilisation_2', 'pcg_id':'2/21/212'      },
        { 'id':'immobilisation_3', 'pcg_id':'2/21/213'      },
        { 'id':'vat_1'           , 'pcg_id':'4/44/444'      },
        { 'id':'vat_2'           , 'pcg_id':'4/44/445'      },
        { 'id':'vat_3'           , 'pcg_id':'4/44/447'      },
        { 'id':'in_out_1'        , 'pcg_id':'3/32'          },
        { 'id':'in_out_2'        , 'pcg_id':'3/33'          },
        { 'id':'in_out_3'        , 'pcg_id':'3/34'          },
        { 'id':'in_out_4'        , 'pcg_id':'3/35'          },
        { 'id':'in_out_5'        , 'pcg_id':'3/37'          },
        { 'id':'in_out_6'        , 'pcg_id':'3/39'          },
        { 'id':'depreciation_1'  , 'pcg_id':'6/68/681'      },
        { 'id':'depreciation_2'  , 'pcg_id':'6/68/681/6811' },
        { 'id':'depreciation_3'  , 'pcg_id':'6/68/681/6815' } ]
  
  property_list = ( ('value'         , 'AmortisationStartPrice'),
                    ('method'        , 'AmortisationMethod'),
                    ('date'          , 'StopDate'),
                    ('immobilisation', 'Immobilisation'),
                    ('duration'      , 'AmortisationDuration'),
                    ('durability'    , 'Durability'),
                    ('disposal_price', 'DisposalPrice'),
                    ('vat'           , 'Vat'),
                    ('coef'          , 'DegressiveCoefficient'),
                    ('amo_acc'       , 'AmortisationAccount'),
                    ('immo_acc'      , 'ImmobilisationAccount'),
                    ('vat_acc'       , 'VatAccount'),
                    ('in_acc'        , 'InputAccount'),
                    ('out_acc'       , 'OutputAccount'),
                    ('depr_acc'      , 'DepreciationAccount')  )
  
  
  immobilisation_movement_change_list = {
          'linear':     [ {}, {'id':'linear_4', 'duration':24}, {'id':'linear_4', 'disposal_price':10000.} ],
          'complex':    [ {'id':'complex_7', 'date':DateTime("2006/06/24")  + centis} ],
          'actual_use': [ {'id':'actual_use_2', 'date':DateTime('2006/07/01') } ],
          'degressive': [ {'id':'degressive_1', 'duration':96}, {'id':'degressive_1', 'duration':60}, {'id':'degressive_1', 'duration':180} ],
          'solver_3':   [ {'id':'solver_3_1', 'duration':36},
                          {'id':'solver_3_1', 'depr_acc':'account/depreciation_2', 'duration':60},
                          {'id':'solver_3_1', 'date':DateTime('2004/01/01')},
                          {'id':'solver_3_1', 'depr_acc':'account/depreciation_1', 'date':DateTime('2003/01/01')} ],
          }
        
        
  immobilisation_movement_data_list = {
          # coef is optional in case of linear amortisation
          'linear_1' :        { 'value':300000., 'method':'eu/linear', 'date':DateTime("2002/02/01"), 
                                'amo_acc':'amortisation_1', 'vat' : 30000., 'immobilisation': 1, 
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_1',  'in_acc':'in_out_1', 'out_acc' : 'in_out_2',
                                'depr_acc' : 'depreciation_1', 'duration' : 36, 'durability' : 36,
                                'disposal_price' : 0
                              },
          'linear_2' :        { 'date':DateTime("2003/09/14"), 'immobilisation':0, 'item':'vpn_1', 'durability':0 },
          'linear_3' :        { 'value':100000., 'method':'eu/linear', 'date':DateTime("2004/02/01"), 
                                'amo_acc':'amortisation_1', 'vat'  : 10000., 'immobilisation': 1, 
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1',
                                'item':'vpn_1',  'in_acc':'in_out_1', 'out_acc' : 'in_out_2',
                                'depr_acc':'depreciation_1', 'duration' : 12, 'durability' : 12,
                                'disposal_price' : 0
                              },
          'linear_4' :        { 'value': 50000., 'method':'eu/linear', 'date':DateTime("2005/01/01"), 
                                'amo_acc':'amortisation_1', 'vat' :   2000., 'immobilisation': 1, 
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1',
                                'item':'vpn_1',  'in_acc':'in_out_1', 'out_acc' : 'in_out_2',
                                'depr_acc':'depreciation_1', 'duration' : 5, 'durability' : 5,
                                'disposal_price' : 0
                              },
          'degressive_1' :    { 'value':300000., 'method':'fr/degressive', 'date':DateTime("2002/02/01"), 
                                'amo_acc':'amortisation_1', 'vat' :  30000., 'immobilisation': 1, 
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_2', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',
                                'depr_acc' : 'depreciation_1', 'duration' : 120, 'durability' : 120,
                                'disposal_price' : 0
                              },
          'degressive_2' :    { 'date':DateTime("2003/09/14"), 'immobilisation': 0,'item':'vpn_2', 'durability':0 },
          'degressive_3' :    { 'value':169824.22, 'method':'fr/degressive', 'date':DateTime("2004/02/01"), 
                                'amo_acc':'amortisation_1', 'vat' :  16982.422, 'immobilisation': 1, 
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_2', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',
                                'depr_acc' : 'depreciation_1', 'duration' : 96, 'durability' : 96,
                                'disposal_price' : 0
                              },
          'degressive_4' :    { 'value':100000., 'method':'fr/degressive', 'date':DateTime("2005/01/01"),
                                'amo_acc':'amortisation_1', 'vat' :   5000., 'immobilisation': 1, 
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_2', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',
                                'depr_acc' : 'depreciation_1', 'duration' : 85, 'durability' : 85,
                                'disposal_price' : 0
                              },
          'same_day_1' :      { 'date':DateTime("2003/01/01"), 'immobilisation':0, 'item':'vpn_3', 'durability':0 },
          'same_day_2' :      { 'value':100000., 'method':'eu/linear', 'date':DateTime("2003/01/01"), 
                                'amo_acc':'amortisation_1', 'vat' :   5000., 'immobilisation': 1, 
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_3', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',
                                'depr_acc' : 'depreciation_1', 'duration' : 36, 'durability' : 36,
                                'disposal_price' : 0
                              },
          'same_day_3' :      { 'date':DateTime("2003/01/01"), 'immobilisation':0, 'item':'vpn_3', 'durability':0 },
          'same_day_4' :      { 'value':200000., 'method':'eu/linear', 'date':DateTime("2003/01/01"), 
                                'amo_acc':'amortisation_1', 'vat' :   5000., 'immobilisation': 1, 
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_3', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',
                                'depr_acc' : 'depreciation_1', 'duration' : 36 , 'durability' : 36,
                                'disposal_price' : 0
                              },
          'owner_change_1_1' :{ 'value': 30000., 'method':'eu/linear', 'date':DateTime("2001/01/01"), 
                                'amo_acc':'amortisation_1', 'vat' :   3000., 'immobilisation': 1, 
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_4', 'in_acc':'in_out_1',  'out_acc' :'in_out_2', 
                                'depr_acc' : 'depreciation_1', 'duration' : 36, 'durability' : 36,
                                'disposal_price' : 0
                              },
          'owner_change_1_2' :{ 'date':DateTime("2001/03/01"), 'immobilisation':0, 'item':'vpn_4', 'durability':0 },
          'owner_change_1_3' :{ 'value': 20000., 'method':'eu/linear', 'date':DateTime("2002/07/06"), 
                                'amo_acc':'amortisation_1', 'vat' :   2000., 'immobilisation': 1, 
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_4', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',
                                'depr_acc' : 'depreciation_1', 'duration' : 24, 'durability' : 24,
                                'disposal_price' : 0
                              },
          'owner_change_2_1' :{ 'value':100000., 'method':'eu/linear', 'date':DateTime("2001/01/01"), 
                                'amo_acc':'amortisation_1', 'vat' :  10000., 'immobilisation': 1, 
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_5', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',
                                'depr_acc' : 'depreciation_1', 'duration' : 120, 'durability' : 120,
                                'disposal_price' : 0
                              },
          'owner_change_2_2' :{ 'date':DateTime("2002/12/01"), 'immobilisation':0, 'item':'vpn_5', 'durability':0 },
          'owner_change_2_3' :{ 'value': 50000., 'method':'eu/linear', 'date':DateTime("2003/03/12") - 1/25.,
                                'amo_acc':'amortisation_1', 'vat' :   5000., 'immobilisation': 1,
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_5', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',
                                'depr_acc' : 'depreciation_1', 'duration' : 60, 'durability' : 60,
                                'disposal_price' : 0
                              },
          'owner_change_2_4' :{ 'date':DateTime("2004/08/15"), 'immobilisation':0, 'item':'vpn_5', 'durability':0 },
          'owner_change_2_5' :{ 'value': 20000., 'method':'eu/linear', 'date':DateTime("2005/01/01") - 1/25.,
                                'amo_acc':'amortisation_1', 'vat' :   2000., 'immobilisation': 1,
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_5', 'in_acc':'in_out_1',  'out_acc' :'in_out_2', 
                                'depr_acc' : 'depreciation_1', 'duration' : 2, 'durability' : 2,
                                'disposal_price' : 0
                              },
          'owner_change_3_1' :{ 'value':100000., 'method':'eu/linear', 'date':DateTime("2001/01/01"),
                                'amo_acc':'amortisation_1', 'vat' :  10000., 'immobilisation': 1,
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_6', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',
                                'depr_acc' : 'depreciation_1', 'duration' : 120, 'durability' : 120,
                                'disposal_price' : 0
                              },
          'owner_change_3_2' :{ 'date':DateTime("2002/12/01"), 'immobilisation':0, 'item':'vpn_6', 'durability':0 },
          'owner_change_3_3' :{ 'value': 50000., 'method':'eu/linear', 'date':DateTime("2003/03/12") + 1/25.,
                                'amo_acc':'amortisation_1', 'vat' :   5000., 'immobilisation': 1,
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_6', 'in_acc':'in_out_1',  'out_acc' :'in_out_2', 
                                'depr_acc' : 'depreciation_1', 'duration' : 60, 'durability' : 60,
                                'disposal_price' : 0
                              },
          'owner_change_3_4' :{ 'date':DateTime("2004/08/15"), 'immobilisation':0, 'item':'vpn_6', 'durability':0 },
          'owner_change_3_5' :{ 'value': 20000., 'method':'eu/linear', 'date':DateTime("2005/01/01") + 1/25.,
                                'amo_acc':'amortisation_1', 'vat' :   2000., 'immobilisation': 1,
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_6', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',
                                'depr_acc' : 'depreciation_1', 'duration' : 2, 'durability' : 2,
                                'disposal_price' : 0
                              },
          'complex_1' :       { 'value':300000., 'method':'eu/linear', 'date':DateTime("2001/06/12"),
                                'amo_acc':'amortisation_1', 'vat' :  30000., 'immobilisation': 1, 
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_7', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',
                                'depr_acc' : 'depreciation_1', 'duration' : 120, 'durability' : 120,
                                'disposal_price' : 0
                              },
          'complex_2' :       { 'date':DateTime("2001/12/15"), 'immobilisation':0, 'item':'vpn_7', 'durability':0 },
          'complex_3' :       { 'value':284712.33, 'method':'eu/linear', 'date':DateTime("2002/06/01"),
                                'amo_acc':'amortisation_1', 'vat' :  28471.23, 'immobilisation': 1,
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_7', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',
                                'depr_acc' : 'depreciation_1', 'duration' : 114, 'durability' : 114,
                                'disposal_price' : 0
                              },
          'complex_4' :       { 'value':200000., 'method':'fr/degressive', 'date':DateTime("2003/03/12")- 1/25.,
                                'amo_acc':'amortisation_2', 'vat' :  15000., 'immobilisation': 1, 
                                'immo_acc':'immobilisation_2', 'vat_acc':'vat_2', 'coef':2.5,
                                'item':'vpn_7', 'in_acc':'in_out_3',  'out_acc' :'in_out_4',
                                'depr_acc' : 'depreciation_2', 'duration' : 120, 'durability' : 120,
                                'disposal_price' : 0
                              },
          'complex_5' :       { 'date':DateTime("2003/12/30"), 'immobilisation':0, 'item':'vpn_7', 'durability':0 },
          'complex_6' :       { 'value':150000., 'method':'eu/linear', 'date':DateTime("2006/06/24"), 
                                'amo_acc':'amortisation_3', 'vat' :  15000., 'immobilisation': 1,
                                'immo_acc':'immobilisation_3', 'vat_acc':'vat_3', 'coef':2.5,
                                'item':'vpn_7', 'in_acc':'in_out_5',  'out_acc' :'in_out_6',
                                'depr_acc' : 'depreciation_3', 'duration' : 15, 'durability' : 15,
                                'disposal_price' : 0
                              },
          'complex_7' :       { 'date':DateTime("2007/02/01") + 1/25., 'immobilisation':0, 'item':'vpn_7', 'durability':0 },
          'complex_8' :       { 'value':10000., 'method':'fr/linear', 'date':DateTime('2010/04/01'),
                                'amo_acc':'amortisation_1', 'vat': 1000., 'immobilisation': 1,
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1',
                                'item':'vpn_7', 'in_acc':'in_out_1', 'out_acc' : 'in_out_2',
                                'depr_acc' : 'depreciation_1', 'duration' : 24, 'durability' : 100,
                                'disposal_price' : 0
                              },
          'actual_use_1' :    { 'value':100000., 'method':'fr/actual_use', 'date':DateTime("2004/01/01"), 
                                'amo_acc':'amortisation_1', 'vat' :  10000., 'immobilisation': 1,
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_8', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',
                                'depr_acc' : 'depreciation_1', 'duration' : 36, 'durability' : 100,
                                'disposal_price' : 2000
                              },
          'actual_use_2' :    { 'value':10000., 'method':'fr/actual_use', 'date':DateTime("2005/07/01"), 
                                'amo_acc':'amortisation_1', 'vat' :  1000., 'immobilisation': 1,
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_8', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',
                                'depr_acc' : 'depreciation_1', 'duration' : 12, 'durability' : 5,
                                'disposal_price' : 2000
                              },
          'solver_1_1':       { 'value':10000., 'method':'fr/linear', 'date':DateTime("2001/01/01"), 
                                'amo_acc':'amortisation_1', 'vat' :  1000., 'immobilisation': 1,
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_9', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',
                                'depr_acc' : 'depreciation_1', 'duration' : 60, 'durability' : 5,
                                'disposal_price' : 0
                              },
          'solver_2_1':       { 'value':50000., 'method':'fr/linear', 'date':DateTime("2002/01/01"),
                                'amo_acc':'amortisation_1', 'vat' : 5000., 'immobilisation': 1,
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_10', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',
                                'depr_acc' : 'depreciation_1', 'duration' : 60, 'durability' : 5,
                                'disposal_price' : 0
                              },
          'solver_3_1':       { 'value':30000., 'method':'fr/linear', 'date':DateTime("2003/01/01"),
                                'amo_acc':'amortisation_1', 'vat' : 3000., 'immobilisation': 1,
                                'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_11', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',
                                'depr_acc' : 'depreciation_1', 'duration' : 60, 'durability' : 5,
                                'disposal_price' : 0
                              },
                                
            }

            
  immobilisation_movement_list = { 'linear'     :['linear_1', 'linear_2', 'linear_3', 'linear_4'],
                                   'degressive' :['degressive_1', 'degressive_2', 'degressive_3', 'degressive_4'],
                                   'same_day'   :['same_day_1', 'same_day_2', 'same_day_3', 'same_day_4'],
                                   'owner_change_1':['owner_change_1_1', 'owner_change_1_2', 'owner_change_1_3'],
                                   'owner_change_2':['owner_change_2_1', 'owner_change_2_2', 'owner_change_2_3', 'owner_change_2_4',
                                                     'owner_change_2_5'],
                                   'owner_change_3':['owner_change_3_1', 'owner_change_3_2', 'owner_change_3_3', 'owner_change_3_4',
                                                     'owner_change_3_5'],
                                   'complex'    :['complex_1', 'complex_2', 'complex_3', 'complex_4', 'complex_5', 'complex_6',   
                                                  'complex_7', 'complex_8'],
                                   'actual_use' :['actual_use_1', 'actual_use_2'],
                                   'solver_1' : ['solver_1_1'],
                                   'solver_2' : ['solver_2_1'],
                                   'solver_3' : ['solver_3_1'] } 


  validation_switch_list = { 'linear' :     [0,1,0],
                             'degressive' : [0,1,0,3,2],
                             'same_day'   : [0,1,2,3] }
  
  
  simulation_value_list = { 
            'linear': [ 
                              [ # immobilisation start
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':  - 30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 91506.85,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':   91506.85,           'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': - 8493.15,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':   8493.15,            'destination_section':None, 'destination':None, },
                              ], # linear_1
                              
                              [ # immobilisation start
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  91506.85,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91506.85,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  70136.99,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    70136.99,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': - 161643.84,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 152191.78,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    13835.62,          'destination_section':None, 'destination':None, },
                              ], # linear_1, linear_2
                              
                              [ # immobilisation start
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  91506.85,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91506.85,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  70136.99,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    70136.99,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': - 161643.84,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 152191.78,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    13835.62,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  91530.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91530.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   8469.95,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     8469.95,          'destination_section':None, 'destination':None, },
                              ], # linear_1, linear_2, linear_3
                              
                              [ # immobilisation start
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  91506.85,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91506.85,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  70136.99,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    70136.99,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': - 161643.84,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 152191.78,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    13835.62,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  91530.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91530.05,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  91530.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -   9316.94,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':      846.99,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    52000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   2000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    50000.,            'destination_section':None, 'destination':None, },
                              ], # linear_1, linear_2, linear_3, linear_4
                              
                              
                              [ # immobilisation start
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  91530.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91530.05,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  91530.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -   9316.94,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':      846.99,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    52000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   2000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    50000.,            'destination_section':None, 'destination':None, },
                              ], # linear_2, linear_3, linear_4
                              
                              [ # immobilisation start
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  91530.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91530.05,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  91530.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -   9316.94,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':      846.99,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    52000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   2000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    50000.,            'destination_section':None, 'destination':None, },
                              ], # linear_3, linear_4
                              
                              [ # immobilisation start
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  91506.85,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91506.85,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': - 100000.  ,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':   100000.  ,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   8469.95,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     8469.95,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': - 199976.79,          'destination_section':None, 'destination':None, }, 
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 110025.53,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    10002.32,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 91530.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91530.05,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  91530.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -   9316.94,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':      846.99,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    52000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   2000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    50000.,            'destination_section':None, 'destination':None, },
                              ], # linear_1, linear_3, linear_4
                              
                              [ # immobilisation start
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  91506.85,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91506.85,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': - 100000.  ,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':   100000.  ,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   8469.95,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     8469.95,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': - 199976.79,          'destination_section':None, 'destination':None, }, 
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 110025.53,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    10002.32,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 91530.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91530.05,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  91530.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -   9316.94,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':      846.99,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    52000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   2000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    50000.,            'destination_section':None, 'destination':None, },
                              ], # linear_1, linear_3, linear_4 => reexpand
                              
                              [ # immobilisation start
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  91506.85,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91506.85,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': - 100000.  ,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':   100000.  ,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   8469.95,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     8469.95,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': - 199976.79,          'destination_section':None, 'destination':None, }, 
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 110025.53,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    10002.32,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 91530.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91530.05,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  91530.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -   9316.94,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':      846.99,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    52000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   2000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  25000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    25000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  25000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    25000.,            'destination_section':None, 'destination':None, },
                              ], # linear_1, linear_3, linear_4 => reexpand, linear_4 modified
                              
                              [ # immobilisation start
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  91506.85,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91506.85,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': - 100000.  ,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':   100000.  ,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   8469.95,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     8469.95,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': - 199976.79,          'destination_section':None, 'destination':None, }, 
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 110025.53,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    10002.32,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 91530.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91530.05,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  91530.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -   9316.94,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':      846.99,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    52000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   2000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  20000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    20000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  20000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    20000.,            'destination_section':None, 'destination':None, },
                                  # immobilisation end
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':    50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  40000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -  10400.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':      400.,            'destination_section':None, 'destination':None, },
                              ], # linear_1, linear_3, linear_4 => reexpand, linear_4 modified for the second time
                              
                      ],
                        
            'degressive': [ 
                              [ # immobilisation start
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':  - 30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  57812.50,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    57812.50,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  43359.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    43359.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  32519.53,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    32519.53,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  24389.65,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    24389.65,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  18292.24,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    18292.24,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None, },
                              ], # degressive_1
                              
                              [ # immobilisation start
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  43359.38,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    43359.38,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': - 112109.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 206679.69,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    18789.06,          'destination_section':None, 'destination':None, },
                              ], # degressive_1, degressive_2
                              
                              [ # immobilisation start
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  43359.38,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    43359.38,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': - 112109.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 206679.69,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    18789.06,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 169824.22,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   186806.64,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  16982.42,          'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  48647.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    48647.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  37867.71,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    37867.71,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  26034.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    26034.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  17898.41,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    17898.41,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  12305.16,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    12305.16,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   9023.78,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     9023.78,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   9023.78,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     9023.78,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   9023.78,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     9023.78,          'destination_section':None, 'destination':None, },
                              ], # degressive_1, degressive_2, degressive_3
                              
                              [ # immobilisation start
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  43359.38,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    43359.38,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': - 112109.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 206679.69,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/09/14'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    18789.06,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 169824.22,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   186806.64,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  16982.42,          'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  48647.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    48647.56,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   169824.22,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  48647.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 133294.32,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    12117.67,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   105000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   5000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  31250.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    31250.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  21484.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    21484.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  14770.51,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    14770.51,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  10154.72,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10154.72,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6981.37,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6981.37,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5119.67,            'destination_section':None, 'destination':None, },
                              ], # degressive_1, degressive_2, degressive_3, degressive_4
                              
                              
                              [ # immobilisation start
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 169824.22,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   186806.64,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  16982.42,          'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  48647.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    48647.56,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   169824.22,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  48647.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 133294.32,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    12117.67,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   105000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   5000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  31250.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    31250.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  21484.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    21484.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  14770.51,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    14770.51,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  10154.72,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10154.72,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6981.37,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6981.37,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5119.67,            'destination_section':None, 'destination':None, },
                              ], # degressive_2, degressive_3, degressive_4
                              
                              [ # immobilisation start
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 169824.22,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   186806.64,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  16982.42,          'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  48647.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    48647.56,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   169824.22,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  48647.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 133294.32,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    12117.67,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   105000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   5000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  31250.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    31250.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  21484.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    21484.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  14770.51,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    14770.51,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  10154.72,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10154.72,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6981.37,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6981.37,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5119.67,            'destination_section':None, 'destination':None, },
                              ], # degressive_3, degressive_4
                              
                              [ # immobilisation start
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  57812.50,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    57812.50,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   3613.28,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     3613.28,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':'nexedi', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   186806.64,          'destination_section':'nexedi', 'destination':'in_out_2', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  16982.42,          'destination_section':'nexedi', 'destination':'vat_1', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':   130175.78,            'destination_section':'nexedi', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  48647.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    48647.56,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   169824.22,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  48647.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 133294.32,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    12117.67,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   105000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   5000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  31250.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    31250.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  21484.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    21484.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  14770.51,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    14770.51,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  10154.72,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10154.72,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6981.37,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6981.37,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   5119.67,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5119.67,            'destination_section':None, 'destination':None, },
                              ], # degressive_1, degressive_3, degressive_4
                              
                              [ # immobilisation start
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  57812.50,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    57812.50,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   3613.28,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     3613.28,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':'nexedi', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   186806.64,          'destination_section':'nexedi', 'destination':'in_out_2', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  16982.42,          'destination_section':'nexedi', 'destination':'vat_1', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':   130175.78,            'destination_section':'nexedi', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  48647.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    48647.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  37867.71,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    37867.71,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  26034.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    26034.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  17898.41,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    17898.41,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  12305.16,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    12305.16,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   9023.78,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     9023.78,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   9023.78,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     9023.78,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   9023.78,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     9023.78,          'destination_section':None, 'destination':None, },
                                  
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                              ], # degressive_1, degressive_3, reexpand
                              
                              [ # immobilisation start
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':  - 30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  57812.50,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    57812.50,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  43359.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    43359.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  32519.53,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    32519.53,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  24389.65,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    24389.65,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  18292.24,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    18292.24,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None, },
                                  
                                # immobilisation end and start
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -      0.,            'destination_section':'nexedi', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':        0.,            'destination_section':'nexedi', 'destination':'in_out_2', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -      0.,            'destination_section':'nexedi', 'destination':'vat_1', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':'nexedi', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },

                              ], # degressive_1, reexpand

                              [ # immobilisation start
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':  - 30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  57812.50,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    57812.50,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  43359.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    43359.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  32519.53,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    32519.53,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  24389.65,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    24389.65,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  18292.24,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    18292.24,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None,},
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None,},
                                  
                                # immobilisation end and start
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -      0.,            'destination_section':'nexedi', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':        0.,            'destination_section':'nexedi', 'destination':'in_out_2', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -      0.,            'destination_section':'nexedi', 'destination':'vat_1', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':'nexedi', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                              
                                # Correction
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': - 17187.5,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':   17187.5,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  9082.03,           'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    9082.03,           'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   2630.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     2630.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':      901.41,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -    901.41,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':     2652.19,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -   2652.19,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':     2351.44,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -   2351.44,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   2221.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     2221.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   2221.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     2221.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':    13719.18,          'destination_section':None, 'destination':None,},
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  13719.18,          'destination_section':None, 'destination':None,},
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':    13719.18,          'destination_section':None, 'destination':None,},
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  13719.18,          'destination_section':None, 'destination':None,},
                              ], # degressive_1, reexpand after validation
                              
                              [ # immobilisation start
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':  - 30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  57812.50,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    57812.50,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  43359.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    43359.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  32519.53,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    32519.53,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  24389.65,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    24389.65,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  18292.24,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    18292.24,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None,
                                  'profit_quantity': - 13719.18 },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None,
                                  'profit_quantity':   13719.18 },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None,
                                  'profit_quantity': - 13719.18 },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None,
                                  'profit_quantity':   13719.18 },
                                  
                                # immobilisation end and start
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -      0.,            'destination_section':'nexedi', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':        0.,            'destination_section':'nexedi', 'destination':'in_out_2', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -      0.,            'destination_section':'nexedi', 'destination':'vat_1', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':'nexedi', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                              
                                # Correction
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': - 17187.5,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':   17187.5,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  9082.03,           'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    9082.03,           'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   2630.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     2630.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':      901.41,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -    901.41,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':     2652.19,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -   2652.19,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':     2351.44,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -   2351.44,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   2221.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     2221.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   2221.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     2221.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':    13719.18,          'destination_section':None, 'destination':None,
                                  'profit_quantity':   13719.18 },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  13719.18,          'destination_section':None, 'destination':None,
                                  'profit_quantity': - 13719.18 },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':    13719.18,          'destination_section':None, 'destination':None,
                                  'profit_quantity':   13719.18 },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  13719.18,          'destination_section':None, 'destination':None,
                                  'profit_quantity': - 13719.18 },
                                  
                                # Correction 2
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   51562.5,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     51562.5,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   14355.47,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     14355.47,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':      5364.99,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -    5364.99,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':     11305.62,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -   11305.62,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':      1424.96,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -    1424.96,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':     15940.80,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -   15940.80,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':     15940.80,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -   15940.80,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':     15940.80,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -   15940.80,         'destination_section':None, 'destination':None, },
                              ], # degressive_1, reexpand after second validation
                              
                              [ # immobilisation start
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':  - 30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    68750.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  57812.50,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    57812.50,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  43359.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    43359.38,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  32519.53,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    32519.53,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  24389.65,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    24389.65,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  18292.24,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    18292.24,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None,
                                  'profit_quantity': - 13719.18 },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None,
                                  'profit_quantity':   13719.18 },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  13719.18,            'destination_section':None, 'destination':None,
                                  'profit_quantity': - 13719.18 },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    13719.18,            'destination_section':None, 'destination':None,
                                  'profit_quantity':   13719.18 },
                                  
                                # immobilisation end and start
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -      0.,            'destination_section':'nexedi', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':        0.,            'destination_section':'nexedi', 'destination':'in_out_2', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -      0.,            'destination_section':'nexedi', 'destination':'vat_1', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':'nexedi', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                              
                                # Correction
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': - 17187.5,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':   17187.5,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  9082.03,           'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    9082.03,           'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   2630.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     2630.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':      901.41,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -    901.41,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':     2652.19,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -   2652.19,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':     2351.44,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -   2351.44,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   2221.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     2221.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   2221.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     2221.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':    13719.18,          'destination_section':None, 'destination':None,
                                  'profit_quantity':   13719.18 },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  13719.18,          'destination_section':None, 'destination':None,
                                  'profit_quantity': - 13719.18 },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':    13719.18,          'destination_section':None, 'destination':None,
                                  'profit_quantity':   13719.18 },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  13719.18,          'destination_section':None, 'destination':None,
                                  'profit_quantity': - 13719.18 },

                                # Correction 2
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':     40104.17,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -   40104.17,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':     24533.42,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -   24533.42,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':     10689.06,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -   10689.06,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':      2200.68,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -    2200.68,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -    2777.08,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':      2777.08,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -    4487.98,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':      4487.98,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -    1083.18,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':      1083.18,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':      1754.15,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -    1754.15,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   11822.21,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     11822.21,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -    9851.84,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':      9851.84,         'destination_section':None, 'destination':None, },
                                  
                                # New annuities
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -    9851.84,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':      9851.84,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2014/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -    9851.84,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2014/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':      9851.84,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2015/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -    9851.84,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2015/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':      9851.84,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2016/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -    9851.84,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2016/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':      9851.84,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2017/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -    9851.84,         'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2017/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':      9851.84,         'destination_section':None, 'destination':None, },
                                
                              ], # degressive_1, reexpand after change after second validation
                        
                          ],
                          
            'same_day': [ 
                              [ ],
                              [ # immobilisation start
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   105000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   5000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 33333.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    33333.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 33333.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    33333.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 33333.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    33333.33,          'destination_section':None, 'destination':None, },
                               ], # same_day_1, same_day_2
                               
                              [ # immobilisation start
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   105000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   5000.,            'destination_section':None, 'destination':None, },
                              ], # same_day_1, same_day_2, same_day_3
                              
                              [ # immobilisation start
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   105000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   5000.,            'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 200000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   205000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   5000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 66666.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    66666.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 66666.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    66666.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 66666.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    66666.67,          'destination_section':None, 'destination':None, },
                              ], # same_day_1, same_day_2, same_day_3, same_day_4
                              [],
                              [],
                              [],
                              [] # These four empty lists are here to pass the Simulation verification
                        ],
                       
      'owner_change_1': [ 
                              [ ],
                              [ ],
                              [ # immobilisation start
                                { 'date':DateTime('2002/07/06'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  20000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/07/06'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    22000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/07/06'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   2000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  4904.11,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     4904.11,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  2000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     2000.,            'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2003/03/15'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value': -  20000.,            'destination_section':'nexedi', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2003/03/15'), 'source_section':'coramy', 'source':'in_out_2',
                                  'value':    14405.48,          'destination_section':'nexedi', 'destination':'in_out_2', },
                                { 'date':DateTime('2003/03/15'), 'source_section':'coramy', 'source':'vat_1',
                                  'value': -   1309.59,          'destination_section':'nexedi', 'destination':'vat_1', },
                                { 'date':DateTime('2003/03/15'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     6904.11,          'destination_section':'nexedi', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -   457.15,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':      457.15,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  9815.2,           'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     9815.2,           'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  2823.55,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     2823.55,          'destination_section':None, 'destination':None, },
                                
                              ]                                
                              
                         ],
       
       'owner_change_2': [ 
                              [ # immobilisation start
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  1917.81,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     1917.81,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':'nexedi', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'in_out_2',
                                  'value':    85890.41,          'destination_section':'nexedi', 'destination':'in_out_2', },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'vat_1',
                                  'value': -   7808.22,          'destination_section':'nexedi', 'destination':'vat_1', },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    21917.81,          'destination_section':'nexedi', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -   545.84,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':      545.84,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  9961.55,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     9961.55,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  7505.28,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     7505.28,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  78082.19,          'destination_section':'coramy', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value':    66076.47,          'destination_section':'coramy', 'destination':'in_out_2', },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   6006.95,          'destination_section':'coramy', 'destination':'vat_1', },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    18012.67,          'destination_section':'coramy', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10011.59,          'destination_section':None, 'destination':None, },
                              ], # owner_change_2_1
                              
                              [ # immobilisation start
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  9150.68,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     9150.68,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  19150.68,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -  88934.25,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':     8084.932,         'destination_section':None, 'destination':None, },
                              ], # owner_change_2_1, owner_change_2_2
                              
                              [ # immobilisation start
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  9150.68,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     9150.68,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  19150.68,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -  88934.25,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':     8084.93,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value': -  50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'in_out_1',
                                  'value':    55000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'vat_1',
                                  'value': -   5000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -   547.95,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':      547.95,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  7534.25,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     7534.25,            'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  50000.,            'destination_section':'coramy', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value':    35109.59,          'destination_section':'coramy', 'destination':'in_out_2', },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   3191.78,          'destination_section':'coramy', 'destination':'vat_1', },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    18082.19,          'destination_section':'coramy', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10086.58,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10086.58,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10086.58,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10086.58,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10086.58,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10086.58,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  1658.07,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     1658.07,          'destination_section':None, 'destination':None, },
                                
                              ], # owner_change_2_1, owner_change_2_2, owner_change_2_3
                                
                              [ # immobilisation start
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  9150.68,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     9150.68,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  19150.68,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -  88934.25,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':     8084.93,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value': -  50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'in_out_1',
                                  'value':    55000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'vat_1',
                                  'value': -   5000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -   547.95,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':      547.95,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  3726.03,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     3726.03,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2004/08/15'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value':    50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/08/15'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value': -  14273.97,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/08/15'), 'source_section':'coramy', 'source':'in_out_2',
                                  'value': -  39298.63,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/08/15'), 'source_section':'coramy', 'source':'vat_1',
                                  'value':     3572.60,          'destination_section':None, 'destination':None, },
                                
                              ], # owner_change_2_1, owner_change_2_2, owner_change_2_3, owner_change_2_4
                              
                              [ # immobilisation start
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  9150.68,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     9150.68,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  19150.68,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -  88934.25,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':     8084.93,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value': -  50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'in_out_1',
                                  'value':    55000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'vat_1',
                                  'value': -   5000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -   547.95,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':      547.95,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  3726.03,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     3726.03,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2004/08/15'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value':    50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/08/15'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value': -  14273.97,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/08/15'), 'source_section':'coramy', 'source':'in_out_2',
                                  'value': -  39298.63,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/08/15'), 'source_section':'coramy', 'source':'vat_1',
                                  'value':     3572.60,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  20000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    22000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   2000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 20000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    20000.,            'destination_section':None, 'destination':None, },
                                
                              ], # owner_change_2_1, owner_change_2_2, owner_change_2_3, owner_change_2_4, owner_change_2_5
                         ],
                         
       'owner_change_3': [ 
                              [ # immobilisation start
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  1917.81,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     1917.81,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':'nexedi', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'in_out_2',
                                  'value':    85890.41,          'destination_section':'nexedi', 'destination':'in_out_2', },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'vat_1',
                                  'value': -   7808.22,          'destination_section':'nexedi', 'destination':'vat_1', },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    21917.81,          'destination_section':'nexedi', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -   545.84,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':      545.84,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  9961.55,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     9961.55,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  7505.28,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     7505.28,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  78082.19,          'destination_section':'coramy', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value':    66076.47,          'destination_section':'coramy', 'destination':'in_out_2', },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   6006.95,          'destination_section':'coramy', 'destination':'vat_1', },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    18012.67,          'destination_section':'coramy', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10011.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10011.59,          'destination_section':None, 'destination':None, },
                              ], # owner_change_3_1
                              
                              [ # immobilisation start
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  9150.68,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     9150.68,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  19150.68,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -  88934.25,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':     8084.932,         'destination_section':None, 'destination':None, },
                              ], # owner_change_3_1, owner_change_3_2
                              
                              [ # immobilisation start
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  9150.68,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     9150.68,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  19150.68,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -  88934.25,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':     8084.93,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value': -  50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'in_out_1',
                                  'value':    55000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'vat_1',
                                  'value': -   5000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -   547.95,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':      547.95,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  7534.25,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     7534.25,            'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  50000.,            'destination_section':'coramy', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value':    35109.59,          'destination_section':'coramy', 'destination':'in_out_2', },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   3191.78,          'destination_section':'coramy', 'destination':'vat_1', },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    18082.19,          'destination_section':'coramy', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10086.58,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10086.58,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10086.58,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10086.58,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10086.58,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10086.58,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  1658.07,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     1658.07,          'destination_section':None, 'destination':None, },
                              ], # owner_change_3_1, owner_change_3_2, owner_change_3_3
                                
                              [ # immobilisation start
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  9150.68,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     9150.68,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  19150.68,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -  88934.25,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':     8084.93,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value': -  50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'in_out_1',
                                  'value':    55000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'vat_1',
                                  'value': -   5000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -   547.95,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':      547.95,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  3726.03,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     3726.03,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2004/08/15'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value':    50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/08/15'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value': -  14273.97,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/08/15'), 'source_section':'coramy', 'source':'in_out_2',
                                  'value': -  39298.63,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/08/15'), 'source_section':'coramy', 'source':'vat_1',
                                  'value':     3572.60,          'destination_section':None, 'destination':None, },
                                
                              ], # owner_change_3_1, owner_change_3_2, owner_change_3_3, owner_change_3_4
                              
                              [ # immobilisation start
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  9150.68,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     9150.68,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  19150.68,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -  88934.25,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':     8084.93,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value': -  50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'in_out_1',
                                  'value':    55000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'vat_1',
                                  'value': -   5000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -   547.95,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':      547.95,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  3726.03,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     3726.03,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2004/08/15'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value':    50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/08/15'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value': -  14273.97,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/08/15'), 'source_section':'coramy', 'source':'in_out_2',
                                  'value': -  39298.63,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/08/15'), 'source_section':'coramy', 'source':'vat_1',
                                  'value':     3572.60,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  20000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    22000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   2000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 20000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    20000.,            'destination_section':None, 'destination':None, },
                                
                              ], # owner_change_3_1, owner_change_3_2, owner_change_3_3, owner_change_3_4, owner_change_3_5
                         ],
                         
                         
       'complex': [ 
                              [ # immobilisation start
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 16684.93,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    16684.93,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 30000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    30000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  5753.42,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5753.42,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':'nexedi', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'in_out_2',
                                  'value':   272317.81,          'destination_section':'nexedi', 'destination':'in_out_2', },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'vat_1',
                                  'value': -  24756.16,         'destination_section':'nexedi', 'destination':'vat_1', },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    52438.36,          'destination_section':'nexedi', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  1643.84,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     1643.84,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 30000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    30000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 30000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    30000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 30000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    30000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  6821.92,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     6821.92,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 247561.64,          'destination_section':'coramy', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value':   164005.48,          'destination_section':'coramy', 'destination':'in_out_2', },
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  14909.59,         'destination_section':'coramy', 'destination':'vat_1', },
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    98465.75,          'destination_section':'coramy', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 15685.70,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    15685.70,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  2532.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     2532.59,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value': - 149095.89,          'destination_section':'nexedi', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'in_out_2',
                                  'value':   143965.36,          'destination_section':'nexedi', 'destination':'in_out_2', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'vat_1',
                                  'value': -  13087.76,          'destination_section':'nexedi', 'destination':'vat_1', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    18218.29,          'destination_section':'nexedi', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  4796.14,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     4796.14,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29671.01,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29671.01,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29671.01,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29671.01,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29671.01,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29671.01,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29671.01,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29671.01,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  7397.43,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     7397.43,          'destination_section':None, 'destination':None, },
                                
                              ], # complex_1
                              
                              [ # immobilisation start
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 15287.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    15287.67,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  15287.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 313183.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':     28471.23,          'destination_section':None, 'destination':None, },
                              ], # complex_1, complex_2
                              
                              [ # immobilisation start
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 15287.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    15287.67,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  15287.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 313183.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':     28471.23,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 284712.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   313183.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  28471.23,          'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 17568.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    17568.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  5746.79,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5746.79,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value': - 284712.33,          'destination_section':'nexedi', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'in_out_2',
                                  'value':   287536.46,          'destination_section':'nexedi', 'destination':'in_out_2', },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'vat_1',
                                  'value': -  26139.68,         'destination_section':'nexedi', 'destination':'vat_1', },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    23315.54,          'destination_section':'nexedi', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  1636.29,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     1636.29,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29862.23,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29862.23,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29862.23,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29862.23,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29862.23,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29862.23,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  6790.59,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     6790.59,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 261396.79,          'destination_section':'coramy', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value':   179721.54,          'destination_section':'coramy', 'destination':'in_out_2', },
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  16338.32,         'destination_section':'coramy', 'destination':'vat_1', },
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    98013.57,          'destination_section':'coramy', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 15622.30,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    15622.30,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  2522.35,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     2522.35,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value': - 163383.22,          'destination_section':'nexedi', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'in_out_2',
                                  'value':   159762.42,          'destination_section':'nexedi', 'destination':'in_out_2', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'vat_1',
                                  'value': -  14523.86,          'destination_section':'nexedi', 'destination':'vat_1', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    18144.65,          'destination_section':'nexedi', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  4776.52,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     4776.52,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29549.65,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29549.65,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29549.65,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29549.65,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29549.65,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29549.65,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29549.65,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29549.65,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 22263.44,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    22263.44,          'destination_section':None, 'destination':None, },
                                
                               ], # complex_1, complex_2, complex_3
                               
                              [ # immobilisation start
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 15287.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    15287.67,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  15287.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 313183.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':     28471.23,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 284712.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   313183.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  28471.23,          'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 17568.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    17568.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  5746.79,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5746.79,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   284712.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  23315.54,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 287536.46,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    26139.68,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'immobilisation_2',
                                  'value': - 200000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'in_out_3',
                                  'value':   215000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'vat_2',
                                  'value': -  15000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  -  4166.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':     4166.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  - 48958.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':    48958.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  - 36718.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':    36718.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  - 27539.06,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':    27539.06,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  -  5163.57,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':     5163.57,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'immobilisation_2',
                                  'value': - 200000.,            'destination_section':'coramy', 'destination':'immobilisation_2', },
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'in_out_4',
                                  'value':    83262.63,          'destination_section':'coramy', 'destination':'in_out_4', },
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'vat_2',
                                  'value': -   5809.02,          'destination_section':'coramy', 'destination':'vat_2', },
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'amortisation_2',
                                  'value':   122546.39,          'destination_section':'coramy', 'destination':'amortisation_2', },
                                # annuities
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_2',
                                  'value':  - 16136.17,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_2',
                                  'value':    16136.17,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_2',
                                  'value':  -  1824.92,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_2',
                                  'value':     1824.92,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'immobilisation_2',
                                  'value': -  77453.61,          'destination_section':'nexedi', 'destination':'immobilisation_2', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'in_out_4',
                                  'value':    63954.46,          'destination_section':'nexedi', 'destination':'in_out_4', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'vat_2',
                                  'value': -   4461.94,          'destination_section':'nexedi', 'destination':'vat_2', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':    17961.09,          'destination_section':'nexedi', 'destination':'amortisation_2', },
                                # annuities
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  -  3541.22,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':     3541.22,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  - 19982.61,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':    19982.61,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  - 12845.96,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':    12845.96,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  -  8258.12,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':     8258.12,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  -  5308.79,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':     5308.79,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  -  4777.91,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':     4777.91,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  -  4777.91,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2013/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':     4777.91,          'destination_section':None, 'destination':None, },
                                
                               ], # complex_1, complex_2, complex_3, complex_4
                               
                              [ # immobilisation start
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 15287.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    15287.67,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  15287.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 313183.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':     28471.23,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 284712.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   313183.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  28471.23,          'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 17568.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    17568.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  5746.79,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5746.79,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   284712.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  23315.54,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 287536.46,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    26139.68,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'immobilisation_2',
                                  'value': - 200000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'in_out_3',
                                  'value':   215000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'vat_2',
                                  'value': -  15000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  -  4166.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':     4166.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  - 36718.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':    36718.75,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'immobilisation_2',
                                  'value':   200000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value': -  40885.42,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'in_out_4',
                                  'value': - 171048.18,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'vat_2',
                                  'value':    11933.59,          'destination_section':None, 'destination':None, },
                                
                               ], # complex_1, complex_2, complex_3, complex_4, complex_5
                               
                              [ # immobilisation start
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 15287.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    15287.67,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  15287.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 313183.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':     28471.23,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 284712.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   313183.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  28471.23,          'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 17568.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    17568.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  5746.79,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5746.79,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   284712.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  23315.54,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 287536.46,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    26139.68,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'immobilisation_2',
                                  'value': - 200000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'in_out_3',
                                  'value':   215000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'vat_2',
                                  'value': -  15000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  -  4166.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':     4166.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  - 36718.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':    36718.75,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'immobilisation_2',
                                  'value':   200000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value': -  40885.42,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'in_out_4',
                                  'value': - 171048.18,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'vat_2',
                                  'value':    11933.59,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2006/06/24'), 'source_section':'nexedi', 'source':'immobilisation_3',
                                  'value': - 150000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/06/24'), 'source_section':'nexedi', 'source':'in_out_5',
                                  'value':   165000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/06/24'), 'source_section':'nexedi', 'source':'vat_3',
                                  'value': -  15000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_3',
                                  'value':  - 62691.47,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_3',
                                  'value':    62691.47,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_3',
                                  'value':  - 10175.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_3',
                                  'value':    10175.05,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'immobilisation_3',
                                  'value': - 150000.,            'destination_section':'nexedi', 'destination':'immobilisation_3', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'in_out_6',
                                  'value':    84846.83,          'destination_section':'nexedi', 'destination':'in_out_6', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'vat_3',
                                  'value': -   7713.35,          'destination_section':'nexedi', 'destination':'vat_3', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'amortisation_3',
                                  'value':    72866.52,          'destination_section':'nexedi', 'destination':'amortisation_3', },
                                # annuities
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'depreciation_3',
                                  'value':  - 18805.27,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'amortisation_3',
                                  'value':    18805.27,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/04/01'), 'source_section':'coramy', 'source':'depreciation_3',
                                  'value':  - 58328.21,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/04/01'), 'source_section':'coramy', 'source':'amortisation_3',
                                  'value':    58328.21,          'destination_section':None, 'destination':None, },
                                
                               ], # complex_1, complex_2, complex_3, complex_4, complex_5, complex_6
                               
                               
                              [ # immobilisation start
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 15287.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    15287.67,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  15287.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 313183.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':     28471.23,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 284712.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   313183.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  28471.23,          'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 17568.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    17568.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  5746.79,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5746.79,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   284712.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  23315.54,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 287536.46,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    26139.68,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'immobilisation_2',
                                  'value': - 200000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'in_out_3',
                                  'value':   215000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'vat_2',
                                  'value': -  15000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  -  4166.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':     4166.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  - 36718.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':    36718.75,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'immobilisation_2',
                                  'value':   200000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value': -  40885.42,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'in_out_4',
                                  'value': - 171048.18,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'vat_2',
                                  'value':    11933.59,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2006/06/24'), 'source_section':'nexedi', 'source':'immobilisation_3',
                                  'value': - 150000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/06/24'), 'source_section':'nexedi', 'source':'in_out_5',
                                  'value':   165000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/06/24'), 'source_section':'nexedi', 'source':'vat_3',
                                  'value': -  15000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_3',
                                  'value':  - 62691.47,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_3',
                                  'value':    62691.47,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_3',
                                  'value':  - 10175.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_3',
                                  'value':    10175.05,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2007/02/01'), 'source_section':'nexedi', 'source':'immobilisation_3',
                                  'value':   150000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/02/01'), 'source_section':'nexedi', 'source':'in_out_6',
                                  'value': -  84846.83,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/02/01'), 'source_section':'nexedi', 'source':'vat_3',
                                  'value':     7713.35,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/02/01'), 'source_section':'nexedi', 'source':'amortisation_3',
                                  'value': -  72866.52,          'destination_section':None, 'destination':None, },
                                
                               ], # complex_1, complex_2, complex_3, complex_4, complex_5, complex_6, complex_7
                               
                               [ # immobilisation start
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 15287.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    15287.67,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  15287.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 313183.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':     28471.23,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 284712.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   313183.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  28471.23,          'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 17568.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    17568.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  5746.79,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5746.79,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   284712.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  23315.54,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 287536.46,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    26139.68,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'immobilisation_2',
                                  'value': - 200000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'in_out_3',
                                  'value':   215000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'vat_2',
                                  'value': -  15000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  -  4166.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':     4166.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  - 36718.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':    36718.75,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'immobilisation_2',
                                  'value':   200000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value': -  40885.42,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'in_out_4',
                                  'value': - 171048.18,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'vat_2',
                                  'value':    11933.59,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2006/06/24'), 'source_section':'nexedi', 'source':'immobilisation_3',
                                  'value': - 150000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/06/24'), 'source_section':'nexedi', 'source':'in_out_5',
                                  'value':   165000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/06/24'), 'source_section':'nexedi', 'source':'vat_3',
                                  'value': -  15000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_3',
                                  'value':  - 62691.47,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_3',
                                  'value':    62691.47,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_3',
                                  'value':  - 10175.05,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_3',
                                  'value':    10175.05,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2007/02/01'), 'source_section':'nexedi', 'source':'immobilisation_3',
                                  'value':   150000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/02/01'), 'source_section':'nexedi', 'source':'in_out_6',
                                  'value': -  84846.83,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/02/01'), 'source_section':'nexedi', 'source':'vat_3',
                                  'value':     7713.35,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/02/01'), 'source_section':'nexedi', 'source':'amortisation_3',
                                  'value': -  72866.52,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2010/04/01'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/04/01'), 'source_section':'coramy', 'source':'in_out_1',
                                  'value':    11000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/04/01'), 'source_section':'coramy', 'source':'vat_1',
                                  'value': -  1000.,             'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2011/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  5000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     5000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  5000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     5000.,            'destination_section':None, 'destination':None, },
                               ], # complex_1, complex_2, complex_3, complex_4, complex_5, complex_6, complex_7, complex_8

                               [ # immobilisation start
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   330000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 15287.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    15287.67,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   300000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  15287.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 313183.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':     28471.23,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 284712.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   313183.56,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  28471.23,          'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 17568.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    17568.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  5746.79,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5746.79,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   284712.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  23315.54,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 287536.46,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    26139.68,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'immobilisation_2',
                                  'value': - 200000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'in_out_3',
                                  'value':   215000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'vat_2',
                                  'value': -  15000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  -  4166.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':     4166.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_2',
                                  'value':  - 36718.75,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value':    36718.75,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'immobilisation_2',
                                  'value':   200000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'amortisation_2',
                                  'value': -  40885.42,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'in_out_4',
                                  'value': - 171048.18,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'source':'vat_2',
                                  'value':    11933.59,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2006/06/24'), 'source_section':'nexedi', 'source':'immobilisation_3',
                                  'value': - 150000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/06/24'), 'source_section':'nexedi', 'source':'in_out_5',
                                  'value':   165000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/06/24'), 'source_section':'nexedi', 'source':'vat_3',
                                  'value': -  15000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_3',
                                  'value':    0.,                'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_3',
                                  'value':    0.,                'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_3',
                                  'value':    0.,                'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_3',
                                  'value':    0.,                'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2007/02/01'), 'source_section':'nexedi', 'source':'amortisation_3',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/06/24'), 'source_section':'nexedi', 'source':'immobilisation_3',
                                  'value':   150000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/06/24'), 'source_section':'nexedi', 'source':'in_out_6',
                                  'value': - 165000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/06/24'), 'source_section':'nexedi', 'source':'vat_3',
                                  'value':    15000.,          'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2010/04/01'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/04/01'), 'source_section':'coramy', 'source':'in_out_1',
                                  'value':    11000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/04/01'), 'source_section':'coramy', 'source':'vat_1',
                                  'value': -  1000.,             'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2011/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  5000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     5000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  5000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     5000.,            'destination_section':None, 'destination':None, },
                               ], # complex_1, complex_2, complex_3, complex_4, complex_5, complex_6, complex_7, complex_8 => reexpand, complex_7 modified
                 ],
                 
            'actual_use' : [
                               [
                                # immobilisation start
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 32666.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    32666.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 32666.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    32666.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 32666.67,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    32666.67,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -   2200.,            'destination_section':None, 'destination':None },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':      200.,            'destination_section':None, 'destination':None },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  98000.,            'destination_section':None, 'destination':None },
                               ], # actual_use_1
                               
                               [
                                # immobilisation start
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 62237.18,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    62237.18,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 30862.82,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    30862.82,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/07/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/07/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -   7590.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/07/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':      690.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/07/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  93100.,            'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2005/07/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/07/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    11000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/07/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   1000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   4032.88,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     4032.88,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   3967.12,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     3967.12,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -   2200.,            'destination_section':None, 'destination':None },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':      200.,            'destination_section':None, 'destination':None },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -   8000.,            'destination_section':None, 'destination':None },
                                ], # actual_use_1, actual_use_2
                               [
                                # immobilisation start
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 37301.32,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    37301.32,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 37301.32,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    37301.32,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 18497.37,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    18497.37,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2006/07/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/07/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -   7590.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/07/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':      690.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/07/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  93100.,            'destination_section':None, 'destination':None, },
                                # immobilisation start
                                { 'date':DateTime('2006/07/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/07/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    11000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/07/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   1000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   4032.88,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     4032.88,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   3967.12,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     3967.12,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -   2200.,            'destination_section':None, 'destination':None },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':      200.,            'destination_section':None, 'destination':None },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -   8000.,            'destination_section':None, 'destination':None },
                                ], # actual_use_1, actual_use_2 => actual_use_2 modified

                 ],
       'solver_1': [ 
                              [ # immobilisation start
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    11000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':  -  1000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  2000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     2000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   2000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     2000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   2000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     2000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   2000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     2000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   2000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     2000.,            'destination_section':None, 'destination':None, },
                              ],
                        ],
       'solver_2': [ 
                              [ # immobilisation start
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  50000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    55000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':  -  5000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                              ],
                        ],
       'solver_3': [ 
                              [ # immobilisation start
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    33000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':  -  3000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                              ], # Duration 60
                              [ # immobilisation start
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    33000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':  -  3000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -  10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -      0.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':        0.,            'destination_section':None, 'destination':None, },
                              ], # Duration 36
                              [ # immobilisation start
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    33000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':  -  3000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_2',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_2',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_2',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_2',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_2',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                              ], # Depreciation account changed
                              [ # immobilisation start
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    33000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':  -  3000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_2',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_2',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_2',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_2',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_2',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                              ], # Depreciation account changed, date changed
                              [ # immobilisation start
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    33000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':  -  3000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                              ], # Original conditions
                              [ # immobilisation start
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    33000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':  -  3000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None,},
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,},
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,
                                  'profit_quantity': -6000. },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                              ], # After profit_and_loss (quantity modified)
                              [ # immobilisation start
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    33000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':  -  3000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None,},
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,},
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,
                                  'profit_quantity': -6000. },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,
                                  'profit_quantity': 6000. },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                              ], # After profit_and_loss (source modified)
                              [ # immobilisation start
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    33000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':  -  3000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None,},
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,},
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,
                                  'profit_quantity': -6000. },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,
                                  'profit_quantity': 6000. },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,
                                  'profit_quantity': 6000. },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                              ], # After profit_and_loss (a transaction set to 0)
                              [ # immobilisation start
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    33000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':  -  3000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None,},
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,},
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,
                                  'profit_quantity': -6000. },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,
                                  'profit_quantity': 6000. },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,
                                  'profit_quantity': 2000. },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None, },
                              ], # After profit_and_loss (the previous transaction reset to 8000)
                              [ # immobilisation start
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    33000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':  -  3000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None,},
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,},
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,
                                  'profit_quantity': -6000. },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,
                                  'profit_quantity': 6000. },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,
                                  'profit_quantity': 2000. },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,
                                  'profit_quantity': 6000. },
                              ], # After profit_and_loss (another transaction set to 0)
                              [ # immobilisation start
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  30000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':    33000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':  -  3000.,            'destination_section':None, 'destination':None, },
                                # annuities
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None,},
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,},
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,
                                  'profit_quantity': -6000. },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,
                                  'profit_quantity': 6000. },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,
                                  'profit_quantity': 2000. },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   6000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     6000.,            'destination_section':None, 'destination':None,
                                  'profit_quantity': 6000. },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     0.,            'destination_section':None, 'destination':None, }
                              ], # After profit_and_loss (artificial simulation movement set to 0)
                        ]                        
       }


  aggregated = [ [ { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1', 'value': - 200000.,   'destination':None, },
                                                  { 'source':'in_out_1',         'value':   220000.,   'destination':None, },
                                                  { 'source':'vat_1',            'value': -  20000.,   'destination':None, } ] },
                   { 'date':DateTime('2001/06/12'), 'source_section':'nexedi', 'destination_section':None, 
                                        'data': [ { 'source':'immobilisation_1', 'value': - 300000.,   'destination':None, },
                                                  { 'source':'in_out_1',         'value':   330000.,   'destination':None, },
                                                  { 'source':'vat_1',            'value': -  30000.,   'destination':None, } ] },
                   { 'date':DateTime('2001/12/15'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1', 'value':   300000.,   'destination':None, },
                                                  { 'source':'amortisation_1',   'value': -  15287.67, 'destination':None, },
                                                  { 'source':'in_out_2',         'value': - 313183.56, 'destination':None, },
                                                  { 'source':'vat_1',            'value':    28471.23, 'destination':None, } ] },
                   { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',   'value':  - 35287.67, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':    35287.67, 'destination':None, } ] },
                   { 'date':DateTime('2002/02/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1', 'value': - 600000.,   'destination':None, },
                                                  { 'source':'in_out_1',         'value':   660000.,   'destination':None, },
                                                  { 'source':'vat_1',            'value': -  60000.,   'destination':None, } ] },
                   { 'date':DateTime('2002/06/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1', 'value': - 284712.33, 'destination':None, },
                                                  { 'source':'in_out_1',         'value':   313183.56, 'destination':None, },
                                                  { 'source':'vat_1',            'value': -  28471.23, 'destination':None, } ] },
                   { 'date':DateTime('2002/07/06'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1', 'value': -  20000.,   'destination':None, },
                                                  { 'source':'in_out_1',         'value':    22000.,   'destination':None, },
                                                  { 'source':'vat_1',            'value': -   2000.,   'destination':None, } ] },
                   { 'date':DateTime('2002/12/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1', 'value':   200000.,   'destination':None, },
                                                  { 'source':'amortisation_1',   'value': -  38301.37, 'destination':None, },
                                                  { 'source':'in_out_2',         'value': - 177868.49, 'destination':None, },
                                                  { 'source':'vat_1',            'value':    16169.86, 'destination':None, } ] },
                   { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',   'value': - 201031.08, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':   201031.08, 'destination':None, },] },
                   { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1', 'value': - 100000.,   'destination':None, },
                                                  { 'source':'in_out_1',         'value':   110000.,   'destination':None, },
                                                  { 'source':'vat_1',            'value': -  10000.,   'destination':None, },
                                                  { 'source':'immobilisation_2', 'value': - 200000.,   'destination':None, },
                                                  { 'source':'in_out_3',         'value':   215000.,   'destination':None, },
                                                  { 'source':'vat_2',            'value': -  15000.,   'destination':None, } ] },
                   { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1', 'value':   284712.33, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value': -  23315.54, 'destination':None, },
                                                  { 'source':'in_out_2',         'value': - 287536.46, 'destination':None, },
                                                  { 'source':'vat_1',            'value':    26139.68,'destination':None, } ] },
                   { 'date':DateTime('2003/03/15'), 'source_section':'coramy', 'destination_section':'nexedi',
                                        'data': [ { 'source':'immobilisation_1', 'value': -  20000.,   'destination':'immobilisation_1'},
                                                  { 'source':'in_out_2',         'value':    14405.48, 'destination':'in_out_2', },
                                                  { 'source':'vat_1',            'value': -   1309.59, 'destination':'vat_1', },
                                                  { 'source':'amortisation_1',   'value':     6904.11, 'destination':'amortisation_1'}]},
                   { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_2',   'value':  -  4166.67, 'destination':None, },
                                                  { 'source':'amortisation_2',   'value':     4166.67, 'destination':None, },
                                                  { 'source':'depreciation_1',   'value':  -  1553.04, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':     1553.04, 'destination':None, } ] },
                   { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_2', 'value':   200000.,   'destination':None, },
                                                  { 'source':'amortisation_2',   'value': -  40885.42, 'destination':None, },
                                                  { 'source':'in_out_4',         'value': - 171048.18, 'destination':None, },
                                                  { 'source':'vat_2',            'value':    11933.59, 'destination':None, } ] },
                   { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',   'value': - 165559.29, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':   165559.29, 'destination':None, } ] },
                   { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'destination_section':'nexedi',
                                        'data': [ { 'source':'in_out_1',         'value':   186806.64, 'destination':'in_out_2', },
                                                  { 'source':'immobilisation_1', 'value': - 300000.,   'destination':'immobilisation_1'},
                                                  { 'source':'vat_1',            'value': -  16982.42, 'destination':'vat_1' },
                                                  { 'source':'amortisation_1',   'value':   130175.78, 'destination':'amortisation_1'}]},
                   { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1', 'value':   200000.,   'destination':None, },
                                                  { 'source':'amortisation_1',   'value': - 199976.79, 'destination':None, },
                                                  { 'source':'in_out_2',         'value': - 110025.53, 'destination':None, },
                                                  { 'source':'in_out_1',         'value':   110000.,   'destination':None, },
                                                  { 'source':'vat_1',            'value':        2.32, 'destination':None, }]},
                   { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_2',   'value':  - 36718.75, 'destination':None, },
                                                  { 'source':'amortisation_2',   'value':    36718.75, 'destination':None, },
                                                  { 'source':'depreciation_1',   'value':  - 29815.20, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':    29815.20, 'destination':None, } ] },
                   { 'date':DateTime('2004/08/15'), 'source_section':'coramy', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1', 'value':   100000.,   'destination':None, },
                                                  { 'source':'amortisation_1',   'value': -  28547.95, 'destination':None, },
                                                  { 'source':'in_out_2',         'value': -  78597.26, 'destination':None, },
                                                  { 'source':'vat_1',            'value':     7145.21, 'destination':None, } ] },
                   { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1', 'value':    79824.22, 'destination':None, },
                                                  { 'source':'in_out_1',         'value':   201000.,   'destination':None, },
                                                  { 'source':'vat_1',            'value':     1964.66, 'destination':None, },
                                                  { 'source':'depreciation_1',   'value': - 152260.84, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':    12083.23, 'destination':None, },
                                                  { 'source':'in_out_2',         'value': - 142611.26, 'destination':None, } ] },
                   { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',   'value':  - 10275.60, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':    10275.60, 'destination':None, } ] },
                   { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',   'value': - 121250.,   'destination':None, },
                                                  { 'source':'amortisation_1',   'value':   121250.,   'destination':None, } ] },
                   { 'date':DateTime('2006/06/24'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_3', 'value': - 150000.,   'destination':None, },
                                                  { 'source':'in_out_5',         'value':   165000.,   'destination':None, },
                                                  { 'source':'vat_3',            'value': -  15000.,   'destination':None, } ] },
                   { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_3',   'value':  - 62691.47, 'destination':None, },
                                                  { 'source':'amortisation_3',   'value':    62691.47, 'destination':None, },
                                                  { 'source':'depreciation_1',   'value': -  21484.38, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':    21484.38, 'destination':None, } ] },
                   { 'date':DateTime('2007/02/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_3', 'value':   150000.,   'destination':None, },
                                                  { 'source':'in_out_6',         'value': -  84846.83, 'destination':None, },
                                                  { 'source':'vat_3',            'value':     7713.35, 'destination':None, },
                                                  { 'source':'amortisation_3',   'value': -  72866.52, 'destination':None, } ] },
                   { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_3',   'value':  - 10175.05, 'destination':None, },
                                                  { 'source':'amortisation_3',   'value':    10175.05, 'destination':None, },
                                                  { 'source':'depreciation_1',   'value': -  14770.51, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':    14770.51, 'destination':None, } ] },
                   { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',   'value': -  10154.72, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':    10154.72, 'destination':None, } ] },
                   { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',   'value': -   6981.37, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':     6981.37, 'destination':None, } ] },
                   { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',   'value': -   5119.67, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':     5119.67, 'destination':None, } ] },
                   { 'date':DateTime('2012/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',   'value': -   5119.67, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':     5119.67, 'destination':None, } ] },
                   { 'date':DateTime('2013/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',   'value': -   5119.67, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':     5119.67, 'destination':None, } ] },      
                  ],
                  
                  # Solvers test
                  [
                   { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1',   'value': -    10000., 'destination':None, },
                                                  { 'source':'in_out_1',           'value':      11000., 'destination':None, },
                                                  { 'source':'vat_1',              'value': -     1000., 'destination':None, } ] },
                   { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1',   'value': -    50000., 'destination':None, },
                                                  { 'source':'in_out_1',           'value':      55000., 'destination':None, },
                                                  { 'source':'vat_1',              'value': -     5000., 'destination':None, },
                                                  { 'source':'depreciation_1',     'value': -     2000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':       2000., 'destination':None, } ] },
                   { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1',   'value': -    30000., 'destination':None, },
                                                  { 'source':'in_out_1',           'value':      33000., 'destination':None, },
                                                  { 'source':'vat_1',              'value': -     3000., 'destination':None, },
                                                  { 'source':'depreciation_1',     'value': -    12000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      12000., 'destination':None, } ] },
                   { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -    18000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      18000., 'destination':None, } ] },
                   { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -    18000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      18000., 'destination':None, } ] },
                   { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -    18000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      18000., 'destination':None, } ] },
                   { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -    16000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      16000., 'destination':None, } ] },
                   { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -     6000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':       6000., 'destination':None, } ] },
                                                                                
                  ],
                  
                  # Solvers test, duration 36
                  [
                   { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1',   'value': -    10000., 'destination':None, },
                                                  { 'source':'in_out_1',           'value':      11000., 'destination':None, },
                                                  { 'source':'vat_1',              'value': -     1000., 'destination':None, } ] },
                   { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1',   'value': -    50000., 'destination':None, },
                                                  { 'source':'in_out_1',           'value':      55000., 'destination':None, },
                                                  { 'source':'vat_1',              'value': -     5000., 'destination':None, },
                                                  { 'source':'depreciation_1',     'value': -     2000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':       2000., 'destination':None, } ] },
                   { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1',   'value': -    30000., 'destination':None, },
                                                  { 'source':'in_out_1',           'value':      33000., 'destination':None, },
                                                  { 'source':'vat_1',              'value': -     3000., 'destination':None, },
                                                  { 'source':'depreciation_1',     'value': -    12000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      12000., 'destination':None, } ] },
                   { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -    22000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      22000., 'destination':None, } ] },
                   { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -    22000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      22000., 'destination':None, } ] },
                   { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -    22000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      22000., 'destination':None, } ] },
                   { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -    10000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      10000., 'destination':None, } ] },
                   { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -        0., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':          0., 'destination':None, } ] },
                                                                                
                  ],
                  
                  # Solvers test, depreciation account changed
                  [
                   { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1',   'value': -    10000., 'destination':None, },
                                                  { 'source':'in_out_1',           'value':      11000., 'destination':None, },
                                                  { 'source':'vat_1',              'value': -     1000., 'destination':None, } ] },
                   { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1',   'value': -    50000., 'destination':None, },
                                                  { 'source':'in_out_1',           'value':      55000., 'destination':None, },
                                                  { 'source':'vat_1',              'value': -     5000., 'destination':None, },
                                                  { 'source':'depreciation_1',     'value': -     2000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':       2000., 'destination':None, } ] },
                   { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1',   'value': -    30000., 'destination':None, },
                                                  { 'source':'in_out_1',           'value':      33000., 'destination':None, },
                                                  { 'source':'vat_1',              'value': -     3000., 'destination':None, },
                                                  { 'source':'depreciation_1',     'value': -    12000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      12000., 'destination':None, } ] },
                   { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -    12000., 'destination':None, },
                                                  { 'source':'depreciation_2',     'value': -     6000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      18000., 'destination':None, } ] },
                   { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -    12000., 'destination':None, },
                                                  { 'source':'depreciation_2',     'value': -     6000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      18000., 'destination':None, } ] },
                   { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -    12000., 'destination':None, },
                                                  { 'source':'depreciation_2',     'value': -     6000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      18000., 'destination':None, } ] },
                   { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -    10000., 'destination':None, },
                                                  { 'source':'depreciation_2',     'value': -     6000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      16000., 'destination':None, } ] },
                   { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -        0., 'destination':None, },
                                                  { 'source':'depreciation_2',     'value': -     6000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':       6000., 'destination':None, } ] },
                                                                                
                  ],
                  
                  # Solvers test, depreciation account changed, solver_3 date changed
                  [
                   { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1',   'value': -    10000., 'destination':None, },
                                                  { 'source':'in_out_1',           'value':      11000., 'destination':None, },
                                                  { 'source':'vat_1',              'value': -     1000., 'destination':None, } ] },
                   { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1',   'value': -    50000., 'destination':None, },
                                                  { 'source':'in_out_1',           'value':      55000., 'destination':None, },
                                                  { 'source':'vat_1',              'value': -     5000., 'destination':None, },
                                                  { 'source':'depreciation_1',     'value': -     2000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':       2000., 'destination':None, } ] },
                   { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1',   'value': -        0., 'destination':None, },
                                                  { 'source':'in_out_1',           'value':          0., 'destination':None, },
                                                  { 'source':'vat_1',              'value': -        0., 'destination':None, },
                                                  { 'source':'depreciation_1',     'value': -    12000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      12000., 'destination':None, } ] },
                   { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1',   'value': -    30000., 'destination':None, },
                                                  { 'source':'in_out_1',           'value':      33000., 'destination':None, },
                                                  { 'source':'vat_1',              'value': -     3000., 'destination':None, },
                                                  { 'source':'depreciation_1',     'value': -    12000., 'destination':None, },
                                                  { 'source':'depreciation_2',     'value': -        0., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      12000., 'destination':None, } ] },
                   { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -    12000., 'destination':None, },
                                                  { 'source':'depreciation_2',     'value': -     6000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      18000., 'destination':None, } ] },
                   { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -    12000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      18000., 'destination':None, },
                                                  { 'source':'depreciation_2',     'value': -     6000., 'destination':None, } ] },  
                   { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -    10000., 'destination':None, },
                                                  { 'source':'depreciation_2',     'value': -     6000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      16000., 'destination':None, } ] },
                   { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -        0., 'destination':None, },
                                                  { 'source':'depreciation_2',     'value': -     6000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':       6000., 'destination':None, } ] },
                   { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_2',     'value': -     6000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':       6000., 'destination':None, } ] },
                  ],
                  
                  # Solvers test, original values
                  [
                   { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1',   'value': -    10000., 'destination':None, },
                                                  { 'source':'in_out_1',           'value':      11000., 'destination':None, },
                                                  { 'source':'vat_1',              'value': -     1000., 'destination':None, } ] },
                   { 'date':DateTime('2002/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1',   'value': -    50000., 'destination':None, },
                                                  { 'source':'in_out_1',           'value':      55000., 'destination':None, },
                                                  { 'source':'vat_1',              'value': -     5000., 'destination':None, },
                                                  { 'source':'depreciation_1',     'value': -     2000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':       2000., 'destination':None, } ] },
                   { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1',   'value': -    30000., 'destination':None, },
                                                  { 'source':'in_out_1',           'value':      33000., 'destination':None, },
                                                  { 'source':'vat_1',              'value': -     3000., 'destination':None, },
                                                  { 'source':'depreciation_1',     'value': -    12000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      12000., 'destination':None, } ] },
                   { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -    18000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      18000., 'destination':None, } ] },
                   { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -    18000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      18000., 'destination':None, } ] },
                   { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -    18000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      18000., 'destination':None, } ] },
                   { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -    16000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':      16000., 'destination':None, } ] },
                   { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',     'value': -     6000., 'destination':None, },
                                                  { 'source':'amortisation_1',     'value':       6000., 'destination':None, } ] },
                                                                                
                  ],
                ]
             
        
  validation_list = [ [ { 'date':DateTime('2003/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2004/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2005/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2006/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2007/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2008/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2009/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2010/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2011/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2012/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2013/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2004/02/01'), 'source_section':'organisation/nexedi', 'destination_section':None}, ],
                      [ { 'date':DateTime('2003/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2004/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2005/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2006/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2007/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2008/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2009/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2010/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2011/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2012/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2013/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                        { 'date':DateTime('2004/02/01'), 'source_section':'organisation/nexedi', 'destination_section':None}, ],
                      ]
  validation_step = 0
  
  solve_list = [ [ { 'date':DateTime('2001/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2002/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2003/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2004/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2005/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2006/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2007/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2008/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None}, ],
                 [ { 'date':DateTime('2001/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2002/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2003/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2004/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2005/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2006/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2007/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2008/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None}, ],
                 [ { 'date':DateTime('2001/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2002/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2003/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2004/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2005/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2006/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2007/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None},
                   { 'date':DateTime('2008/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None}, ],
                 # Profit and loss
                 [ { 'date':DateTime('2005/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None} ],
                 [ { 'date':DateTime('2006/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None} ],
                 [ { 'date':DateTime('2007/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None} ],
                 [ { 'date':DateTime('2007/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None} ],
                 [ { 'date':DateTime('2008/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None} ],
                 [ { 'date':DateTime('2008/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None} ] ]
                   
  
  solver_dict = { 'solver_3' : ['update_from_simulation_amortisation', 'update_from_simulation_amortisation',
                                'update_from_simulation_amortisation', 'profit_loss_amortisation',
                                'profit_loss_amortisation', 'profit_loss_amortisation', 'profit_loss_amortisation',
                                'profit_loss_amortisation', 'profit_loss_amortisation', 'profit_loss_amortisation' ] }
                                
  transaction_change_list = [ 
      { 'transaction': { 'date':DateTime('2005/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None,
                         'source':'account/amortisation_1', 'destination':None},
        'changes': { 'Quantity':36000. } },
      { 'transaction': { 'date':DateTime('2006/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None,
                         'source':'account/amortisation_1', 'destination':None},
        'changes': { 'Source':'account/amortisation_2' } },
      { 'transaction': { 'date':DateTime('2007/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None,
                         'source':'account/amortisation_1', 'destination':None},
        'changes': { 'Quantity':0. } },
      { 'transaction': { 'date':DateTime('2007/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None,
                         'source':'account/amortisation_1', 'destination':None},
        'changes': { 'Quantity':8000. } },
      { 'transaction': { 'date':DateTime('2008/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None,
                         'source':'account/amortisation_1', 'destination':None},
        'changes': { 'Quantity':0. } },
                            ]
                            
  zero_simulation_movement_list = [
      { 'transaction' : { 'date':DateTime('2008/01/01'), 'source_section':'organisation/nexedi', 'destination_section':None,
                         'source':'account/amortisation_1', 'destination':None},
      'item': 'vpn_11' }
                                  ]
      
  
                       
  def assertDifference(self, a, b, diff=0.02):
   """
   Raise an error if the difference between a and b is
   greater than diff
   """
   self.failUnless( self.areNear(a,b,diff) )
   
  
  def roundedEquals(self, a, b, precision=2):
    LOG("roundedEquals", 0, "compares %s and %s, precision = %s ; rounded values = %s and %s" % (repr(a), repr(b), repr(precision), repr(round(a,precision)), repr(round(b,precision))))
    return round(a,precision) == round(b,precision)
  
  def areNear(self, a, b, diff=0.02):
    """
    Return true if the difference between a and b 
    is lower than diff
    """
    difference = a - b
    return abs(a-b) <= diff
  
  
  def getBusinessTemplateList(self):
    """
      Return the list of business templates.
    """
    return ('erp5_trade', 'erp5_accounting', 
            'nexedi_vpn', 'erp5_immobilisation')

  def convertToLowerCase(self, key):
    """
      This function returns an attribute name 
      thanks to the name of a class
      for example convert 'Purchase Order' to 'purchase_order' 
    """
    result = key.lower()
    result = result.replace(' ','_')
    return result


  def getSqlConnection(self):
    return getattr(self.getPortal(), 'erp5_sql_connection', None)
  
  def getItemModule(self):
    return getattr(self.getPortal(), self.item_module_name, None)
  
  def getCurrencyModule(self):
    return getattr(self.getPortal(), 'currency', None)
  
  def getOrganisationModule(self):
    return getattr(self.getPortal(), 'organisation', None)
  
  def getAccountingModule(self):
    return getattr(self.getPortal(), 'accounting', None)
  
  def getAccountModule(self):
    return getattr(self.getPortal(), 'account', None)
  
  def getDeliveryModule(self):
    return getattr(self.getPortal(), 'purchase_packing_list', None)
  
  def getPortalId(self):
    return self.getPortal().getId()
 
  def sqlQuery(self, sql):
    sql_connection = self.getSqlConnection()
    return sql_connection.manage_test(sql)
    
  
  def failIfDifferentSet(self, a,b):
    for i in a:
      self.failUnless(i in b)
    for i in b:
      self.failUnless(i in a)
    self.assertEquals(len(a),len(b))

  def afterSetUp(self, quiet=1, run=1):
    self.login()
    portal = self.getPortal()
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_catalogClear()
#     # First set Acquisition
#     portal.ERP5_setAcquisition()
#     # Then reindex
    LOG('before reindex', 0, "")
    portal.ERP5Site_reindexAll()
    self.stepTic()
    LOG('afterSetup',0,'portal.portal_categories.immediateReindexObject')
    self.getAccountingModule().manage_addLocalRoles('guillaume', ('Assignor',))
    portal.portal_categories.immediateReindexObject()
    for o in portal.portal_categories.objectValues():
      o.recursiveImmediateReindexObject()
    self.stepTic()
    LOG('afterSetup',0,'portal.portal_simulation.immediateReindexObject')
    portal.portal_simulation.immediateReindexObject()
    for o in portal.portal_simulation.objectValues():
      o.recursiveImmediateReindexObject()
    self.stepTic()
    LOG('afterSetup',0,'portal.portal_rules.immediateReindexObject')
    portal.portal_rules.immediateReindexObject()
    self.stepTic()
    
    # Then add new components
    # Currencies
    currency_module = self.getCurrencyModule()
    for currency_id in self.currency_list:
      currency_module.newContent(id=currency_id, portal_type="Currency")
    self.stepTic()

    # Construct item module
    #portal.newContent(portal_type='Nexedi VPN Module',id='vpn',title='VPN List')
    
    # Items
    item_module = self.getItemModule()
    for item_id in self.item_id_list:
      item_module.newContent(id=item_id, portal_type=self.item_portal_type)
    self.stepTic()
    
    # Build all movement groups
    #self.getPortal().SimulationTool_constructMovementGroupList()

    # Organisations
    organisation_module = self.getOrganisationModule()
    for organisation_data in self.organisation_data_list:
      organisation = organisation_module.newContent(id=organisation_data['id'], immediate_reindex=1)
      end_date = organisation_data.get('end_date')
      currency_id = organisation_data.get('currency')
      if currency_id is not None:
        currency_id = 'currency/%s' % currency_id
        organisation.setSocialCapitalCurrencyId(currency_id)
      if end_date is not None:
        organisation.setFinancialYearStopDate(end_date)
    self.stepTic()
        
    # Accounts
    account_module = self.getAccountModule()
    for account_data in self.account_data_list:
      account = account_module.newContent(id = account_data['id'])
      account.setPcg(account_data['pcg_id'])
    self.stepTic()
   
    # Deliveries
    delivery_module = self.getDeliveryModule()
    del_type = self.delivery_type
    del_line_type = del_type + " Line"
    
    for delivery_line_data in self.delivery_line_data_list:
      parent_id = delivery_line_data['parent_id']
      del_line_id = delivery_line_data['id']
      date = DateTime(delivery_line_data['date'])
      source_section = delivery_line_data['source_section']
      destination_section = delivery_line_data['destination_section']
      if source_section is not None: source_section = organisation_module[source_section]
      if destination_section is not None: destination_section = organisation_module[destination_section]
      item_id_list = delivery_line_data['items']
      
      delivery = getattr(delivery_module, parent_id, None)
      if delivery is None:
        # Create the parent of current delivery line
        delivery = delivery_module.newContent(id = parent_id, portal_type = del_type)
      delivery_line = delivery.newContent(id = del_line_id, portal_type = del_line_type)
      delivery_line.setStopDate(date)
      if source_section is not None: delivery_line.setSourceSectionValue(source_section)
      if destination_section is not None: delivery_line.setDestinationSectionValue(destination_section)
      item_list = []
      for item_id in item_id_list:
        item_list.append(item_module[item_id])
      self.tic()
      delivery_line.immediateReindexObject()
      delivery_line.setAggregateValueList(item_list)
      delivery_line.immediateReindexObject()
      
      get_transaction().commit()
      self.stepTic()
      LOG('test :', 0, 'delivery line %s ; aggregate value list = %s' % (repr(delivery_line), repr(delivery_line.getAggregateValueList())))
      my_item = item_list[0]
    self.stepTic()
      
    # Build the default rule
    #self.getPortal().portal_types.constructContent(type_name='Amortisation Rule',
    #                    container=self.getPortal().portal_rules,
    #                    id='default_amortisation_rule')

                        
                        
  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('guillaume', '', ['Manager'], [])
    user = uf.getUserById('guillaume').__of__(uf)
    newSecurityManager(None, user)

  def stepAddZeroSimulationMovement(self, sequence=None, **kw):
    """
    Add a zero simulation movement to a specific delivery
    """
    zero_step = getattr(self, 'zero_step', -1)
    zero_step += 1
    to_change = self.zero_simulation_movement_list[zero_step]['transaction']
    item_id = self.zero_simulation_movement_list[zero_step]['item']
    item = getattr(self.getItemModule(), item_id)
    applied_rule = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    applied_rule = applied_rule[0]
    LOG('applied rule', 0, applied_rule)
    found = 0
    for transaction in self.getAccountingModule().objectValues():
      if not found:
        if transaction.getDestinationSection() == to_change['destination_section'] and \
        transaction.getSourceSection() == to_change['source_section'] and \
        transaction.getStopDate() == to_change['date']:
          for line in transaction.contentValues():
            if line.getSource() == to_change['source'] and line.getDestination() == to_change['destination']:
              mov = applied_rule.newContent(portal_type = "Simulation Movement",
                                            source = to_change['source'],
                                            destination = to_change['destination'],
                                            source_section = to_change['source_section'],
                                            destination_section = to_change['destination_section'],
                                            resource = 'currency/EUR',
                                            start_date = to_change['date'],
                                            stop_date = to_change['date'],
                                            quantity = 0.)
              mov.immediateReindexObject()
              found = 1
              break
    if not found:
      LOG('TEST WARNING :', 0, 'transaction %s not found to change transaction properties' % (repr(to_change)))
      
    self.zero_step = zero_step
      
    
  def constructImmobilisationMovement(self, immobilisation_id=None, sequence=None, **kw):
    """
    Create an immobilisation movement
    """
    if (sequence is None) or (immobilisation_id is None):
      return
    
    immobilisation_data = self.immobilisation_movement_data_list[immobilisation_id]
    item = self.getItemModule()._getOb(immobilisation_data['item'])
    LOG('test :', 0, 'for immobilisation %s, item = %s' % (repr(immobilisation_id),repr(item)))
    
    immo = item.newContent(id=immobilisation_id, portal_type = 'Immobilisation')
    LOG('test :', 0, 'content of item %s : %s' % (repr(item), repr(map(lambda o:repr(o), item.objectValues()))))
    for property, property_sheet_name in self.property_list:
      property_value = immobilisation_data.get(property)
      if property_value is not None:
        if property[-3:] == 'acc': property_value = 'account/%s' % property_value
        setter = getattr(immo, 'set' + property_sheet_name)
        setter(property_value)
        
    item.recursiveImmediateReindexObject()
    item.immediateExpandAmortisation()
    return immo
  
      
  def stepCreateImmobilisations(self, sequence=None, sequence_list=None, **kw):
    """
    Construct all of the immobilisations needed for the current test
    """
    immobilisation_list_name = sequence.get('immobilisation_list_name')
    immobilisation_list = sequence.get('immobilisation_list') or []
    for i in range(len(self.immobilisation_movement_list[immobilisation_list_name])):
      immobilisation_name = self.immobilisation_movement_list[immobilisation_list_name][i]
      immo = self.constructImmobilisationMovement(immobilisation_name, sequence=sequence)
      immobilisation_list.append(immo)
      
    sequence.set('immobilisation_list', immobilisation_list)
    
   
  def stepArtificialExpand(self, sequence=None, **kw):
    """
    Reexpand the simulation and set the needed properties in sequence
    """
    immobilisation_list = sequence.get('immobilisation_list')
    immobilisation_list_name = sequence.get('immobilisation_list_name')
    step = self.current_step.get(immobilisation_list_name, -1)
    step += 1
    self.current_step[immobilisation_list_name] = step
    item = immobilisation_list[0].getParent()
    item.immediateExpandAmortisation()
    
  def stepVerifyConvergence(self, sequence=None, **kw):
    """
    Fails if any transaction is divergent
    """
    accounting = self.getAccountingModule()
    for transaction in accounting.contentValues():
      if transaction.isDivergent() or self.getWorkflowTool().getStatusOf('amortisation_transaction_divergence_workflow', transaction)['amortisation_causality_state'] == 'diverged':
        LOG('transaction %s is divergent !... data follows' % repr(transaction), 0, '')
        LOG('workflow status', 0, self.getWorkflowTool().getStatusOf('amortisation_transaction_divergence_workflow', transaction)['amortisation_causality_state'])
        LOG('source_section : %s,' % repr(transaction.getSourceSection()), 0, 'destination_section = %s, start_date = %s, stop_date = %s' % (repr(transaction.getDestinationSection()), repr(transaction.getStartDate()), repr(transaction.getStopDate())))
        LOG('lines :', 0, '')
        for line in transaction.contentValues():
          LOG('line %s... source =' % repr(line), 0, '%s, destination = %s, resource = %s, quantity = %s' % (repr(line.getSource()), repr(line.getDestination()), repr(line.getResource()), repr(line.getQuantity())))
          for mov in line.getDeliveryRelatedValueList():
            LOG('in line %s...' % repr(line), 0, 'simulation movement %s : source = %s, destination = %s, source_section = %s, destination_section = %s, resource = %s, start_date = %s, stop_date = %s, quantity = %s, profit_quantity = %s, corrected_quantity = %s' % (repr(mov), repr(mov.getSource()), repr(mov.getDestination()), repr(mov.getSourceSection()), repr(mov.getDestinationSection()), repr(mov.getResource()), repr(mov.getStartDate()), repr(mov.getStopDate()), repr(mov.getQuantity()), repr(mov.getProfitQuantity()), repr(mov.getCorrectedQuantity())))  
        self.failUnless(0)
      else:
        for l in transaction.getMovementList():
          for m in l.getDeliveryRelatedValueList():
            if m.isDivergent():
              LOG('movement %s is divergent' % repr(m), 0, '')
              self.failUnless(0)


  def stepRetrieveData(self, sequence=None, **kw):
    """
    Set the needed properties in sequence
    """
    immobilisation_list_name = sequence.get('immobilisation_list_name')
    immobilisation_id = self.immobilisation_movement_list[immobilisation_list_name][0]
    immobilisation_data = self.immobilisation_movement_data_list[immobilisation_id]
    item = self.getItemModule()._getOb(immobilisation_data['item'])
    
    immobilisation_list = list(item.objectValues())
    sequence.edit(immobilisation_list = immobilisation_list)
  
      
  def stepApplySolver(self, sequence=None, **kw):
    """
    Apply the solvers on the amortisation transactions
    """
    # First search the deliver
    immobilisation_list_name = sequence.get('immobilisation_list_name')
    solver_step_dict = getattr(self, "solver_step", {})
    if solver_step_dict == {}:
      self.solver_step = {}
    solver_step = solver_step_dict.get(immobilisation_list_name, 0)
    to_solve_list = self.solve_list[solver_step]
    solver_type = self.solver_dict[immobilisation_list_name][solver_step]
    LOG('solver_step =',0, solver_step)
    LOG('solver_type =',0, solver_type)

    accounting = self.getAccountingModule()
    for to_solve in to_solve_list:
      LOG('looking for transaction', 0, repr(to_solve))
      found = 0
      for transaction in accounting.objectValues():
        LOG('testing transaction', 0, '%s (dest_sect = %s, source_sect = %s, date = %s, state=%s)' % (repr(transaction), repr(transaction.getDestinationSection()), repr(transaction.getSourceSection()), repr(transaction.getStopDate()), repr(self.getWorkflowTool().getStatusOf('amortisation_transaction_divergence_workflow', transaction)['amortisation_causality_state'])))
        if transaction.getDestinationSection() == to_solve['destination_section'] and \
          transaction.getSourceSection() == to_solve['source_section'] and \
          transaction.getStopDate() == to_solve['date'] and \
          self.getWorkflowTool().getStatusOf('amortisation_transaction_divergence_workflow',transaction)\
          ['amortisation_causality_state'] == 'diverged':
          LOG('applying solver %s on transaction %s :' % (solver_type, repr(transaction)), 0, '')
          for sub in transaction.contentValues():
            LOG('transaction contains %s' % repr(sub), 0, 'source %s, dest %s, qty %s' % (repr(sub.getSource()), repr(sub.getDestination()), repr(sub.getQuantity())))
          self.getWorkflowTool().doActionFor(transaction, solver_type, 'amortisation_transaction_divergence_workflow')
          transaction.updateFromSimulation()
          LOG('new state :', 0, self.getWorkflowTool().getStatusOf('amortisation_transaction_divergence_workflow',transaction)['amortisation_causality_state'])
          found = 1
          break
      if not found:
        LOG('TEST WARNING :', 0, 'transaction %s not found' % repr(to_solve))
      
    self.solver_step[immobilisation_list_name] = solver_step + 1
    
  def stepChangeTransactionProperties(self, sequence=None, **kw):
    """
    Modify some attributes belonging to a transaction
    """
    immobilisation_list_name = sequence.get('immobilisation_list_name')
    transaction_change_dict = getattr(self, "transaction_change_step", {})
    if transaction_change_dict == {}:
      self.transaction_change_step = {}
    step = transaction_change_dict.get(immobilisation_list_name, 0)
    transaction_change = self.transaction_change_list[step]
    to_change = transaction_change['transaction']
    
    accounting = self.getAccountingModule()
    found = 0
    for transaction in accounting.objectValues():
      if not found:
        if transaction.getDestinationSection() == to_change['destination_section'] and \
        transaction.getSourceSection() == to_change['source_section'] and \
        transaction.getStopDate() == to_change['date']:
          for line in transaction.contentValues():
            LOG('for changing properties, testing line %s' % repr(line), 0, 'source = %s, destination = %s' % (repr(line.getSource()), repr(line.getDestination())))
            if line.getSource() == to_change['source'] and line.getDestination() == to_change['destination']:
              for (key, value) in transaction_change['changes'].items():
                setter = getattr(line, 'set' + key)
                LOG('setting value %s for' % repr(value), 0, key)
                setter(value)
                LOG('getQuantity :', 0, line.getQuantity())
              for m in line.getDeliveryRelatedValueList():
                m.immediateReindexObject()
              transaction.notifySimulationChange()
              LOG('line modified... getSource :', 0, line.getSource())
              found = 1
              break
    if not found:
      LOG('TEST WARNING :', 0, 'transaction %s not found to change transaction properties' % (repr(to_change)))
    
    self.transaction_change_step[immobilisation_list_name] = step + 1
    
    
  def stepIncrementStep(self, sequence=None, **kw):
    immobilisation_list_name = sequence.get('immobilisation_list_name')
    self.current_step[immobilisation_list_name] = self.current_step[immobilisation_list_name] + 1  
  
   
  def stepNextTestStep(self, sequence=None, **kw):
    """
    Construct the next immobilisation needed for the current test
    If all of the immobilisations are already constructed, unvalidate or validate the
    next immobilisation to be validated or unvalidated
    """
    immobilisation_list_name = sequence.get('immobilisation_list_name')
    immobilisation_list = sequence.get('immobilisation_list') or []
    step = self.current_step.get(immobilisation_list_name, -1)
    step += 1
    
    LOG('testImmobilisation :', 0, 'step = %s, immobilisation_list = %s' % (repr(step), repr(immobilisation_list)))
    immobilisation_movement_list = self.immobilisation_movement_list[immobilisation_list_name]
    if step < len(immobilisation_movement_list):
      LOG('NextTestStep', 0, 'create')
      immobilisation_name = immobilisation_movement_list[step]
      immobilisation = self.constructImmobilisationMovement(immobilisation_name, sequence=sequence)
      immobilisation_list.append(immobilisation)
      
    else:
      # Validate or unvalidate the next immobilisation to be validated or unvalidated
      switch_list = self.validation_switch_list.get(immobilisation_list_name, [])
      switch_number = step - len(immobilisation_movement_list)
      LOG('stepNextTestStep :', 0, 'immobilisation_list_name=%s, switch_list=%s, switch_number=%s, switch_list[switch_number]=%s' % (repr(immobilisation_list_name), repr(switch_list), repr(switch_number), repr(switch_number)))
      if switch_list is not None and switch_number < len(switch_list):
        LOG('NextTestStep', 0, 'switch')
        self.switchImmobilisationValidity( switch_list[switch_number], sequence=sequence )
      else:
        # Modify data on immobilisation movements
        LOG ('NextTestStep', 0, 'modify')
        change_number = switch_number - len(switch_list)
        LOG('change_number =', 0, '%i, len(immobilisation_movement_change_list) = %i' % (change_number, len(self.immobilisation_movement_change_list[immobilisation_list_name])))
        change_data = self.immobilisation_movement_change_list[immobilisation_list_name][change_number]
        self.changeMovementData(change_data, sequence=sequence)
        
    self.current_step[immobilisation_list_name] = step
    sequence.edit(immobilisation_list = immobilisation_list)
    
    
  def changeMovementData(self, change_data, sequence=None, **kw):
    """
    Modify data on the given immobilisation movement
    """
    movement_id = change_data['id']
    immobilisation_list = sequence.get('immobilisation_list')
    LOG('changeMovementData ; change_data =', 0, repr(change_data))
    for immo in immobilisation_list:
      if immo.getId() == movement_id:
        immobilisation = immo
    LOG('immobilisation = ', 0, repr(immobilisation))
    for (key, value) in change_data.items():
      if key != 'id':
        for (property_key, immobilisation_key) in self.property_list:
          if property_key == key:
            LOG('setting key', 0, repr(immobilisation_key))
            setter = getattr(immobilisation, 'set' + immobilisation_key, None)
            setter(value)
    LOG('blabla', 0, repr(immobilisation.getStopDate()))
    item = immobilisation.getParent()
    item.immediateExpandAmortisation()
    
    
  def stepDeleteAggregation(self, **kw):
    """
    Delete the aggregation
    """
    accounting_module = self.getAccountingModule()
    accounting_module.deleteContent(accounting_module.contentIds())
    LOG('accounting content', 0, accounting_module.contentIds())
    
  def stepCleanItemModule(self, **kw):
    """
    Delete the content of the item module
    """
    item_module = self.getItemModule()
    item_module.deleteContent(item_module.contentIds())
    
  def stepCleanSimulation(self, **kw):
    """
    Delete the simulation contents
    """
    simulation = self.getPortal().portal_simulation
    simulation.deleteContent(simulation.contentIds())
  
  def switchImmobilisationValidity(self, immobilisation_number, sequence=None, **kw):
    """
    Switch the validity state of given immobilisation
    """
    immobilisation_list = sequence.get('immobilisation_list')
    immobilisation = immobilisation_list[immobilisation_number]
    if immobilisation.checkImmobilisationConsistency():
      immobilisation_list_name = sequence.get('immobilisation_list_name')
      immobilisation_data = self.immobilisation_movement_data_list \
                                        [ self.immobilisation_movement_list[immobilisation_list_name][immobilisation_number] ]
      immobilisation.setStopDate(immobilisation_data['date'])
      LOG('switching %s to valid' % repr(immobilisation), 0, '')
    else:
      immobilisation.setStopDate(None)
      LOG('switching %s to unvalid' % repr(immobilisation), 0, '')
      
    item = immobilisation.getParent()
    item.immediateExpandAmortisation()
      
    
    
  def stepVerifySimulation(self, sequence=None, sequence_list=None, **kw):
    """
    Verify if the movements created in simulation correspond
    to the expected ones
    """    
    #for delivery in self.getDeliveryModule().objectValues():
    #  for delivery_line in delivery.objectValues():  
    #    sql = 'select cat2.id from catalog as cat1, catalog as cat2, category where category.uid = cat1.uid '
    #    sql += 'and cat1.id = %s and cat2.uid = category.category_uid' % repr(delivery_line.getId())
    #    LOG('test :', 0, 'sql method on delivery %s : %s' % (repr(delivery_line.getId()), repr(map(lambda x:x['id'],self.sqlQuery(sql)))))
    #    LOG('test :', 0, 'aggregate value list = %s' % repr(delivery_line.getAggregateValueList()))
    immobilisation_list_name = sequence.get('immobilisation_list_name')
    current_step = self.current_step.get(immobilisation_list_name, 0)
    immobilisation_list = sequence.get('immobilisation_list')
    if immobilisation_list is not None:
      item = immobilisation_list[0].getParent()
      LOG('verify simulation, item = ', 0, repr(item))
    else:
      immobilisation_id = self.immobilisation_movement_list[immobilisation_list_name][0]
      immobilisation_data = self.immobilisation_movement_data_list[immobilisation_id]
      item = self.getItemModule()._getOb(immobilisation_data['item'])
      LOG('verify simulation... item = ', 0, repr(item))
    test_name = sequence.get('immobilisation_list_name')
    
    expected = deepcopy(self.simulation_value_list[test_name][current_step])
    
    
    applied_rule_list = item.getCausalityRelatedValueList(portal_type = 'Applied Rule')
    applied_rule_list = [o for o in applied_rule_list if o.getSpecialiseValue().getPortalType() == 'Amortisation Rule']
    LOG('testImmobilisation :',0,'verifying number of applied rules on item %s : %i' % (repr(item.getId()), len(applied_rule_list)))
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    
    # Verify each written simulation movement
    LOG('testImmobilisation :', 0, 'applied rule... objectValues = %s, contentValues = %s' % (repr(applied_rule.objectValues()), repr(applied_rule.contentValues())))
    
    simulation_movement_list = list(applied_rule.objectValues())
    LOG('test :', 0, 'simulation_movement_list = %s' % repr(simulation_movement_list))
    simulation_movement_list.sort(lambda a,b: cmp(a.getStopDate(), b.getStopDate()))
    for simulation_movement in simulation_movement_list:
      source_section = simulation_movement.getSourceSectionId()
      destination_section = simulation_movement.getDestinationSectionId()
      destination = simulation_movement.getDestinationId()
      source = simulation_movement.getSourceId()
      value = simulation_movement.getQuantity()
      date = simulation_movement.getStopDate()
      
      LOG('testImmobilisation :',0,'verifying simulation movement %s : source=%s, destination=%s, source_section=%s, destination_section=%s, value=%s, date=%s' % (repr(simulation_movement.getId()), repr(source), repr(destination), repr(source_section), repr(destination_section), repr(value), repr(date)))
      LOG('testImmobilisation :',0, 'remaining expected movements : %s' % repr(expected))
      i = 0
      expected_movement = None
      while expected_movement is None and i<len(expected):
        current_movement = expected[i]
        if current_movement['date'] == date and current_movement['source'] == source \
                                            and current_movement['destination'] == destination \
                                            and current_movement['source_section'] == source_section \
                                            and current_movement['destination_section'] == destination_section \
                                            and self.roundedEquals(current_movement['value'], value):
          expected_profit_quantity = current_movement.get('profit_quantity', 0)
          profit_quantity = simulation_movement.getProfitQuantity()
          if profit_quantity is None:
            profit_quantity = 0
          if self.roundedEquals(profit_quantity,expected_profit_quantity):
            expected_movement = current_movement
          else:
            LOG('found a movement, but profit_quantity differs', 0, current_movement)
            LOG('profit quantity of transaction', 0, profit_quantity)
        i += 1
      
      self.failUnless(expected_movement is not None)
      
      if expected_movement is not None:
        del expected[i-1]
      
    # Then verify if there are expected simulation movements
    # which have not been matched
    LOG('testImmobilisation :',0,'verifying if expected values have all been matched... remaining = %s' % repr(expected))
    self.assertEquals(len(expected),0)
    
      
      
  def stepPrepareLinearTest(self, sequence=None, **kw):
    """
    Prepare data in sequence for the linear test
    """
    sequence.edit(immobilisation_list_name = 'linear')

    
  def stepPrepareDegressiveTest(self, sequence=None, **kw):
    """
    Prepare data in sequence for the degressive test
    """
    sequence.edit(immobilisation_list_name = 'degressive')
    
    
  def stepPrepareSameDayTest(self, sequence=None, **kw):
    """
    Prepare data in sequence for the test on same day
    """
    sequence.edit(immobilisation_list_name = 'same_day')
    
    
  def stepPrepareFirstOwnerChangeTest(self, sequence=None, **kw):
    """
    Prepare data in sequence for the first test on ownership changing
    """
    sequence.edit(immobilisation_list_name = 'owner_change_1')
    
    
  def stepPrepareSecondOwnerChangeTest(self, sequence=None, **kw):
    """
    Prepare data in sequence for the second test on ownership changing
    """
    sequence.edit(immobilisation_list_name = 'owner_change_2')
    
    
  def stepPrepareThirdOwnerChangeTest(self, sequence=None, **kw):
    """
    Prepare data in sequence for the third test on ownership changing
    """
    sequence.edit(immobilisation_list_name = 'owner_change_3')
      
  
  def stepPrepareComplexTest(self, sequence=None, **kw):
    """
    Prepare data in sequence for the complex test
    """
    sequence.edit(immobilisation_list_name = 'complex')


  def stepPrepareActualUseTest(self, sequence=None, **kw):
    """
    Prepare data in sequence for the actual use test
    """
    sequence.edit(immobilisation_list_name = 'actual_use')
    
  def stepPrepareFirstSolverTest(self, sequence=None, **kw):
    sequence.edit(immobilisation_list_name = 'solver_1')
    
  def stepPrepareSecondSolverTest(self, sequence=None, **kw):
    sequence.edit(immobilisation_list_name = 'solver_2')
    
  def stepPrepareThirdSolverTest(self, sequence=None, **kw):
    sequence.edit(immobilisation_list_name = 'solver_3')

  def stepValidateTransaction(self, sequence=None, **kw):
    """
    Validate some existing Amortisation Transaction
    according to the data structure of this test script
    """
    accounting = self.getAccountingModule()
    to_validate_list = self.validation_list[self.validation_step]
    self.validation_step += 1
    for to_validate in to_validate_list:
      LOG('looking for transaction', 0, repr(to_validate))
      for transaction in accounting.objectValues():
        LOG('transaction :', 0, 'destination_section=%s, source_section=%s, stop_date=%s' % (repr(transaction.getDestinationSection()), repr(transaction.getSourceSection()), repr(transaction.getStopDate())))
        if transaction.getDestinationSection() == to_validate['destination_section'] and \
          transaction.getSourceSection() == to_validate['source_section'] and \
          transaction.getStopDate() == to_validate['date'] and \
          self.getWorkflowTool().getStatusOf('amortisation_transaction_workflow',transaction)\
          ['amortisation_transaction_state'] != 'delivered':
          LOG('changing status', 0, "%s (%s to %s, date %s)" % (repr(transaction), repr(transaction.getSourceSection()), repr(transaction.getDestinationSection()), repr(transaction.getStopDate())))
          LOG('current status', 0, repr(self.getWorkflowTool().getStatusOf('amortisation_transaction_workflow', transaction)['amortisation_transaction_state']))
          
          AccountingTransaction_viewAccountingTransactionLineList = transaction.contentValues(filter={'portal_type': ('Accounting Transaction Line', 'Sale Invoice Transaction Line', 'Purchase Invoice Transaction Line', 'Amortisation Transaction Line')})
          sum = 0
          for transaction_line in AccountingTransaction_viewAccountingTransactionLineList:
            LOG('line : ', 0, '%s to %s (%s)' % (repr(transaction_line.getSource()), repr(transaction_line.getDestination()), repr(transaction_line.getQuantity())))
            quantity = transaction_line.getQuantity() or 0.0
            sum += quantity
          LOG('sum', 0, round(sum*100))
          
          self.getWorkflowTool().doActionFor(transaction, 'stop_action', 'amortisation_transaction_workflow')
          LOG('new status', 0, repr(self.getWorkflowTool().getStatusOf('amortisation_transaction_workflow', transaction)['amortisation_transaction_state']))
          LOG('rechanging', 0, repr(transaction))
          LOG('source_section =', 0, '%s, resource = %s' % (repr(transaction.getSourceSection()), repr(transaction.getResource())))
          self.getWorkflowTool().doActionFor(transaction, 'deliver_action', 'amortisation_transaction_workflow')
          LOG('new status', 0, repr(self.getWorkflowTool().getStatusOf('amortisation_transaction_workflow', transaction)['amortisation_transaction_state']))
          for transaction_line in AccountingTransaction_viewAccountingTransactionLineList:
            LOG('line : ', 0, '%s to %s (%s)' % (repr(transaction_line.getSource()), repr(transaction_line.getDestination()), repr(transaction_line.getQuantity())))
            LOG('line.getDeliveryRelated', 0, repr(transaction_line.getDeliveryRelatedValueList()))
          break
    
          
  def stepTic(self,**kw):
    portal = self.getPortal()
    LOG('Tic :', 0, 'before : %s' % repr(portal.portal_activities.getMessageList()))
    tries = 0
    while len(portal.portal_activities.getMessageList())>0:
      try:
        self.tic()
      except:
        LOG('TEST WARNING : error during tic', 0, '')
        # Wait for 2 minutes
        if tries < 5:
          from time import sleep
          sleep(120)
          tries += 1
        else:
          LOG('Timeout', 0, '')
          self.failUnless(0)
    LOG('Tic :', 0, 'after : %s' % repr(portal.portal_activities.getMessageList()))
    
    
  def stepAggregate(self, **kw):
    self.getPortal().AccountingTransactionModule_aggregateSimulationMovementsToAccounting(from_date=None, to_date=None)
    
    
  def stepVerifyAggregation(self, sequence=None, **kw):
    def cmpfunc(a,b):
      if a.getStopDate() - b.getStopDate() < 0: return -1
      if a.getStopDate() - b.getStopDate() > 0: return 1
      return 0

    # Gathering informations to test "delivery" category
    expected_simulation_movement_list = {}
    for name, value in self.simulation_value_list.items():
      if len(value) != 0:
        step = self.current_step.get(name, 0)
        for simulation_movement in value[step]:
          date                = simulation_movement['date']
          source_section      = simulation_movement['source_section']
          destination_section = simulation_movement['destination_section']
          source              = simulation_movement['source']
          destination         = simulation_movement['destination']
          value               = simulation_movement['value']
          if expected_simulation_movement_list.get( (date, source_section, destination_section, source, destination), None) is None:
            expected_simulation_movement_list[ (date, source_section, destination_section, source, destination) ] = []
          expected_simulation_movement_list[(date, source_section, destination_section, source, destination) ].append(value)
             
    aggregation_step = getattr(self,"aggregation_step",None)
    if aggregation_step is None:
      aggregation_step = 0
    LOG('aggregation_step', 0, aggregation_step)
    expected = deepcopy(self.aggregated[aggregation_step])
    self.aggregation_step = aggregation_step + 1
    
    accounting_transaction_list = list(self.getAccountingModule().objectValues())
    accounting_transaction_list.sort(cmpfunc)

    for accounting_transaction in accounting_transaction_list:
      # Check if this accounting transaction is expected
      expected_transaction = None
      i = 0
      date = accounting_transaction.getStopDate()
      source_section = accounting_transaction.getSourceSection()
      destination_section = accounting_transaction.getDestinationSection()
      LOG('testImmobilisation :',0,'verifying accounting transaction %s : destination_section=%s, source_section=%s, date=%s' % (repr(accounting_transaction.getId()), repr(destination_section), repr(source_section), repr(date)))
      LOG('testImmobilisation :',0, 'remaining expected transactions : %s' % repr(expected))
      while expected_transaction is None and i<len(expected):
        current_transaction = expected[i]
        expected_date = current_transaction['date']
        expected_source_section = current_transaction['source_section']
        expected_destination_section = current_transaction['destination_section']
        if expected_source_section is not None: expected_source_section = 'organisation/' + expected_source_section
        if expected_destination_section is not None: expected_destination_section = 'organisation/' + expected_destination_section
        if current_transaction['date'] == date and expected_source_section == source_section \
                                               and expected_destination_section == destination_section:
          expected_transaction = current_transaction
        i += 1
       
      self.failUnless(expected_transaction is not None)
      # We matched this accounting transaction with an expected one
      # Now we check if each of its lines matchs with an expected one
      #if expected_transaction is not None:
      for accounting_transaction_line in accounting_transaction.objectValues():
        # Check if this accounting transaction line is expected
        expected_transaction_line = None
        j = 0
        source = accounting_transaction_line.getSource()
        destination = accounting_transaction_line.getDestination()
        value = accounting_transaction_line.getQuantity()
        
        LOG('testImmobilisation :',0,'verifying accounting transaction  line %s : destination=%s, source=%s, value=%s' % (repr(accounting_transaction_line.getId()), repr(destination), repr(source), repr(value)))
        LOG('testImmobilisation :',0, 'remaining expected transaction lines : %s' % repr(expected_transaction['data']))
        while expected_transaction_line is None and j<len(expected_transaction['data']):
          current_transaction_line = expected_transaction['data'][j]
          expected_value = current_transaction_line['value']
          expected_source = current_transaction_line['source']
          expected_destination = current_transaction_line['destination']
          if expected_source is not None: expected_source = 'account/' + expected_source
          if expected_destination is not None: expected_destination = 'account/' + expected_destination
          if expected_source == source and expected_destination == destination \
                                       and self.roundedEquals(expected_value, value):
            expected_transaction_line = current_transaction_line
          j += 1
       
        self.failUnless(expected_transaction_line is not None)
        # The current accounting transaction line is matched, we delete it
        # in the "expected" data
        del expected_transaction['data'][j-1]
        
        # Check if "delivery" category is well formed
        simulation_movement_list = accounting_transaction_line.getDeliveryRelatedValueList()
        
        date = accounting_transaction.getStopDate()
        source_section = accounting_transaction.getSourceSection()
        destination_section = accounting_transaction.getDestinationSection()
        source = accounting_transaction_line.getSource()
        destination = accounting_transaction_line.getDestination()
        if source_section is not None:
          source_section = source_section.split('/')[-1]
        if destination_section is not None:
          destination_section = destination_section.split('/')[-1]
        if source is not None:
          source = source.split('/')[-1]
        if destination is not None:
          destination = destination.split('/')[-1]
        
        # To check the delivery category, we need to find which
        # simulation movements are expected in getDeliveryRelatedValueList
        expected_list = expected_simulation_movement_list.get( (date, source_section, destination_section, source, destination) , [])
        if expected_list is []:
          LOG('test :', 0, 'unable to find key "(%s,%s,%s,%s,%s)"... expected_simulation_movement_list = %s' % (repr(date), repr(source_section), repr(destination_section), repr(source), repr(destination), repr(expected_simulation_movement_list)))
        
        LOG('testImmobilisation :', 0, 'verifying DeliveryRelatedValueList for line %s... expected = %s, found = %s' % (repr(accounting_transaction_line.getId()), repr(expected_list), repr(simulation_movement_list)))
        for simulation_movement in simulation_movement_list:
          value = simulation_movement.getQuantity()
          LOG('testImmobilisation :', 0, 'in DeliveryRelatedValueList, verifying if we find %s in expected list' % repr(value))
          matching_movement = None
          j = 0
          while matching_movement is None and j<len(expected_list):
            current_movement = expected_list[j]
            LOG('testImmobilisation :', 0, 'current_movement = %s, value = %s' % (repr(current_movement), repr(value)))
            LOG('testImmobilisation :', 0, 'rounded current = %s, rounded value = %s' % (repr(round(current_movement,2)), repr(round(value, 2))))
            if self.roundedEquals(current_movement,value):
              matching_movement = current_movement
            j += 1
          
          self.failUnless(matching_movement is not None)
          if matching_movement == expected_list[j-1]:
            j -= 1
          del expected_list[j]   
        
          
      LOG('testImmobilisation :', 0, 'Verify if transaction %s is empty... remaining = %s' % (repr(accounting_transaction.getId()), repr(expected_transaction['data'])))
      # Deleting 0 remaining lines
      for i in range(len(expected_transaction['data'][:])):
        remaining_line = expected_transaction['data'][i]
        if remaining_line['value'] == 0:
          del expected_transaction['data'][i]
      self.assertEquals( len(expected_transaction['data']), 0 )
      
      del expected[i-1]
          
    LOG('testImmobilisation :', 0, 'Verify if all expected transaction have been matched... remaining = %s' % repr(expected))
    self.assertEquals(len(expected), 0)
        
      
    
  def testImmobilisation(self, quiet=0,run=1):
    sequence_list = SequenceList()
    
    # 1)
    # Linear amortisation
    # 4 movements. Depending on validity of each of them, different cases occur.
    # We play with validity to make a maximum of cases occur
    sequence_string = 'PrepareLinearTest Tic NextTestStep Tic VerifySimulation NextTestStep Tic VerifySimulation '
    sequence_string +=                      'NextTestStep Tic VerifySimulation NextTestStep Tic VerifySimulation '
    sequence_string +=                      'NextTestStep Tic VerifySimulation NextTestStep Tic VerifySimulation '
    sequence_string +=                      'NextTestStep Tic VerifySimulation'
    sequence_list.addSequenceString(sequence_string)

    # 2)
    # Degressive amortisation
    # Same as first test, with degressive amortisation
    sequence_string = 'PrepareDegressiveTest Tic NextTestStep Tic VerifySimulation NextTestStep Tic VerifySimulation '
    sequence_string +=                          'NextTestStep Tic VerifySimulation NextTestStep Tic VerifySimulation '
    sequence_string +=                          'NextTestStep Tic VerifySimulation NextTestStep Tic VerifySimulation '
    sequence_string +=                          'NextTestStep Tic VerifySimulation '
    sequence_list.addSequenceString(sequence_string)

    # 3)
    # Immobilisation movement are on the same day, exactly the same date
    # The behavior is uncertain and results should be wrong since sort is made on date, but the
    # expand process must not be broken.
    # No Simulation verification is made since it can change from a test to another
    sequence_string = 'PrepareSameDayTest Tic NextTestStep Tic NextTestStep Tic '
    sequence_string +=                       'NextTestStep Tic NextTestStep Tic '
    sequence_string +=                       'NextTestStep NextTestStep NextTestStep NextTestStep'
    sequence_list.addSequenceString(sequence_string)
    
    # 4)
    # Owner changing
    # Test the behavior of automatic acknowledgement of ownership change
    # Test also the behavior if sometimes deliveries are made on None during immobilisation period
    sequence_string = 'PrepareFirstOwnerChangeTest Tic NextTestStep Tic VerifySimulation NextTestStep Tic VerifySimulation '
    sequence_string +=                                'NextTestStep Tic VerifySimulation '
    sequence_list.addSequenceString(sequence_string)
    
    # 5)
    # Owner changing
    # Test the behavior of automatic acknowledgement of ownership change
    # This time, manual immobilisation movements are present. Verify if their date is correctly modified
    sequence_string = 'PrepareSecondOwnerChangeTest Tic NextTestStep Tic VerifySimulation NextTestStep Tic VerifySimulation '
    sequence_string +=                                 'NextTestStep Tic VerifySimulation NextTestStep Tic VerifySimulation '
    sequence_string +=                                 'NextTestStep Tic VerifySimulation '
    sequence_list.addSequenceString(sequence_string)
    
    # 6)
    # Owner changing
    # Test the behavior of automatic acknowledgement of ownership change
    # Same as the previous test, but immobilisation movements are located after the deliveries; they were located before on previous test
    sequence_string = 'PrepareThirdOwnerChangeTest Tic NextTestStep Tic VerifySimulation NextTestStep Tic VerifySimulation '
    sequence_string +=                                'NextTestStep Tic VerifySimulation NextTestStep Tic VerifySimulation '
    sequence_string +=                                'NextTestStep Tic VerifySimulation '
    sequence_list.addSequenceString(sequence_string)
    
    # 7)
    # Complex test
    # Item is immobilised and unimmobilised several times, with several deliveries, and some immobilisation are on the same
    # date as deliveries, but not only.
    sequence_string = 'PrepareComplexTest Tic NextTestStep Tic VerifySimulation NextTestStep Tic VerifySimulation '
    sequence_string +=                       'NextTestStep Tic VerifySimulation NextTestStep Tic VerifySimulation '
    sequence_string +=                       'NextTestStep Tic VerifySimulation NextTestStep Tic VerifySimulation '
    sequence_string +=                       'NextTestStep Tic VerifySimulation Aggregate VerifyAggregation'
    sequence_list.addSequenceString(sequence_string)

    # 8)
    # Actual use
    # Item is immobilised using the actual use amortisation method
    sequence_string = 'PrepareActualUseTest Tic NextTestStep Tic VerifySimulation NextTestStep Tic VerifySimulation'
    sequence_list.addSequenceString(sequence_string)
    
   
    ### The following tests verify the behavior when a reexpand is made after the aggregation
    # 9)
    # On linear test : no changes has been made, the simulation should have not changed
    # Then : change of the last immobilisation movement duration, it should change the annuities values and add some annuities
    # Then : change of disposal value to create some new movements to add to this period
    sequence_string =  'PrepareLinearTest Tic RetrieveData ArtificialExpand VerifySimulation '
    sequence_string += 'NextTestStep Tic VerifySimulation NextTestStep Tic VerifySimulation'
    sequence_list.addSequenceString(sequence_string)
    
    # 10)
    # On complex test : add an immobilisation movement, it should create a new period
    # then, change of the last immobilisation movement date, it should annulate some annuities
    sequence_string = 'PrepareComplexTest Tic RetrieveData Tic NextTestStep Tic VerifySimulation '
    sequence_string += 'Tic NextTestStep Tic VerifySimulation'
    sequence_list.addSequenceString(sequence_string)
    
    # 11)
    # On actual use test : change the last immobilisation movement date, it should create some annuities, and
    # relocate some movements
    sequence_string = 'PrepareActualUseTest Tic RetrieveData Tic NextTestStep Tic VerifySimulation'
    sequence_list.addSequenceString(sequence_string)
    
    # 12)
    # On degressive test : annulation of some immobilisation movements, it should annulate entire aggregated periods
    # Then : validate the transactions and reexpand, it should create correction movements
    # Then : validate and expand again, it should create correction movements takins in account existing correction movements
    # Then : re-expand, the created correction movements which are not validated should be modified
    sequence_string = 'PrepareDegressiveTest Tic RetrieveData Tic NextTestStep Tic '
    sequence_string += 'VerifySimulation Tic NextTestStep Tic VerifySimulation Tic DeleteAggregation '
    sequence_string += 'Aggregate Tic ValidateTransaction Tic NextTestStep Tic VerifySimulation Tic '
    sequence_string += 'Aggregate Tic ValidateTransaction Tic NextTestStep Tic VerifySimulation Tic NextTestStep Tic VerifySimulation '
    sequence_list.addSequenceString(sequence_string)
    
    # 13) 14) 15) 16)
    # To test the solvers, we clean the contents, then create a specific set of immobilisations
    #self.aggregation_step = 1
    sequence_string = 'CleanSimulation DeleteAggregation '
    sequence_list.addSequenceString(sequence_string)
    sequence_string = 'PrepareFirstSolverTest Tic NextTestStep Tic VerifySimulation'
    sequence_list.addSequenceString(sequence_string)
    sequence_string = 'PrepareSecondSolverTest Tic NextTestStep Tic VerifySimulation'
    sequence_list.addSequenceString(sequence_string)
    
    sequence_string = 'PrepareThirdSolverTest Tic NextTestStep Tic VerifySimulation Aggregate Tic VerifyAggregation VerifyConvergence '
    # And then modify and apply the solvers...
    # 1- updateFromSimulation : modify the duration => the quantity changes, and some movements are annulated
    sequence_string += 'NextTestStep Tic VerifySimulation ApplySolver Tic VerifyAggregation VerifyConvergence '
    # 2- updateFromSimulation : restore the duration, and modify an account => movements are annulated and recreated,
    #                           it just affects the lines
    sequence_string += 'NextTestStep Tic ApplySolver Tic VerifyAggregation VerifyConvergence '
    # 3- updateFromSimulation : modify the immobilisation date => movements are annulated and recreated, it affects transactions
    sequence_string += 'NextTestStep Tic VerifySimulation ApplySolver Tic VerifyAggregation VerifyConvergence '
    # 4- Clean the aggregation to be clearer, and reestablish the original conditions
    sequence_string += 'DeleteAggregation NextTestStep Tic VerifySimulation Aggregate Tic VerifyAggregation VerifyConvergence '
    # 5- ProfitAndLoss : quantity is doubled, profit_quantity should be set in some simulation movements
    sequence_string += 'ChangeTransactionProperties Tic IncrementStep ApplySolver VerifySimulation VerifyConvergence '
    # 6- ProfitAndLoss : source is modified, the movement should be disconnected
    sequence_string += 'ChangeTransactionProperties Tic IncrementStep ApplySolver VerifySimulation VerifyConvergence '
    # 7- ProfitAndLoss : a transaction is set to 0
    sequence_string += 'ChangeTransactionProperties Tic IncrementStep ApplySolver VerifySimulation VerifyConvergence '
    # 8- ProfitAndLoss : the previous transaction is reset to 8000
    sequence_string += 'ChangeTransactionProperties Tic IncrementStep ApplySolver VerifySimulation VerifyConvergence '
    # 9- ProfitAndLoss : another transaction is set to 0, then we add a non-0 simulation movement
    sequence_string += 'ChangeTransactionProperties Tic IncrementStep ApplySolver VerifySimulation VerifyConvergence '
    sequence_string += 'AddZeroSimulationMovement Tic IncrementStep ApplySolver VerifySimulation VerifyConvergence '
    
    sequence_list.addSequenceString(sequence_string)
    
    sequence_list.play(self)


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestImmobilisation))
        return suite
