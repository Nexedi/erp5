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
    , 'description': 'Head Office RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'activity_free_text'
    , 'description': 'Activities'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'auditor_first_no_check'
    , 'description': 'No'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'auditor_first_yes_check'
    , 'description': 'Yes'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'activities_check'
    , 'description': 'Activities'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'activity_check'
    , 'description': 'Check if there is more activities in a m2 bis sub form'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'added_activities'
    , 'description': 'Activities added'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'added_activities_date'
    , 'description': 'Date'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'auditor_second_no_check'
    , 'description': 'No'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'auditor_second_yes_check'
    , 'description': 'Yes'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'buyers_address'
    , 'description': 'Old Address'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'buyers_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'buyers_name'
    , 'description': 'Buyers'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'default_address_city'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'applicant'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'capital_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'characteristics_check'
    , 'description': 'Characteristics'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'closing_check'
    , 'description': 'Closing'
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
    , 'description': 'Company'
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
    , 'description': 'Activities deleted'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'deleted_activities_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'dissolved_check'
    , 'description': 'dissolve'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'beginning_date'
    , 'description': 'Beginning Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'rccm_check'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'other_check_info'
    , 'description': 'Other'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'other_companies'
    , 'description': 'Second company'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'other_companies_rccm'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'oui_check'
    , 'description': 'Yes'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'purchase_check'
    , 'description': 'Purchase'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'rent_check'
    , 'description': 'Rent'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'report_number'
    , 'description': 'Report Number'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'place'
    , 'description': 'Place'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'registration_number'
    , 'description': 'Registration Number'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_registration_number'
    , 'description': 'Second Registration Number'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eight_administrator_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eight_administrator_fullname'
    , 'description': 'Fullname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_associate_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_associate_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_associate_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_associate_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_associate_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_administrator_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_administrator_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_administrator_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_administrator_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_administrator_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_auditor_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_auditor_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_auditor_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_auditor_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fifth_auditor_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_fullname'
    , 'description': 'Fullname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_lastname'
    , 'description': 'Last Name'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_firstname'
    , 'description': 'first Name'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_birthplace'
    , 'description': 'Going'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_going_check'
    , 'description': 'going'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_maintained_check'
    , 'description': 'Maintained'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_new_check'
    , 'description': 'New'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_new_quality'
    , 'description': 'New quality'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_old_quality'
    , 'description': 'Old quality'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_associate_modified_check'
    , 'description': 'Modified'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_fullname'
    , 'description': 'Fullname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_lastname'
    , 'description': 'Last Name'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_firstname'
    , 'description': 'First Name'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_going_check'
    , 'description': 'going'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_maintained_check'
    , 'description': 'Maintained'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_new_check'
    , 'description': 'New'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_new_quality'
    , 'description': 'New quality'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_old_quality'
    , 'description': 'Old quality'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_administrator_modified_check'
    , 'description': 'Modified'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_rccm_check'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_associate_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_associate_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_associate_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_associate_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_associate_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_administrator_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_administrator_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_administrator_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_administrator_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_administrator_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_auditor_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_auditor_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_auditor_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_auditor_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'fourth_auditor_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'initials'
    , 'description': 'Acronym'
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
    , 'description': 'Activities added'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'modified_deleted_activities'
    , 'description': 'Activities deleted'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'moral_person_check'
    , 'description': 'Personne Morale'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'new_address'
    , 'description': 'Address'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    }, 
    { 'id'         : 'new_capital'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'new_commercial'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'new_headquarters'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'new_legal_form'
    , 'description': 'Legal Form'
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
    , 'description': 'New commercial name'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'old_headquarters'
    , 'description': 'Ancien Siege'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'old_legal_form'
    , 'description': 'Legal Form'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'old_corporate_registration_code'
    , 'description': 'New RCCM'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    }, 
    { 'id'         : 'other'
    , 'description': 'Other'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'other_reason'
    , 'description': 'Other'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'registration_date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_fullname'
    , 'description': 'Fullname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_lastname'
    , 'description': 'Last Name'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_firstname'
    , 'description': 'First Name'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_going_check'
    , 'description': 'going'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_maintained_check'
    , 'description': 'Maintained'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_new_check'
    , 'description': 'New'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_new_quality'
    , 'description': 'New quality'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_old_quality'
    , 'description': 'Old quality'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_associate_modified_check'
    , 'description': 'Modified'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_fullname'
    , 'description': 'Fullname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_lastname'
    , 'description': 'Last Name'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_firstname'
    , 'description': 'First Name'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_going_check'
    , 'description': 'going'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_maintained_check'
    , 'description': 'Maintained'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_new_check'
    , 'description': 'New'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_new_quality'
    , 'description': 'New quality'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_old_quality'
    , 'description': 'Old quality'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_administrator_modified_check'
    , 'description': 'Modified'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_rccm_check'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_place'
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
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    {
     'id'         : 'seventh_associate_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_associate_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
     { 'id'         : 'seventh_associate_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_associate_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_administrator_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    {
     'id'         : 'seventh_administrator_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_administrator_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_administrator_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_administrator_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_auditor_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    {
     'id'         : 'seventh_auditor_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_auditor_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_auditor_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'seventh_auditor_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eighth_associate_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    {
     'id'         : 'eighth_associate_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eighth_associate_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
     { 'id'         : 'eighth_associate_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eighth_associate_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eighth_administrator_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    {
     'id'         : 'eighth_administrator_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eighth_administrator_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eighth_administrator_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'eighth_administrator_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_associate_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    {
     'id'         : 'ninth_associate_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_associate_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_associate_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_associate_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_administrator_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    {
     'id'         : 'ninth_administrator_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_administrator_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_administrator_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'ninth_administrator_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_associate_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    {
     'id'         : 'tenth_associate_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_associate_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_associate_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_associate_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_administrator_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    {
     'id'         : 'tenth_administrator_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_administrator_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_administrator_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'tenth_administrator_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sign'
    , 'description': 'Sign'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'signature'
    , 'description': 'Signature'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_associate_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_associate_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_associate_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_associate_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_associate_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_administrator_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_administrator_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_administrator_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_administrator_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_administrator_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_auditor_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_auditor_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_auditor_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_auditor_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'sixth_auditor_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_associate_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_associate_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_associate_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_associate_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_associate_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    
    
    { 'id'         : 'third_administrator_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_administrator_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_administrator_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_administrator_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_administrator_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_auditor_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_auditor_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_auditor_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_auditor_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'third_auditor_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_auditor_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_auditor_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_auditor_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_auditor_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_auditor_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_auditor_another_info'
    , 'description': 'Other Info'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_auditor_firstname'
    , 'description': 'Firstname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_auditor_lastname'
    , 'description': 'Lastname'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_auditor_birthday'
    , 'description': 'Birthday'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'second_auditor_birthplace'
    , 'description': 'Birthplace'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'transfer_check'
    , 'description': 'Transfer'
    , 'type'       : 'boolean'
    , 'mode'       : 'w'
    },
    { 'id'         : 'transferred_address'
    , 'description': 'Address'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'transferred_date'
    , 'description': 'Date'
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'source_reference'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
  )

