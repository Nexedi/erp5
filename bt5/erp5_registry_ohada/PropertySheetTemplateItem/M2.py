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


class M2:
  """
    M2 properties and categories
  """

  _properties = (
    # M2 properties
    { 'id'         : 'new_corporate_registration_code'
    , 'description': 'RCCM du siege'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'activity_free_text'
    , 'description': 'Activite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'auditor_first_no_check'
    , 'description': 'Non'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'auditor_first_yes_check'
    , 'description': 'OUI'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'activities_check'
    , 'description': 'Activites'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'activity_check'
    , 'description': 'Check if there is more activities in a m2 bis sub form'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'added_activities'
    , 'description': 'Activites ajoutees'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'added_activities_date'
    , 'description': 'Date'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'auditor_second_no_check'
    , 'description': 'NON'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'auditor_second_yes_check'
    , 'description': 'OUI'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'buyers_address'
    , 'description': 'Ancienne adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'buyers_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'buyers_name'
    , 'description': 'Acquereur'
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
    { 'id'         : 'capital_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'characteristics_check'
    , 'description': 'Caracteristiques'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'closing_check'
    , 'description': 'Fermeture'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'closed_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'commercial_name_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'company_check'
    , 'description': 'ETABLISSEMENT'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'old_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'deleted_activities'
    , 'description': 'Activite Supprimees'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'deleted_activities_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'dissolved_check'
    , 'description': 'Dissolution'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'beginning_date'
    , 'description': 'Date de debut'
    , 'type'       : 'date'
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
    { 'id'         : 'other_companies_rccm'
    , 'description': 'Identit� de l exploitant'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'oui_check'
    , 'description': 'OUI'
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
    , 'description': 'Fait �'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'registration_number'
    , 'description': 'NUMERO'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_registration_number'
    , 'description': 'NUMERO'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_fullname'
    , 'description': 'PRENOMS'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_lastname'
    , 'description': 'NOM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_firstname'
    , 'description': 'NUMERO'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_birthday'
    , 'description': 'Date et lieu de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eight_administrator_another_info'
    , 'description': 'Date et lieu de naissance,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eight_administrator_fullname'
    , 'description': 'NOM,PRENOM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_associate_another_info'
    , 'description': 'Date et lieu de naissance,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_associate_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_associate_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_associate_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_administrator_another_info'
    , 'description': 'Date et lieu de naissance,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_administrator_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_administrator_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_administrator_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_auditor_another_info'
    , 'description': 'Date et lieu de naissance,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_auditor_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_auditor_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_auditor_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_auditor_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_fullname'
    , 'description': 'Nom,Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_going_check'
    , 'description': 'Partant'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_identity'
    , 'description': 'Identite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_maintained_check'
    , 'description': 'Maintenu'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_new_check'
    , 'description': 'Nouveau'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_new_quality'
    , 'description': 'Nouvelle qualite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_old_quality'
    , 'description': 'Ancienne qualite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_modified_check'
    , 'description': 'Modifiee'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_auditor_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_auditor_fullname'
    , 'description': 'NOM,PRENOMS,DOMICILE PERSONNEL'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_fullname'
    , 'description': 'Nom,Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_going_check'
    , 'description': 'Partant'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_identity'
    , 'description': 'Identite'
    , 'type'       : 'string'
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
    { 'id'         : 'first_administrator_new_quality'
    , 'description': 'Nouvelle qualite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_old_quality'
    , 'description': 'Ancienne qualite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_modified_check'
    , 'description': 'Modifiee'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_rccm_check'
    , 'description': 'Demande d immatriculation au RCCM'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_associate_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_associate_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_associate_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_associate_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_administrator_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_administrator_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_administrator_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_administrator_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_auditor_another_info'
    , 'description': 'Date et Lieu de naissance, de mariage,regime matrimonial,etc...'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_auditor_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_auditor_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_auditor_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_auditor_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'initials'
    , 'description': 'SIGLE'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'legal_form_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'administrators_check'
    , 'description': 'Dirigeants'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'modified_added_activities'
    , 'description': 'Activites ajoutees'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'modified_deleted_activities'
    , 'description': 'Activites supprimees'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'moral_person_check'
    , 'description': 'Personne Morale'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'new_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    }, 
    { 'id'         : 'new_capital'
    , 'description': 'Nouveau'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'new_commercial'
    , 'description': 'Nouveau'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'new_headquarters'
    , 'description': 'Nouveau Siege'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'new_legal_form'
    , 'description': 'Forme Juridique'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'old_capital'
    , 'description': 'Capital'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    }, 
    { 'id'         : 'new_title'
    , 'description': 'New commercial name'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'old_title'
    , 'description': 'Old commercial name'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'old_headquarters'
    , 'description': 'Ancien Siege'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'old_legal_form'
    , 'description': 'Forme Juridique'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'old_corporate_registration_code'
    , 'description': 'Ancien RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    }, 
    { 'id'         : 'other'
    , 'description': 'Autre'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'other_reason'
    , 'description': 'Autre'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'registration_date'
    , 'description': 'Le'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_fullname'
    , 'description': 'Nom,Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_going_check'
    , 'description': 'Partant'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_identity'
    , 'description': 'Identite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_maintained_check'
    , 'description': 'Maintenu'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_new_check'
    , 'description': 'Nouveau'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_new_quality'
    , 'description': 'Nouvelle qualite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_old_quality'
    , 'description': 'Ancienne qualite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_modified_check'
    , 'description': 'Modifiee'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_auditor_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_auditor_fullname'
    , 'description': 'NOM,PRENOMS,DOMICILE PERSONNEL'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_fullname'
    , 'description': 'Nom,Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_going_check'
    , 'description': 'Partant'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_identity'
    , 'description': 'Identite'
    , 'type'       : 'string'
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
    { 'id'         : 'second_administrator_new_quality'
    , 'description': 'Nouvelle qualite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_old_quality'
    , 'description': 'Ancienne qualite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_modified_check'
    , 'description': 'Modifiee'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_rccm_check'
    , 'description': 'Demande d immatriculation au RCCM'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_place'
    , 'description': 'Fait a'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_registration_date'
    , 'description': 'le'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_registration_number'
    , 'description': 'Numero'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_signature'
    , 'description': 'Signature'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_associate_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    {
     'id'         : 'seventh_associate_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
     { 'id'         : 'seventh_associate_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_associate_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_administrator_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    {
     'id'         : 'seventh_administrator_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_administrator_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_administrator_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_auditor_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    {
     'id'         : 'seventh_auditor_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_auditor_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_auditor_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_auditor_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eighth_associate_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    {
     'id'         : 'eighth_associate_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eighth_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
     { 'id'         : 'eighth_associate_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eighth_associate_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eighth_administrator_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    {
     'id'         : 'eighth_administrator_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eighth_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eighth_administrator_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eighth_administrator_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_associate_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    {
     'id'         : 'ninth_associate_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_associate_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_associate_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_administrator_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    {
     'id'         : 'ninth_administrator_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_administrator_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_administrator_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_associate_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    {
     'id'         : 'tenth_associate_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_associate_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_associate_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_administrator_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    {
     'id'         : 'tenth_administrator_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_administrator_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_administrator_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sign'
    , 'description': 'Enseigne'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'signature'
    , 'description': 'Signature'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_associate_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_associate_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_associate_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_associate_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_administrator_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_administrator_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_administrator_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_administrator_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_auditor_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_auditor_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_auditor_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_auditor_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_auditor_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_associate_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_associate_fullname'
    , 'description': 'Nom,Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_administrator_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_administrator_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_administrator_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_administrator_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_auditor_another_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_auditor_firstname'
    , 'description': 'Prénom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_auditor_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_auditor_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_auditor_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'transfer_check'
    , 'description': 'Transfert'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'transferred_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'transferred_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'source_reference'
    , 'description': 'Numero de formalite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
  )

