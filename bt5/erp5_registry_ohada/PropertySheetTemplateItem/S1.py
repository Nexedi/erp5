# -*- coding: utf-8 -*-
#############################################################################
#
# Copyright (c) 2002-2005 Nexedi SARL and Contributors. All Rights Reserved.
#                         Jean-Paul Smets-Solanes <jp@nexedi.com>
#                         Kevin Deldycke <kevin_AT_nexedi_DOT_com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################


class S1:
  """
    Autorisation properties and categories
  """

  _properties = (
    # Autorisation properties
    { 'id'         : 'actions_check'
    , 'description': 'Actions'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'head_office_address'
    , 'description': 'Adresse du siège'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'affluent_goods_actions_check'
    , 'description': 'Actions'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'affluent_goods_description'
    , 'description': 'Description des biens nantis'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'affluent_goods_goodwill_check'
    , 'description': 'Fonds de commerce'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'affluent_goods_mat_prof_check'
    , 'description': 'Materiel Professionnel'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'affluent_goods_patent_check'
    , 'description': 'Brevet'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'affluent_goods_stock_check'
    , 'description': 'Stocks'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'affluent_goods_vehicle_check'
    , 'description': 'Vehicules'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'applicant'
    , 'description': 'Le soussigne'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'capital'
    , 'description': 'Capital'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'credit_acts'
    , 'description': 'Actes deposes'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'credit_amount'
    , 'description': 'Montant du credit'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'credit_date'
    , 'description': 'Date'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'credit_title'
    , 'description': 'Titre constitutif'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'documents_nature'
    , 'description': 'Nature des documents deposes'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'goods_location'
    , 'description': 'Localisation future des biens susceptibles d etre deplaces'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'goodwill_check'
    , 'description': 'Fonds de Commerce'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'hypothecation_capital'
    , 'description': 'Capital'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'hypothecation_date'
    , 'description': 'Date'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'hypothecation_description'
    , 'description': 'Preciser'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'hypothecation_person_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'hypothecation_person_corporate_registration_code'
    , 'description': 'RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'hypothecation_person_title'
    , 'description': 'Denomination'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'hypothecation_corporate_registration_code'
    , 'description': 'RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'inscription_check'
    , 'description': 'Inscription'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'liability_conditions'
    , 'description': 'Conditions d exigibilite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'mat_prof_check'
    , 'description': 'Materiel Professionnel'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'modified_check'
    , 'description': 'Modifications'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'no_check'
    , 'description': 'Non'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'patent_check'
    , 'description': 'Brevet'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'place'
    , 'description': 'Fait a'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'previous_inscriptions'
    , 'description': 'INDIQUER'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'radiation'
    , 'description': 'Radiation a concurrence de'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'radiation_check'
    , 'description': 'Radiation'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'rccm_modification_check'
    , 'description': 'Demande de modification au RCCM'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'rccm_radiation_check'
    , 'description': 'Demande de Radiation au RCCM'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'rccm_registration_check'
    , 'description': 'Demande d immatriculation au RCCM'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'source_reference'
    , 'description': 'RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'inscription_person_corporate_registration_code'
    , 'description': 'RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'registration_date'
    , 'description': 'Le'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'registration_number'
    , 'description': 'NUMERO'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'renewal_check'
    , 'description': 'Renouvellement'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'residence'
    , 'description': 'Election de residence'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'signature'
    , 'description': 'Signature'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'stock_check'
    , 'description': 'Stocks'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'title'
    , 'description': 'Denomination'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'vehicle_check'
    , 'description': 'Vehicules'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'yes_check'
    , 'description': 'OUI'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
)
