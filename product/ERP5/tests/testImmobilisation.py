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
                  
  
  currency_list = [ 'EUR', 'USD' ]
  
  organisation_data_list = [ 
        { 'id':'nexedi', 'end_date':DateTime('2004/01/01'), 'currency':'EUR' },
        { 'id':'coramy', 'end_date':DateTime('2003/04/01'), 'currency':'EUR' }
     ]
     
     
  delivery_type = "Purchase Packing List"
  delivery_line_data_list = [
      { 'id':'1_1', 'parent_id':'1', 'items':['vpn_1', 'vpn_2', 'vpn_3'], 'date':'2000/01/01', 'source_section':None, 'destination_section':'nexedi' },
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
  
  
  immobilisation_movement_data_list = {
          # coef is optional in case of linear amortisation
          'linear_1' :        { 'value':300000., 'type':'linear',     'date':DateTime("2002/02/01"), 'amo_acc':'amortisation_1',
                                'vat' : 30000.,  'immobilisation': 1, 'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_1',  'in_acc':'in_out_1', 'out_acc' : 'in_out_2',        'depr_acc' : 'depreciation_1',
                                'duration' : 36,
                              },
          'linear_2' :        { 'date':DateTime("2003/09/14"), 'immobilisation':0, 'item':'vpn_1' },
          'linear_3' :        { 'value':100000., 'type':'linear',     'date':DateTime("2004/02/01"), 'amo_acc':'amortisation_1',
                                'vat'  : 10000., 'immobilisation': 1, 'immo_acc':'immobilisation_1', 'vat_acc':'vat_1',
                                'item':'vpn_1',  'in_acc':'in_out_1', 'out_acc' : 'in_out_2',        'depr_acc':'depreciation_1',
                                'duration' : 12
                              },
          'linear_4' :        { 'value': 50000., 'type':'linear',     'date':DateTime("2005/01/01"), 'amo_acc':'amortisation_1',
                                'vat' :   2000., 'immobilisation': 1, 'immo_acc':'immobilisation_1', 'vat_acc':'vat_1',
                                'item':'vpn_1',  'in_acc':'in_out_1', 'out_acc' : 'in_out_2',        'depr_acc':'depreciation_1',
                                'duration' : 5
                              },
          'degressive_1' :    { 'value':300000., 'type':'degressive', 'date':DateTime("2002/02/01"), 'amo_acc':'amortisation_1',
                                'vat' :  30000., 'immobilisation': 1, 'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_2', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',         'depr_acc' : 'depreciation_1',
                                'duration' : 120
                              },
          'degressive_2' :    { 'date':DateTime("2003/09/14"), 'immobilisation': 0,'item':'vpn_2' },
          'degressive_3' :    { 'value':169824.22, 'type':'degressive', 'date':DateTime("2004/02/01"), 'amo_acc':'amortisation_1',
                                'vat' :  16982.422, 'immobilisation': 1, 'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_2', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',         'depr_acc' : 'depreciation_1',
                                'duration' : 96
                              },
          'degressive_4' :    { 'value':100000., 'type':'degressive', 'date':DateTime("2005/01/01"), 'amo_acc':'amortisation_1',
                                'vat' :   5000., 'immobilisation': 1, 'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_2', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',         'depr_acc' : 'depreciation_1',
                                'duration' : 85
                              },
          'same_day_1' :      { 'date':DateTime("2003/01/01"), 'immobilisation':0, 'item':'vpn_3' },
          'same_day_2' :      { 'value':100000., 'type':'linear',     'date':DateTime("2003/01/01"), 'amo_acc':'amortisation_1',
                                'vat' :   5000., 'immobilisation': 1, 'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_3', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',         'depr_acc' : 'depreciation_1',
                                'duration' : 36 },
          'same_day_3' :      { 'date':DateTime("2003/01/01"), 'immobilisation':0, 'item':'vpn_3' },
          'same_day_4' :      { 'value':200000., 'type':'linear',     'date':DateTime("2003/01/01"), 'amo_acc':'amortisation_1',
                                'vat' :   5000., 'immobilisation': 1, 'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_3', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',         'depr_acc' : 'depreciation_1',
                                'duration' : 36 },
          'owner_change_1_1' :{ 'value': 30000., 'type':'linear',     'date':DateTime("2001/01/01"), 'amo_acc':'amortisation_1',
                                'vat' :   3000., 'immobilisation': 1, 'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_4', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',         'depr_acc' : 'depreciation_1',
                                'duration' : 36 },
          'owner_change_1_2' :{ 'date':DateTime("2001/03/01"), 'immobilisation':0, 'item':'vpn_4' },
          'owner_change_1_3' :{ 'value': 20000., 'type':'linear',     'date':DateTime("2002/07/06"), 'amo_acc':'amortisation_1',
                                'vat' :   2000., 'immobilisation': 1, 'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_4', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',         'depr_acc' : 'depreciation_1',
                                'duration' : 24 },
          'owner_change_2_1' :{ 'value':100000., 'type':'linear',     'date':DateTime("2001/01/01"), 'amo_acc':'amortisation_1',
                                'vat' :  10000., 'immobilisation': 1, 'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_5', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',         'depr_acc' : 'depreciation_1',
                                'duration' : 120 },
          'owner_change_2_2' :{ 'date':DateTime("2002/12/01"), 'immobilisation':0, 'item':'vpn_5' },
          'owner_change_2_3' :{ 'value': 50000., 'type':'linear',     'date':DateTime("2003/03/12") - 1/25., 'amo_acc':'amortisation_1',
                                'vat' :   5000., 'immobilisation': 1, 'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_5', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',         'depr_acc' : 'depreciation_1',
                                'duration' : 60 },
          'owner_change_2_4' :{ 'date':DateTime("2004/08/15"), 'immobilisation':0, 'item':'vpn_5' },
          'owner_change_2_5' :{ 'value': 20000., 'type':'linear',     'date':DateTime("2005/01/01") - 1/25., 'amo_acc':'amortisation_1',
                                'vat' :   2000., 'immobilisation': 1, 'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_5', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',         'depr_acc' : 'depreciation_1',
                                'duration' : 2 },
          'owner_change_3_1' :{ 'value':100000., 'type':'linear',     'date':DateTime("2001/01/01"), 'amo_acc':'amortisation_1',
                                'vat' :  10000., 'immobilisation': 1, 'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_6', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',         'depr_acc' : 'depreciation_1',
                                'duration' : 120 },
          'owner_change_3_2' :{ 'date':DateTime("2002/12/01"), 'immobilisation':0, 'item':'vpn_6' },
          'owner_change_3_3' :{ 'value': 50000., 'type':'linear',     'date':DateTime("2003/03/12") + 1/25., 'amo_acc':'amortisation_1',
                                'vat' :   5000., 'immobilisation': 1, 'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_6', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',         'depr_acc' : 'depreciation_1',
                                'duration' : 60 },
          'owner_change_3_4' :{ 'date':DateTime("2004/08/15"), 'immobilisation':0, 'item':'vpn_6' },
          'owner_change_3_5' :{ 'value': 20000., 'type':'linear',     'date':DateTime("2005/01/01") + 1/25., 'amo_acc':'amortisation_1',
                                'vat' :   2000., 'immobilisation': 1, 'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_6', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',         'depr_acc' : 'depreciation_1',
                                'duration' : 2 },
          'complex_1' :       { 'value':300000., 'type':'linear',     'date':DateTime("2001/06/12"), 'amo_acc':'amortisation_1',
                                'vat' :  30000., 'immobilisation': 1, 'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_7', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',         'depr_acc' : 'depreciation_1',
                                'duration' : 120 },
          'complex_2' :       { 'date':DateTime("2001/12/15"), 'immobilisation':0, 'item':'vpn_7' },
          'complex_3' :       { 'value':284712.33, 'type':'linear',     'date':DateTime("2002/06/01"), 'amo_acc':'amortisation_1',
                                'vat' :  28471.23, 'immobilisation': 1, 'immo_acc':'immobilisation_1', 'vat_acc':'vat_1', 'coef':2.5,
                                'item':'vpn_7', 'in_acc':'in_out_1',  'out_acc' :'in_out_2',         'depr_acc' : 'depreciation_1',
                                'duration' : 114 },
          'complex_4' :       { 'value':200000., 'type':'degressive',   'date':DateTime("2003/03/12")- 1/25., 'amo_acc':'amortisation_2',
                                'vat' :  15000., 'immobilisation': 1, 'immo_acc':'immobilisation_2', 'vat_acc':'vat_2', 'coef':2.5,
                                'item':'vpn_7', 'in_acc':'in_out_3',  'out_acc' :'in_out_4',         'depr_acc' : 'depreciation_2',
                                'duration' : 120 },
          'complex_5' :       { 'date':DateTime("2003/12/30"), 'immobilisation':0, 'item':'vpn_7' },
          'complex_6' :       { 'value':150000., 'type':'linear',   'date':DateTime("2006/06/24"), 'amo_acc':'amortisation_3',
                                'vat' :  15000., 'immobilisation': 1, 'immo_acc':'immobilisation_3', 'vat_acc':'vat_3', 'coef':2.5,
                                'item':'vpn_7', 'in_acc':'in_out_5',  'out_acc' :'in_out_6',         'depr_acc' : 'depreciation_3',
                                'duration' : 15 },
          'complex_7' :       { 'date':DateTime("2007/02/01") + 1/25., 'immobilisation':0, 'item':'vpn_7' },
                                
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
                                                  'complex_7'] } 


  validation_switch_list = { 'linear' :     [0,1,0],
                             'degressive' : [0,1,0] }
  
  
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
                                  'value': -  91780.82,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91780.82,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value': -   8219.18,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     8219.18,          'destination_section':None, 'destination':None, },
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
                                  'value': -  91780.82,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91780.82,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  91780.82,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -   9041.10,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':      821.92,          'destination_section':None, 'destination':None, },
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
                                  'value': -  91780.82,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91780.82,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  91780.82,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -   9041.10,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':      821.92,          'destination_section':None, 'destination':None, },
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
                                  'value': -  91780.82,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91780.82,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  91780.82,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -   9041.10,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':      821.92,          'destination_section':None, 'destination':None, },
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
                                  'value': -   8493.15,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     8493.15,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 300000.,            'destination_section':'nexedi', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'in_out_1',
                                  'value':   110000.,            'destination_section':'nexedi', 'destination':'in_out_2', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  10000.,            'destination_section':'nexedi', 'destination':'vat_1', },
                                { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':   200000.,            'destination_section':'nexedi', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 91780.82,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    91780.82,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   100000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  91780.82,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': -   9041.10,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':      821.92,          'destination_section':None, 'destination':None, },
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
                                  'value':  -   457.46,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':      457.46,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  9821.92,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     9821.92,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  2816.51,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     2816.51,          'destination_section':None, 'destination':None, },
                                
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
                                  'value':  -   546.19,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':      546.19,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  9967.94,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     9967.94,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  7510.09,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     7510.09,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  78082.19,          'destination_section':'coramy', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value':    66063.77,          'destination_section':'coramy', 'destination':'in_out_2', },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   6005.80,          'destination_section':'coramy', 'destination':'vat_1', },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    18024.22,          'destination_section':'coramy', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10009.66,          'destination_section':None, 'destination':None, },
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
                                  'value':  - 10079.31,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10079.31,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10079.31,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10079.31,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10079.31,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10079.31,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  1679.88,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     1679.88,          'destination_section':None, 'destination':None, },
                                
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
                                  'value':  -   546.19,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':      546.19,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  9967.94,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     9967.94,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  7510.09,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     7510.09,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': -  78082.19,          'destination_section':'coramy', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value':    66063.77,          'destination_section':'coramy', 'destination':'in_out_2', },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -   6005.80,          'destination_section':'coramy', 'destination':'vat_1', },
                                { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    18024.22,          'destination_section':'coramy', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10009.66,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10009.66,          'destination_section':None, 'destination':None, },
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
                                  'value':  - 10079.31,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10079.31,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10079.31,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10079.31,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 10079.31,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    10079.31,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  1679.88,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     1679.88,          'destination_section':None, 'destination':None, },
                                
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
                                  'value':  -  1644.25,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     1644.25,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 30007.47,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    30007.47,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 30007.47,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    30007.47,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 30007.47,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    30007.47,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  6823.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     6823.62,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 247561.64,          'destination_section':'coramy', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value':   163978.50,          'destination_section':'coramy', 'destination':'in_out_2', },
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  14907.137,         'destination_section':'coramy', 'destination':'vat_1', },
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    98490.28,          'destination_section':'coramy', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 15683.12,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    15683.12,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  2532.17,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     2532.17,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value': - 149071.37,          'destination_section':'nexedi', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'in_out_2',
                                  'value':   143941.68,          'destination_section':'nexedi', 'destination':'in_out_2', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'vat_1',
                                  'value': -  13085.608,         'destination_section':'nexedi', 'destination':'vat_1', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    18215.30,          'destination_section':'nexedi', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  4789.15,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     4789.15,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29627.79,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29627.79,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29627.79,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29627.79,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29627.79,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29627.79,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29627.79,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29627.79,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  7555.76,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     7555.76,          'destination_section':None, 'destination':None, },
                                
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
                                  'value':  - 17571.29,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    17571.29,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  5747.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5747.62,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value': - 284712.33,          'destination_section':'nexedi', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'in_out_2',
                                  'value':   287532.77,          'destination_section':'nexedi', 'destination':'in_out_2', },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'vat_1',
                                  'value': -  26139.342,         'destination_section':'nexedi', 'destination':'vat_1', },
                                { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    23318.90,          'destination_section':'nexedi', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  1636.91,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     1636.91,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29873.53,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29873.53,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29873.53,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29873.53,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29873.53,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2006/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29873.53,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  6793.16,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     6793.16,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value': - 261393.43,          'destination_section':'coramy', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value':   179677.03,          'destination_section':'coramy', 'destination':'in_out_2', },
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value': -  16334.27,         'destination_section':'coramy', 'destination':'vat_1', },
                                { 'date':DateTime('2006/06/23'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    98050.67,          'destination_section':'coramy', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  - 15622.32,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    15622.32,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  2522.35,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     2522.35,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'immobilisation_1',
                                  'value': - 163342.76,          'destination_section':'nexedi', 'destination':'immobilisation_1', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'in_out_2',
                                  'value':   159717.89,          'destination_section':'nexedi', 'destination':'in_out_2', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'vat_1',
                                  'value': -  14519.809,         'destination_section':'nexedi', 'destination':'vat_1', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    18144.67,          'destination_section':'nexedi', 'destination':'amortisation_1', },
                                # annuities
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  -  4773.64,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':     4773.64,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29531.81,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29531.81,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29531.81,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2009/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29531.81,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29531.81,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2010/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29531.81,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 29531.81,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2011/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    29531.81,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/04/01'), 'source_section':'coramy', 'source':'depreciation_1',
                                  'value':  - 22297.19,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2012/04/01'), 'source_section':'coramy', 'source':'amortisation_1',
                                  'value':    22297.19,          'destination_section':None, 'destination':None, },
                                
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
                                  'value':  - 17571.29,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    17571.29,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  5747.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5747.62,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   284712.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  23318.90,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 287532.77,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    26139.342,          'destination_section':None, 'destination':None, },
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
                                  'value':  - 17571.29,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    17571.29,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  5747.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5747.62,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   284712.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  23318.90,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 287532.77,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    26139.342,          'destination_section':None, 'destination':None, },
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
                                  'value':  - 17571.29,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    17571.29,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  5747.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5747.62,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   284712.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  23318.90,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 287532.77,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    26139.342,          'destination_section':None, 'destination':None, },
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
                                  'value':  - 62794.52,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_3',
                                  'value':    62794.52,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_3',
                                  'value':  - 10191.78,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_3',
                                  'value':    10191.78,          'destination_section':None, 'destination':None, },
                                # immobilisation end and start
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'immobilisation_3',
                                  'value': - 150000.,            'destination_section':'nexedi', 'destination':'immobilisation_3', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'in_out_6',
                                  'value':    84715.07,          'destination_section':'nexedi', 'destination':'in_out_6', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'vat_3',
                                  'value': -   7701.37,          'destination_section':'nexedi', 'destination':'vat_3', },
                                { 'date':DateTime('2007/02/01'), 'source_section':'coramy', 'source':'amortisation_3',
                                  'value':    72986.30,          'destination_section':'nexedi', 'destination':'amortisation_3', },
                                # annuities
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'depreciation_3',
                                  'value':  - 18673.18,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/04/01'), 'source_section':'coramy', 'source':'amortisation_3',
                                  'value':    18673.18,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/04/01'), 'source_section':'coramy', 'source':'depreciation_3',
                                  'value':  - 58340.51,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/04/01'), 'source_section':'coramy', 'source':'amortisation_3',
                                  'value':    58340.51,          'destination_section':None, 'destination':None, },
                                
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
                                  'value':  - 17571.29,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':    17571.29,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'depreciation_1',
                                  'value':  -  5747.62,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value':     5747.62,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'immobilisation_1',
                                  'value':   284712.33,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'amortisation_1',
                                  'value': -  23318.90,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'in_out_2',
                                  'value': - 287532.77,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'source':'vat_1',
                                  'value':    26139.342,          'destination_section':None, 'destination':None, },
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
                                  'value':  - 62794.52,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'source':'amortisation_3',
                                  'value':    62794.52,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'depreciation_3',
                                  'value':  - 10191.78,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'source':'amortisation_3',
                                  'value':    10191.78,          'destination_section':None, 'destination':None, },
                                # immobilisation end
                                { 'date':DateTime('2007/02/01'), 'source_section':'nexedi', 'source':'immobilisation_3',
                                  'value':   150000.,            'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/02/01'), 'source_section':'nexedi', 'source':'in_out_6',
                                  'value': -  84715.07,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/02/01'), 'source_section':'nexedi', 'source':'vat_3',
                                  'value':     7701.37,          'destination_section':None, 'destination':None, },
                                { 'date':DateTime('2007/02/01'), 'source_section':'nexedi', 'source':'amortisation_3',
                                  'value': -  72986.30,          'destination_section':None, 'destination':None, },
                                
                               ], # complex_1, complex_2, complex_3, complex_4, complex_5, complex_6, complex_7
                                
                 ],
                        
       }


  aggregated = [   { 'date':DateTime('2001/01/01'), 'source_section':'nexedi', 'destination_section':None,
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
                                        'data': [ { 'source':'depreciation_1',   'value': - 201033.62, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':   201033.62, 'destination':None, },
                                                  { 'source':'immobilisation_1', 'value': - 300000.,   'destination':None, },
                                                  { 'source':'in_out_1',         'value':   310000.,   'destination':None, },
                                                  { 'source':'vat_1',            'value': -  10000.,   'destination':None, } ] },
                   { 'date':DateTime('2003/03/12'), 'source_section':'coramy', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1', 'value': - 100000.,   'destination':None, },
                                                  { 'source':'in_out_1',         'value':   110000.,   'destination':None, },
                                                  { 'source':'vat_1',            'value': -  10000.,   'destination':None, },
                                                  { 'source':'immobilisation_2', 'value': - 200000.,   'destination':None, },
                                                  { 'source':'in_out_3',         'value':   215000.,   'destination':None, },
                                                  { 'source':'vat_2',            'value': -  15000.,   'destination':None, } ] },
                   { 'date':DateTime('2003/03/12'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1', 'value':   284712.33, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value': -  23318.904605623655, 'destination':None, },
                                                  { 'source':'in_out_2',         'value': - 287532.76517952414, 'destination':None, },
                                                  { 'source':'vat_1',            'value':    26139.342,'destination':None, } ] },
                   { 'date':DateTime('2003/03/15'), 'source_section':'coramy', 'destination_section':'nexedi',
                                        'data': [ { 'source':'immobilisation_1', 'value': -  20000.,   'destination':'immobilisation_1'},
                                                  { 'source':'in_out_2',         'value':    14405.48, 'destination':'in_out_2', },
                                                  { 'source':'vat_1',            'value': -   1309.59, 'destination':'vat_1', },
                                                  { 'source':'amortisation_1',   'value':     6904.11, 'destination':'amortisation_1'}]},
                   { 'date':DateTime('2003/04/01'), 'source_section':'coramy', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_2',   'value':  -  4166.67, 'destination':None, },
                                                  { 'source':'amortisation_2',   'value':     4166.67, 'destination':None, },
                                                  { 'source':'depreciation_1',   'value':  -  1553.35, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':     1553.35, 'destination':None, } ] },
                   { 'date':DateTime('2003/12/30'), 'source_section':'coramy', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_2', 'value':   200000.,   'destination':None, },
                                                  { 'source':'amortisation_2',   'value': -  40885.42, 'destination':None, },
                                                  { 'source':'in_out_4',         'value': - 171048.17708333334, 'destination':None, },
                                                  { 'source':'vat_2',            'value':    11933.59, 'destination':None, } ] },
                   { 'date':DateTime('2004/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',   'value': - 232226.78, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':   232226.78, 'destination':None, } ] },
                   { 'date':DateTime('2004/02/01'), 'source_section':'nexedi', 'destination_section':'nexedi',
                                        'data': [ { 'source':'in_out_1',         'value':   296806.64, 'destination':'in_out_2', },
                                                  { 'source':'immobilisation_1', 'value': - 600000.,   'destination':'immobilisation_1'},
                                                  { 'source':'vat_1',            'value': -  26982.42, 'destination':'vat_1' },
                                                  { 'source':'amortisation_1',   'value':   330175.78, 'destination':'amortisation_1'}]},
                   { 'date':DateTime('2004/04/01'), 'source_section':'coramy', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_2',   'value':  - 36718.75, 'destination':None, },
                                                  { 'source':'amortisation_2',   'value':    36718.75, 'destination':None, },
                                                  { 'source':'depreciation_1',   'value':  - 29821.92, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':    29821.92, 'destination':None, } ] },
                   { 'date':DateTime('2004/08/15'), 'source_section':'coramy', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1', 'value':   100000.,   'destination':None, },
                                                  { 'source':'amortisation_1',   'value': -  28547.95, 'destination':None, },
                                                  { 'source':'in_out_2',         'value': -  78597.26, 'destination':None, },
                                                  { 'source':'vat_1',            'value':     7145.21, 'destination':None, } ] },
                   { 'date':DateTime('2005/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_1', 'value':    79824.22, 'destination':None, },
                                                  { 'source':'in_out_1',         'value':   201000.,   'destination':None, },
                                                  { 'source':'vat_1',            'value':     1939.58, 'destination':None, },
                                                  { 'source':'depreciation_1',   'value': - 219201.48, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':    78773.10, 'destination':None, },
                                                  { 'source':'in_out_2',         'value': - 142335.42, 'destination':None, } ] },
                   { 'date':DateTime('2005/04/01'), 'source_section':'coramy', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',   'value':  - 10268.57, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':    10268.57, 'destination':None, } ] },
                   { 'date':DateTime('2006/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_1',   'value': - 187916.67, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':   187916.67, 'destination':None, } ] },
                   { 'date':DateTime('2006/06/24'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_3', 'value': - 150000.,   'destination':None, },
                                                  { 'source':'in_out_5',         'value':   165000.,   'destination':None, },
                                                  { 'source':'vat_3',            'value': -  15000.,   'destination':None, } ] },
                   { 'date':DateTime('2007/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_3',   'value':  - 62794.52, 'destination':None, },
                                                  { 'source':'amortisation_3',   'value':    62794.52, 'destination':None, },
                                                  { 'source':'depreciation_1',   'value': -  21484.38, 'destination':None, },
                                                  { 'source':'amortisation_1',   'value':    21484.38, 'destination':None, } ] },
                   { 'date':DateTime('2007/02/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'immobilisation_3', 'value':   150000.,   'destination':None, },
                                                  { 'source':'in_out_6',         'value': -  84715.07, 'destination':None, },
                                                  { 'source':'vat_3',            'value':     7701.37, 'destination':None, },
                                                  { 'source':'amortisation_3',   'value': -  72986.30, 'destination':None, } ] },
                   { 'date':DateTime('2008/01/01'), 'source_section':'nexedi', 'destination_section':None,
                                        'data': [ { 'source':'depreciation_3',   'value':  - 10191.78, 'destination':None, },
                                                  { 'source':'amortisation_3',   'value':    10191.78, 'destination':None, },
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
    #return ('erp5_core', 'copy_of_vpn', 'erp5_trade', 'erp5_accounting', 
    #        'nexedi_vpn', 'erp5_immobilisation')
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
    LOG('afterSetup',0,'portal.portal_categories.immediateReindexObject')
    portal.portal_categories.immediateReindexObject()
    for o in portal.portal_categories.objectValues():
      o.recursiveImmediateReindexObject()
    LOG('afterSetup',0,'portal.portal_simulation.immediateReindexObject')
    portal.portal_simulation.immediateReindexObject()
    for o in portal.portal_simulation.objectValues():
      o.recursiveImmediateReindexObject()
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
    self.getPortal().portal_types.constructContent(type_name='Amortisation Rule',
                        container=self.getPortal().portal_rules,
                        id='default_amortisation_rule')
    

                        
                        
  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('guillaume', '', ['Manager'], [])
    user = uf.getUserById('guillaume').__of__(uf)
    newSecurityManager(None, user)


    
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
    for property, property_sheet_name in ( ('value'         , 'AmortisationBeginningPrice'),
                                           ('type'          , 'AmortisationType'),
                                           ('date'          , 'StopDate'),
                                           ('immobilisation', 'Immobilisation'),
                                           ('duration'      , 'AmortisationDuration'),
                                           ('vat'           , 'Vat'),
                                           ('coef'          , 'FiscalCoefficient'),
                                           ('amo_acc'       , 'AmortisationAccount'),
                                           ('immo_acc'      , 'ImmobilisationAccount'),
                                           ('vat_acc'       , 'VatAccount'),
                                           ('in_acc'        , 'InputAccount'),
                                           ('out_acc'       , 'OutputAccount'),
                                           ('depr_acc'      , 'DepreciationAccount')  ):
      
      
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
    
    
  def stepNextTestStep(self, sequence=None, **kw):
    """
    Construct the next immobilisation needed for the current test
    If all of the immobilisations are already constructed, unvalidate or validate the
    next immobilisation to be validated or unvalidated
    """
    immobilisation_list_name = sequence.get('immobilisation_list_name')
    immobilisation_list = sequence.get('immobilisation_list') or []
    step = sequence.get('step_number')
    if step is None: step = -1
    step += 1
    
    LOG('testImmobilisation :', 0, 'step = %s, immobilisation_list = %s' % (repr(step), repr(immobilisation_list)))
    immobilisation_movement_list = self.immobilisation_movement_list[immobilisation_list_name]
    if step < len(immobilisation_movement_list):
      immobilisation_name = immobilisation_movement_list[step]
      immobilisation = self.constructImmobilisationMovement(immobilisation_name, sequence=sequence)
      immobilisation_list.append(immobilisation)
      
    else:
      # Validate or unvalidate the next immobilisation to be validated or unvalidated
      switch_list = self.validation_switch_list.get(immobilisation_list_name, None)
      switch_number = step - len(immobilisation_movement_list)
      LOG('stepNextTestStep :', 0, 'immobilisation_list_name=%s, switch_list=%s, switch_number=%s, switch_list[switch_number]=%s' % (repr(immobilisation_list_name), repr(switch_list), repr(switch_number), repr(switch_number)))
      if switch_list is not None and switch_number < len(switch_list):
        self.switchImmobilisationValidity( switch_list[switch_number], sequence=sequence )
        
    sequence.edit(immobilisation_list = immobilisation_list, step_number = step)
    
  
    
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
    else:
      immobilisation.setStopDate(None)
      
    item = immobilisation.getParent()
    item.immediateExpandAmortisation()
      
    
    
  def stepVerifySimulation(self, sequence=None, sequence_list=None, **kw):
    """
    Verify if the movements created in simulation correspond
    to the expected ones
    """    
    for delivery in self.getDeliveryModule().objectValues():
      for delivery_line in delivery.objectValues():  
        sql = 'select cat2.id from catalog as cat1, catalog as cat2, category where category.uid = cat1.uid '
        sql += 'and cat1.id = %s and cat2.uid = category.category_uid' % repr(delivery_line.getId())
        LOG('test :', 0, 'sql method on delivery %s : %s' % (repr(delivery_line.getId()), repr(map(lambda x:x['id'],self.sqlQuery(sql)))))
        LOG('test :', 0, 'aggregate value list = %s' % repr(delivery_line.getAggregateValueList()))
    
    
    
    current_step = sequence.get('step_number')
    immobilisation_list = sequence.get('immobilisation_list')
    item = immobilisation_list[0].getParent()
    test_name = sequence.get('immobilisation_list_name')
    
    expected = deepcopy(self.simulation_value_list[test_name][current_step])
    
    
    applied_rule_list = item.getCausalityRelatedValueList()
    LOG('testImmobilisation :',0,'verifying number of applied rules on item %s' % repr(item.getId()))
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    
    # Verify each written simulation movement
    LOG('testImmobilisation :', 0, 'applied rule... objectValues = %s, contentValues = %s' % (repr(applied_rule.objectValues()), repr(applied_rule.contentValues())))
    
    def cmpfunc(a,b):
      if a.getStopDate() - b.getStopDate() < 0: return -1
      if a.getStopDate() - b.getStopDate() > 0: return 1
      return 0
    
    simulation_movement_list = list(applied_rule.objectValues())
    LOG('test :', 0, 'simulation_movement_list = %s' % repr(simulation_movement_list))
    simulation_movement_list.sort(cmpfunc)
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
        #if self.areNear(current_movement['date'], date, 1/25. + 0.00001) \
        if current_movement['date'] == date and current_movement['source'] == source \
                                            and current_movement['destination'] == destination \
                                            and current_movement['source_section'] == source_section \
                                            and current_movement['destination_section'] == destination_section \
                                            and self.roundedEquals(current_movement['value'], value):
          #and self.areNear(current_movement['value'], value):
          expected_movement = current_movement
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
    
      
  def stepTic(self,**kw):
    portal = self.getPortal()
    LOG('Tic :', 0, 'before : %s' % repr(portal.portal_activities.getMessageList()))
    #portal.portal_activities.distribute()
    while len(portal.portal_activities.getMessageList())>0:
      self.tic()
    #portal.portal_activities.tic()
    LOG('Tic :', 0, 'after : %s' % repr(portal.portal_activities.getMessageList()))
    
    
  def stepAggregate(self, **kw):
    self.getPortal().Immobilisation_aggregateSimulationMovementsToAccounting(from_date=None, to_date=None)
    
  
    
  def stepVerifyAggregation(self, sequence=None, **kw):
    def cmpfunc(a,b):
      if a.getStopDate() - b.getStopDate() < 0: return -1
      if a.getStopDate() - b.getStopDate() > 0: return 1
      return 0

    
    # Gathering informations to test "delivery" category
    expected_simulation_movement_list = {}
    for value in self.simulation_value_list.values():
      if len(value) != 0:
        for simulation_movement in value[-1]:
          date                = simulation_movement['date']
          source_section      = simulation_movement['source_section']
          destination_section = simulation_movement['destination_section']
          source              = simulation_movement['source']
          destination         = simulation_movement['destination']
          value               = simulation_movement['value']
          if expected_simulation_movement_list.get( (date, source_section, destination_section, source, destination), None) is None:
            expected_simulation_movement_list[ (date, source_section, destination_section, source, destination) ] = []
          expected_simulation_movement_list[(date, source_section, destination_section, source, destination) ].append(value)
          
    
    expected = deepcopy(self.aggregated)
    
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
            #and self.areNear(expected_value, value, 0.04):
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
        # simulations movements are expected in getDeliveryRelatedValueList
        expected_list = expected_simulation_movement_list.get( (date, source_section, destination_section, source, destination) , None)
        if expected_list is None:
          LOG('test :', 0, 'unable to find key "(%s,%s,%s,%s,%s)"... expected_simulation_movement_list = %s' % (repr(date), repr(source_section), repr(destination_section), repr(source), repr(destination), repr(expected_simulation_movement_list)))
          self.failUnless(0)
        
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
    # I noticed a strange behavior in this case during previous tests, so this test is required
    # Behavior is uncertain and results should be wrong since sort is made on date, but the expand process must not be broken
    sequence_string = 'PrepareSameDayTest Tic NextTestStep Tic VerifySimulation NextTestStep Tic VerifySimulation '
    sequence_string +=                       'NextTestStep Tic VerifySimulation NextTestStep Tic VerifySimulation '
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
    
    
    
    sequence_list.play(self)



if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestImmobilisation))
        return suite

