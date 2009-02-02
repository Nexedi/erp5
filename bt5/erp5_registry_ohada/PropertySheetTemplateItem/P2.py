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


class P2:
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
    { 'id'         : 'buyers_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'buyers_date'
    , 'description': 'Date'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'buyers_name'
    , 'description': 'Acquereur'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'closed_date'
    , 'description': 'Date'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'owner_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'owner_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'company_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'applicant'
    , 'description': 'Le soussigne'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'company_modifications'
    , 'description': 'Modification de l entreprise'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'company_modified_added_activities'
    , 'description': 'Activites ajoutees'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'company_modified_name'
    , 'description': 'RCCM'
    , 'type'       : 'string'
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
    { 'id'         : 'company_modified_removed_activities'
    , 'description': 'Activites supprimees'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'company_old_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'company_old_name'
    , 'description': 'Ancien'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'establishment_modification'
    , 'description': 'Modification de l etablissement'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_going_check'
    , 'description': 'Partant'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_maintained_check'
    , 'description': 'Maintenu'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_new_check'
    , 'description': 'Nouveau'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'modified_added_activities'
    , 'description': 'Activites ajoutees'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'modified_removed_activities'
    , 'description': 'Activites supprimees'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'new_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'corporate_registration_code'
    , 'description': 'RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'establishment_corporate_registration_code'
    , 'description': 'RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'company_corporate_registration_code'
    , 'description': 'RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_modification_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_citizenship'
    , 'description': 'Nationalite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_first_name'
    , 'description': 'Fax'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_last_name'
    , 'description': 'Noms et Pr�noms'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_name'
    , 'description': 'Prenoms'
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
    { 'id'         : 'non_check'
    , 'description': 'Mari�'
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
    { 'id'         : 'opening_date'
    , 'description': 'Date d ouverture'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'other'
    , 'description': 'Autres'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'rccm_check'
    , 'description': 'Demande d immatriculation au RCCM'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'owner_address'
    , 'description': 'Domicile'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'owner_birthdate'
    , 'description': 'Date et lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'owner_citizenship'
    , 'description': 'Nationalite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'owner_divorced_check'
    , 'description': 'Divorce'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'owner_first_name'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'owner_last_name'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'owner_married_check'
    , 'description': 'Marie'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'place'
    , 'description': 'Fait �'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'owner_residency_permit'
    , 'description': 'Titre de sejour'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'owner_single_check'
    , 'description': 'Celibataire'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'owner_validity_date'
    , 'description': 'Date de validite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'owner_widower_check'
    , 'description': 'Veuf'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'radiation_rccm_check'
    , 'description': 'Demande de radiation au RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'previous_activity_yes_check'
    , 'description': 'OUI'
    , 'type'       : 'string'
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
    { 'id'         : 'previous_owner_rccm'
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
    { 'id'         : 'second_administrator_birthplace'
    , 'description': 'Lieu de naissance'
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
    , 'description': 'First Name'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_last_name'
    , 'description': 'Noms et Pr�noms'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_going_check'
    , 'description': 'Partant'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_maintained_check'
    , 'description': 'Maintenu'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_new_check'
    , 'description': 'Nouveau'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_modification_date'
    , 'description': 'Date de modification'
    , 'type'       : 'date'
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
    { 'id'         : 'third_spouse_restrictive_clauses'
    , 'description': 'Clauses Restrictives'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'transferred_address'
    , 'description': 'Ancienne Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'transferred_date'
    , 'description': 'Date'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'identification_check'
    , 'description': 'Identification'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'activity_check'
    , 'description': 'Activites'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'administrators_check'
    , 'description': 'Dirigeants'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'transfer_check'
    , 'description': 'Transfert'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'person_registration_number'
    , 'description': 'Registry Number'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'source_reference'
    , 'description': 'Report Number'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'closing_check'
    , 'description': 'Fermeture'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },  
  )

