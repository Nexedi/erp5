##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#          Jean-Paul Smets-Solanes <jp@nexedi.com>
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



class Modele:
  """
    Modele properties and categories
  """

  _properties = (
    { 'id'          : 'accessoires',
      'description' : 'description des accessoires',
      'type'        : 'text',
      'mode'        : 'w' },
    { 'id'          : 'gamme_id',
      'description' : 'la gamme de coloris du modele',
      'type'        : 'string',
      'acquisition_base_category' : ('specialise',),
      'acquisition_portal_type'   : ('Gamme',),
      'acquisition_copy_value'    : 0,
      'acquisition_accessor_id'   : 'getId',
      'acquisition_depends'       : None,
      'mode'        : 'w' },
    { 'id'          : 'forme_id',
      'description' : 'la forme du modËle',
      'type'        : 'string',
      'acquisition_base_category' : ('specialise',),
      'acquisition_portal_type'   : ('Forme',),
      'acquisition_copy_value'    : 0,
      'acquisition_accessor_id'   : 'getId',
      'acquisition_depends'       : None,
      'mode'        : 'w' },
    { 'id'          : 'vetement_id',
      'description' : 'Id des vetements utilises',
      'type'        : 'lines',
      'acquisition_base_category' : ('specialise',),
      'acquisition_portal_type'   : ('Vetement',),
      'acquisition_copy_value'    : 0,
      'acquisition_mask_value'    : 0,
      'acquisition_accessor_id'   : 'getId',
      'acquisition_depends'       : None,
      'mode'        : 'w' },
    { 'id'          : 'commentaires',
      'description' : 'Commentaires',
      'type'        : 'text',
      'mode'        : 'w' },
    { 'id'          : 'composition',
      'description' : 'Composition du modele',
      'type'        : 'text',
      'mode'        : 'w' },
    { 'id'          : 'coef_marge',
      'description' : 'Coefficient de marge',
      'type'        : 'float',
      'mode'        : 'w' },
    { 'id'          : 'coef_majoration',
      'description' : 'Coefficient de majoration de prix',
      'type'        : 'float',
      'mode'        : 'w' },
    { 'id'          : 'cout_additionnel',
      'description' : 'Cout additionnel en euros',
      'type'        : 'float',
      'mode'        : 'w' },
    { 'id'          : 'code_ean13',
      'description' : 'Code EAN 13 du modèle',
      'type'        : 'string',
      'mode'        : 'w' },
    { 'id'          : 'temps_piquage',
      'description' : 'temps de piquage du modèle',
      'type'        : 'float',
      'mode'        : 'w' },
    { 'id'          : 'modele_template',
      'description' : 'Id du modele de reference',
      'type'        : 'string',
      'acquisition_base_category' : ('specialise',),
      'acquisition_portal_type'   : ('Modele',),
      'acquisition_copy_value'    : 0,
      'acquisition_mask_value'    : 0,
      'acquisition_accessor_id'   : 'getId',
      'acquisition_depends'       : None,
      'mode'        : 'w' },
    { 'id'          : 'correspondance_tailles_id',
      'description' : 'Id de la correspondance de tailles utilisee',
      'type'        : 'string',
      'acquisition_base_category' : ('specialise',),
      'acquisition_portal_type'   : ('Correspondance Tailles',),
      'acquisition_copy_value'    : 0,
      'acquisition_mask_value'    : 0,
      'acquisition_accessor_id'   : 'getId',
      'acquisition_depends'       : None,
      'mode'        : 'w' },
    { 'id'          : 'correspondance_mesures_id',
      'description' : 'Id de la correspondance de mesures utilisee',
      'type'        : 'string',
      'acquisition_base_category' : ('specialise',),
      'acquisition_portal_type'   : ('Correspondance Mesures',),
      'acquisition_copy_value'    : 0,
      'acquisition_mask_value'    : 0,
      'acquisition_accessor_id'   : 'getId',
      'acquisition_depends'       : None,
      'mode'        : 'w' },
    { 'id'          : 'nomenclature',
      'description' : 'composants et consommations principaux servant a mettre au point le modele',
      'type'        : 'text',
      'mode'        : 'w' },
    { 'id'          : 'mode_operatoire',
      'description' : 'ensemble de recommandations de montage servant a mettre au point le modele',
      'type'        : 'text',
      'mode'        : 'w' },
  )

  _categories = ( 'eip', 'collection', 'specialise', 'destination', 'taille', 'transformation_state', 'tarif', 'modele_origine', 'marque', 'nomenclature_douane',
'code_entretien' )

  _constraints = (
    { 'id'            : 'forme',
      'description'   : 'There must at most one Forme',
      'type'          : 'CategoryMembershipArity',
      'min_arity'     : '0',
      'max_arity'     : '1',
      'portal_type'   : ('Forme',),
      'base_category' : ('specialise',)
     },
    { 'id'            : 'gamme',
      'description'   : 'There must at most one Gamme',
      'type'          : 'CategoryMembershipArity',
      'min_arity'     : '0',
      'max_arity'     : '1',
      'portal_type'   : ('Gamme',),
      'base_category' : ('specialise',)
     },
  )
