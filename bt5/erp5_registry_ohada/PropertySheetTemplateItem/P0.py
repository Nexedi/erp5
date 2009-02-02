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


class P0:
  """
    Autorisation properties and categories
  """

  _properties = (
    # Autorisation properties
    { 'id'         : 'activity_restart_check'
    , 'description': 'Reprise d activite'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'beginning'
    , 'description': 'Debut'
    , 'type'       : 'boolean'
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
    { 'id'         : 'loueur_de_fonds'
    , 'description': 'Loueur de fonds'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'loueur_de_fonds_extra'
    , 'description': 'Loueur de fonds'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'source_reference'
    , 'description': 'Numero de formalite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'beginning_date'
    , 'description': 'Date de debut'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'citizenship'
    , 'description': 'Nationalite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'divorced_check'
    , 'description': 'Divorce'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'employes_number'
    , 'description': 'Nombre d employes'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_citizenship'
    , 'description': 'Nationalite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_first_name'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_last_name'
    , 'description': 'Noms'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'default_birthplace_address_city'
    , 'description': 'The birthplace of the person'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_name'
    , 'description': 'Prenoms'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'start_date'
    , 'description': 'Date of birth.'
    , 'storage_id' : 'start_date'
    , 'type'       : 'date'
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
    { 'id'         : 'main_activity_free_text'
    , 'description': 'Activit� principale'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_company_activity_free_text'
    , 'description': 'Activit� principale'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'main_company'
    , 'description': 'Principal �tablissement'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'married_check'
    , 'description': 'Mari�'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'inscription_check'
    , 'description': 'Demande d inscription au RCCM'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'miss_check'
    , 'description': 'Mlle'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'mrs_check'
    , 'description': 'Mme'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'mr_check'
    , 'description': 'Mr'
    , 'type'       : 'boolean'
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
    { 'id'         : 'second_company_opening_date'
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
    { 'id'         : 'other_check_info'
    , 'description': 'Autres(pr�ciser)'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'other_companies'
    , 'description': 'Etablissements secondaires'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'other_companies_corporate_registration_code'
    , 'description': 'Identit� de l exploitant'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_company_not_exists_check'
    , 'description': 'A second company not exists'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_company_exists_check'
    , 'description': 'A second company exists'
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
    { 'id'         : 'report_number'
    , 'description': 'Numero de formalite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'place'
    , 'description': 'Fait à'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'previous_activity_beginning_period'
    , 'description': 'Periode de'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'previous_activity_end_period'
    , 'description': 'A'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'previous_activity_nature'
    , 'description': 'Nature de l activite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'previous_activity_non_check'
    , 'description': 'NON'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'previous_activity_corporate_registration_code'
    , 'description': 'Identite de l exploitant precedent'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'previous_activity_yes_check'
    , 'description': 'OUI'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'previous_owner_address'
    , 'description': 'Adresse'
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
    { 'id'         : 'previous_owner_corporate_registration_code'
    , 'description': 'RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'previous_owner_identity'
    , 'description': 'Identite de l exploitant'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'residency_permit'
    , 'description': 'Titre de sejour'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'real_address'
    , 'description': 'Adresse reelle'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'registration_number'
    , 'description': 'NUMERO'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_citizenship'
    , 'description': 'Nationalite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_first_name'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_last_name'
    , 'description': 'Noms'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_spouse_birthdate'
    , 'description': 'Date et Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_spouse_fullname'
    , 'description': 'Noms,Prenoms'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_spouse_matrimonial_situation'
    , 'description': 'Regime Matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_spouse_restrictive_clauses'
    , 'description': 'Clauses Restrictives'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'signature'
    , 'description': 'Noms et Pr�noms'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'single_check'
    , 'description': 'Celibataire'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_spouse_birthdate'
    , 'description': 'Date et Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_spouse_fullname'
    , 'description': 'Noms,Prenoms'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_spouse_matrimonial_situation'
    , 'description': 'Regime Matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'source_reference'
    , 'description': 'Numero de formalite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_spouse_restrictive_clauses'
    , 'description': 'Clauses Restrictives'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'person_registration_number'
    , 'description': 'Registry Number'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'validity_date'
    , 'description': 'Date de validite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'widower_check'
    , 'description': 'Veuf'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
  )

