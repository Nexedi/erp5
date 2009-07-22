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


class P4:
  """
    Autorisation properties and categories
  """

  _properties = (
    # Autorisation properties
    { 'id'         : 'accident_check'
    , 'description': 'Accident'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'agent_signature'
    , 'description': 'Signature de l agent'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'another'
    , 'description': 'Cessation temporaire'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ask_to_change_check'
    , 'description': 'title of the organisation of the form'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ask_to_delete_check'
    , 'description': 'Adresse'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'benefit'
    , 'description': 'Benefit'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'another_cause'
    , 'description': 'Autre cause de cessation temporaire'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'owner_birthplace'
    , 'description': 'Birthdate Place'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'owner_birthday'
    , 'description': 'Owner Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    }, 
    { 'id'         : 'beneficiary_identity'
    , 'description': 'Beneficiary Identity'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'beneficiary_address'
    , 'description': 'Beneficiary Address'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'beneficiary_rccm'
    , 'description': 'Beneficiary RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'consequences'
    , 'description': 'Consequences'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'deces'
    , 'description': 'Deces'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'definitive_check'
    , 'description': 'Definitive'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'disappear_check'
    , 'description': 'Disparait'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'disaster_check'
    , 'description': 'Disaster'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'disparition_check'
    , 'description': 'Disparition'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'enterprise_address'
    , 'description': 'Address of enterprise'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'correspondent_address'
    , 'description': 'Address of correspondent'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'correspondent_identity'
    , 'description': 'Correspondent Identity'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'stop_temporary_activity_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_date'
    , 'description': 'Registration Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'heir_info'
    , 'description': 'Nom, Domiciliation,...'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'is_sold_check'
    , 'description': 'Sold'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_name'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'location_gerence'
    , 'description': 'Location gerance'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'managed_location_check'
    , 'description': 'Managed Location'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'owner_last_name'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'owner_first_name'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'owner_citizenship'
    , 'description': 'Nationalite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'no_check'
    , 'description': 'Non'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'registration_number'
    , 'description': 'Number'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'source_reference'
    , 'description': 'Report Number'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'registration_date'
    , 'description': 'Registration Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'personal_address'
    , 'description': 'Adresse Personnelle'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'place'
    , 'description': 'Place'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_address'
    , 'description': 'Second Address'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_another_cause'
    , 'description': 'Noms et Pr�noms'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_autre'
    , 'description': 'Autre'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_benefit'
    , 'description': 'Benefit'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_rccm'
    , 'description': 'RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_spouse_restrictives_clauses'
    , 'description': 'Clauses Restrictives'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'last_name'
    , 'description': 'Nom de famille'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sickness_check'
    , 'description': 'Maladie'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'signature'
    , 'description': 'Signature'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'temporary_check'
    , 'description': 'Temporaire'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_another_cause'
    , 'description': 'Another cause of cessation'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_another_cause_check'
    , 'description': 'Autre'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'vente'
    , 'description': 'Vente'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'with_check'
    , 'description': 'With'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'without_check'
    , 'description': 'Without'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'yes_check'
    , 'description': 'Yes'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
  )

