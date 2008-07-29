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


class M4:
  """
    Autorisation properties and categories
  """

  _properties = (
    # Autorisation properties
    { 'id'         : 'moral_person'
    , 'description': 'if an annexe is checked or not'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_company'
    , 'description': 'Ouverture d un etablissement secondaire'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'activity_restart_check'
    , 'description': 'if an annexe is checked or not'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'corporate_name'
    , 'description': 'title of the organisation of the form'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'head_office_address'
    , 'description': 'Adresse du siège'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'logo'
    , 'description': 'Enseigne Sigle'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'work_address'
    , 'description': 'Adresse de l etablissement'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'legal_form'
    , 'description': 'Forme Juridique'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'default_address_city'
    , 'description': 'Fait à'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'applicant'
    , 'description': 'Le soussigne'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'capital'
    , 'description': 'Capital Social'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'contribution_check'
    , 'description': 'Apport'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'creation_check'
    , 'description': 'Creation'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'date'
    , 'description': 'Le'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'registration_date'
    , 'description': 'Le'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'donation'
    , 'description': 'Donts en nature'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'duration'
    , 'description': 'Duree'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sold_check'
    , 'description': 'Vendu'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'starting_date'
    , 'description': 'A COMPTER DU'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'brought_check'
    , 'description': 'Apporte'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'beginning_date'
    , 'description': 'Date de debut'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'divorced_check'
    , 'description': 'If the optique is checked or not'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'branch'
    , 'description': 'Ouverture d une succursale d une personne morale etrangere'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'birthdate'
    , 'description': 'Date et Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'reported_date'
    , 'description': 'Date Report�e'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'employees_number'
    , 'description': 'Nombre d employes'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_garanty_person_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_garanty_person_birthdate'
    , 'description': 'Nationalit�'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_garanty_person_citizenship'
    , 'description': 'Email'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_garanty_person_firstname'
    , 'description': 'Fax'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_garanty_person_lastname'
    , 'description': 'Noms et Pr�noms'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_name'
    , 'description': 'T�l�phone'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_spouse_birthdate'
    , 'description': 'Date et Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_spouse_fullname'
    , 'description': 'Noms et pr�noms'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_spouse_matrimonial_situation'
    , 'description': 'Situation Matrimoniale'
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
    { 'id'         : 'main_activity'
    , 'description': 'Activit� principale'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'main_company'
    , 'description': 'Principal �tablissement'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'opening'
    , 'description': 'Ouverture d un etablissement secondaire'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'numerous_donations'
    , 'description': 'Donts Numeraires'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'opening_date'
    , 'description': 'Date d ouverture'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'other_check'
    , 'description': 'Autres'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'rccm_check'
    , 'description': 'Demande d immatriculation au RCCM'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'other_companies_check'
    , 'description': 'Autres etablissements'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'total_suspensionof_activities'
    , 'description': 'Cessation totale d activite'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'liquidation_check'
    , 'description': 'Liquidation'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'purchase_check'
    , 'description': 'Achat'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'rent_check'
    , 'description': 'Prise en location gerance'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'recipient_fullname'
    , 'description': 'Nom,Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'place'
    , 'description': 'Fait �'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'recipient_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'recipient_corporate_registration_code'
    , 'description': 'RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'previous_owner_firstname'
    , 'description': 'Prenoms'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'previous_owner_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'previous_owner_rccm'
    , 'description': 'RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'registration_number'
    , 'description': 'NUMERO'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_company_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_company_corporate_registration_code'
    , 'description': 'RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_company_sold_check'
    , 'description': 'Vendu'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_company_brought_check'
    , 'description': 'Apporte.'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_company_contribution_check'
    , 'description': 'Apport'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_company_rent_check'
    , 'description': 'Mis en location gerance'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_company_disappeared_check'
    , 'description': 'Disparait'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_company_recipient_fullname'
    , 'description': 'Nom,Prenoms'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_company_recipient_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_company_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_company_recipient_corporate_registration_code'
    , 'description': 'RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_company_sold_check'
    , 'description': 'Vendu'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_company_brought_check'
    , 'description': 'Apporte.'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_company_contribution_check'
    , 'description': 'Apport'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_company_rent_check'
    , 'description': 'Mis en location gerance'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_company_disappeared_check'
    , 'description': 'Disparait'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_company_recipient_fullname'
    , 'description': 'Nom,Prenoms'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_company_recipient_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_company_recipient_corporate_registration_code'
    , 'description': 'RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_company_corporate_registration_code'
    , 'description': 'RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'received_date'
    , 'description': 'Date de fusion ou scission'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'participating_people'
    , 'description': 'Nom, Prenom et RCCM des personnes ayant participe a l operation'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'liquidation_date'
    , 'description': 'Date de liquidation'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'report_number'
    , 'description': 'Numero de formalite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'permanent_address'
    , 'description': 'Adresse permanente'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_auditor_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'signature'
    , 'description': 'Signature'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'source_reference'
    , 'description': 'Numero de formalite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
  )

