##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#          Fabien Morin <fabien@nexedi.com>
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

class DefaultAnnotationLine:
  """
  Generate automatic accessors to manage a default AnnotationLine on a object.
  """

  _properties = (
    # Acquisition
    { 'id'          : 'work_time_annotation_line',
      'storage_id'  : 'work_time_annotation_line',
      'description' : 'The duration of worked time',
      'type'        : 'content',
      'portal_type' : ('Annotation Line',),
      'acquired_property_id'      : ('source_section', 'source_section_title',
                                     'source_section_uid', 
                                     'destination_section',
                                     'destination_section_uid',
                                     'destination_section_title',
                                     'resource_uid',
                                     'resource_title', 'quantity', 
                                     'quantity_unit', 'quantity_unit_title'),
      'mode'        : 'w' },
    { 'id'          : 'overtime_annotation_line',
      'storage_id'  : 'overtime_annotation_line',
      'description' : 'The duration of overtime worked hours',
      'type'        : 'content',
      'portal_type' : ('Annotation Line',),
      'acquired_property_id'      : ('source_section', 'source_section_title',
                                     'source_section_uid', 
                                     'destination_section',
                                     'destination_section_uid',
                                     'destination_section_title',
                                     'resource_uid',
                                     'resource_title', 'quantity', 
                                     'quantity_unit', 'quantity_unit_title'),
      'mode'        : 'w' },
    { 'id'          : 'social_insurance_annotation_line',
      'storage_id'  : 'social_insurance_annotation_line',
      'description' : "The Social Insurance annotation line, it's used to"
                      " display information on Social Insurance",
      'type'        : 'content',
      'portal_type' : ('Annotation Line',),
      'acquired_property_id'      : ('source', 'source_title',
                                     'source_uid', 
                                     'destination',
                                     'destination_uid',
                                     'destination_title',
                                     'resource_uid',
                                     'resource_title', 'quantity', 
                                     'quantity_unit', 'quantity_unit_title'),
      'mode'        : 'w' },
   )
