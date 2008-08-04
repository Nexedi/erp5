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


class M0:
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
    { 'id'         : 'name'
    , 'description': 'title of the organisation of the form'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'head_office_address'
    , 'description': 'Adresse du siège'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'initials'
    , 'description': 'Acronym'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sign'
    , 'description': 'Sign'
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
    { 'id'         : 'activity_check'
    , 'description': 'Activite'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'activity_free_text'
    , 'description': 'Activite'
    , 'type'       : 'string'
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
    { 'id'         : 'inscription_check'
    , 'description': 'Demande d inscription au RCCM'
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
    { 'id'         : 'source_reference'
    , 'description': 'Numero de formalite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'place'
    , 'description': 'Fait �'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'frame'
    , 'description': 'Page Number'
    , 'type'       : 'int'
    , 'mode'       : 'w'
    },
    { 'id'         : 'previous_activity_end_period'
    , 'description': 'Fait �'
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
    , 'description': 'date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_birthplace'
    , 'description': 'lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_extra_info'
    , 'description': 'Date et lieu de naissance,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eight_associate_extra_info'
    , 'description': 'Date et lieu de naissance,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eight_associate_fullname'
    , 'description': 'NOM,PRENOM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eight_manager_extra_info'
    , 'description': 'Date et lieu de naissance,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eight_manager_fullname'
    , 'description': 'NOM et PRENOM.'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eleventh_associate_extra_info'
    , 'description': 'Date et lieu de naissance,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eleventh_associate_fullname'
    , 'description': 'NOM,PRENOM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eleventh_manager_extra_info'
    , 'description': 'Date et lieu de naissance,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eleventh_manager_fullname'
    , 'description': 'NOM, PRENOM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_associate_firstname'
    , 'description': 'Prenom'
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
    { 'id'         : 'fifth_associate_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_associate_firstname'
    , 'description': 'Prenom'
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
    { 'id'         : 'sixth_associate_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_associate_firstname'
    , 'description': 'Prenom'
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
    { 'id'         : 'seventh_associate_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eighth_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eighth_associate_firstname'
    , 'description': 'Prenom'
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
    { 'id'         : 'eighth_associate_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_associate_firstname'
    , 'description': 'Prenom'
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
    { 'id'         : 'ninth_associate_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_associate_firstname'
    , 'description': 'Prenom'
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
    { 'id'         : 'tenth_associate_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eleventh_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eleventh_associate_firstname'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eleventh_associate_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eleventh_associate_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eleventh_associate_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'twelfth_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'twelfth_associate_firstname'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'twelfth_associate_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'twelfth_associate_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'twelfth_associate_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'thirteenth_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'thirteenth_associate_firstname'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'thirteenth_associate_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'thirteenth_associate_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'thirteenth_associate_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourteenth_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourteenth_associate_firstname'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourteenth_associate_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourteenth_associate_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourteenth_associate_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifteenth_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifteenth_associate_firstname'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifteenth_associate_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifteenth_associate_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifteenth_associate_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixteenth_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixteenth_associate_firstname'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixteenth_associate_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixteenth_associate_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixteenth_associate_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventeenth_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventeenth_associate_firstname'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventeenth_associate_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
     { 'id'         : 'seventeenth_associate_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventeenth_associate_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_administrator_firstname'
    , 'description': 'Prenom'
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
    { 'id'         : 'third_administrator_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_administrator_firstname'
    , 'description': 'Prenom'
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
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_administrator_firstname'
    , 'description': 'Prenom'
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
    { 'id'         : 'fifth_administrator_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_administrator_firstname'
    , 'description': 'Prenom'
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
    { 'id'         : 'sixth_administrator_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_administrator_firstname'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_administrator_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_administrator_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_administrator_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eighth_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eighth_administrator_firstname'
    , 'description': 'Prenom'
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
    { 'id'         : 'eighth_administrator_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_administrator_firstname'
    , 'description': 'Prenom'
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
    { 'id'         : 'ninth_administrator_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_administrator_firstname'
    , 'description': 'Prenom'
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
    { 'id'         : 'tenth_administrator_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eleventh_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eleventh_administrator_firstname'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eleventh_administrator_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eleventh_administrator_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eleventh_administrator_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'twelfth_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'twelfth_administrator_firstname'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'twelfth_administrator_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'twelfth_administrator_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'twelfth_administrator_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'thirteenth_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'thirteenth_administrator_firstname'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'thirteenth_administrator_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'thirteenth_administrator_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'thirteenth_administrator_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourteenth_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourteenth_administrator_firstname'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourteenth_administrator_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourteenth_administrator_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourteenth_administrator_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifteenth_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifteenth_administrator_firstname'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifteenth_administrator_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifteenth_administrator_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifteenth_administrator_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixteenth_administrator_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixteenth_administrator_firstname'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixteenth_administrator_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
     { 'id'         : 'sixteenth_administrator_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixteenth_administrator_another_info'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_address'
    , 'description': 'Adresse'
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
    { 'id'         : 'first_administrator_firstname'
    , 'description': 'Prenom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_function'
    , 'description': 'Fonction'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_lastname'
    , 'description': 'NOM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_company_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_manager_extra_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_manager_fullname'
    , 'description': 'Nom,Prenom,Domicile Personnel'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_associate_firstname'
    , 'description': 'Prenoms'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_associate_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
     { 'id'         : 'fourth_associate_birthplace'
    , 'description': 'Date de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_associate_another_info'
    , 'description': 'Autre information'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    }, 
    { 'id'         : 'fourth_manager_fullname'
    , 'description': 'Nom,Prenom,Domicile Personnel'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_manager_extra_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_auditor_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_auditor_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_auditor_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_auditor_firstname'
    , 'description': 'PRENOM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_auditor_lastname'
    , 'description': 'NOM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_associate_extra_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_associate_fullname'
    , 'description': 'Nom,Prenoms,Domicile Personnel'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_manager_extra_info'
    , 'description': 'Date et lieu de naissance,de mariage,regime matrimonial,etc..'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_manager_fullname'
    , 'description': 'Nom,Prenoms,Domicile Personnel'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    }, 
    { 'id'         : 'second_administrator_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    }, 
    { 'id'         : 'second_administrator_firstname'
    , 'description': 'Nom,Prenoms'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_function'
    , 'description': 'Fonction'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_lastname'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_extra_info'
    , 'description': 'Date et lieu de naissance, de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_fullname'
    , 'description': 'Nom,Prenoms,Domicile Personnel'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_birthday'
    , 'description': 'Date et lieu de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_firstname'
    , 'description': 'Prenoms'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_auditor_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_auditor_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_auditor_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_auditor_firstname'
    , 'description': 'Prenoms'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_auditor_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_company_activity'
    , 'description': 'Activite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_company_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_date'
    , 'description': 'Le'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_manager_extra_info'
    , 'description': 'Date et Lieu de naissance,de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_manager_fullname'
    , 'description': 'Nom,Prenoms,Domicile Personnel'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_place'
    , 'description': 'Fait à'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_registration_date'
    , 'description': 'Le'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_registration_number'
    , 'description': 'NUMERO'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_signature'
    , 'description': 'Le'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_associate_extra_info'
    , 'description': 'Date et lieu de naissance, de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_associate_fullname'
    , 'description': 'Nom,Prenoms,Domicile Personenel'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_manager_extra_info'
    , 'description': 'Date et lieu de naissance, de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_manager_fullname'
    , 'description': 'Date et lieu de naissance, de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'signature'
    , 'description': 'Signature'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_associate_extra_info'
    , 'description': 'Date et lieu de naissance, de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_associate_fullname'
    , 'description': 'Nom,Prenoms,Domicile Personenel'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_manager_extra_info'
    , 'description': 'Date et lieu de naissance, de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_manager_fullname'
    , 'description': 'Date et lieu de naissance, de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_associate_extra_info'
    , 'description': 'Date et lieu de naissance, de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_associate_fullname'
    , 'description': 'Nom,Prenoms,Domicile Personenel'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_manager_extra_info'
    , 'description': 'Date et lieu de naissance, de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_manager_fullname'
    , 'description': 'Date et lieu de naissance, de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_associate_extra_info'
    , 'description': 'Date et lieu de naissance, de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_associate_fullname'
    , 'description': 'Nom,Prenoms,Domicile Personenel'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_manager_extra_info'
    , 'description': 'Date et lieu de naissance, de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_manager_fullname'
    , 'description': 'Date et lieu de naissance, de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_associate_address'
    , 'description': 'Adresse'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_associate_birthday'
    , 'description': 'Date de naissance'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
     { 'id'         : 'third_associate_birthplace'
    , 'description': 'Lieu de naissance'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_associate_firstname'
    , 'description': 'Prenoms'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_associate_lastname'
    , 'description': 'Nom'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'm0_bis_activity_free_text'
    , 'description': 'Activite'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'thirteenth_associate_extra_info'
    , 'description': 'Date et lieu de naissance, de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'thirteenth_associate_fullname'
    , 'description': 'Nom,Prenoms,Domicile Personenel'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'thirteenth_manager_extra_info'
    , 'description': 'Date et lieu de naissance, de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'thirteenth_manager_fullname'
    , 'description': 'Date et lieu de naissance, de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'twelfth_associate_extra_info'
    , 'description': 'Date et lieu de naissance, de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'twelfth_associate_fullname'
    , 'description': 'Nom,Prenoms,Domicile Personenel'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'twelfth_manager_extra_info'
    , 'description': 'Date et lieu de naissance, de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'twelfth_manager_fullname'
    , 'description': 'Date et lieu de naissance, de mariage,regime matrimonial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
  )
  _categories = ('function', 'source', 'destination', )
