##############################################################################
#
# Copyright (c) 2008 Nexedi SARL and Contributors. All Rights Reserved.
#                     Thibaut Deheunynck <thibaut@nexedi.com>
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



class PsjImportOrganisation:
  """
    Organisation properties and categories
  """

  _properties = (
      {'id'         : 'import_nreg',
       'type'       : 'string',
       'mode'       : 'w',
      },
      {'id'         : 'import_rs',
       'type'       : 'string',
       'mode'       : 'w'
      },
      {'id'         : 'import_act',
      'type'        : 'string',
      'mode'        : 'w'
      },
      {'id'         : 'import_form',
      'type'        : 'string',
      'mode'        : 'w'
      },
      {'id'         : 'import_codeform',
      'type'        : 'string',
      'mode'        : 'w'
      },
      {'id'         : 'import_ohada',
      'type'        : 'string',
      'mode'        : 'w' 
      },
      {'id'         : 'import_adr',
      'type'        : 'string',
      'mode'        : 'w'
      },
      {'id'         : 'import_enscom',
      'type'        : 'string',
      'mode'        : 'w'
      },
      {'id'         : 'import_capital',
      'type'        : 'string',
      'mode'        : 'w'
      },
      {'id'         : 'import_cjud',
      'type'        : 'string',
      'mode'        : 'w'
      },
      {'id'         : 'import_stat',
      'type'        : 'string',
      'mode'        : 'w'
      },
      {'id'         : 'import_sousc',
      'type'        : 'string',
      'mode'        : 'w'
      },
      {'id'         : 'import_lst',
      'type'        : 'string',
      'mode'        : 'w'
      },
      {'id'         : 'import_detb',
      'type'        : 'string',
      'mode'        : 'w'
      },
      {'id'         : 'import_codactp',
      'type'        : 'string',
      'mode'        : 'w'
      },
      {'id'         : 'import_codacts',
      'type'        : 'string',
      'mode'        : 'w'
      },
      {'id'         : 'import_codloc',
      'type'        : 'string',
      'mode'        : 'w'
      },
      {'id'         : 'import_duree',
      'type'        : 'string',
      'mode'        : 'w'
      },

      {'id'        : 'import_pnom',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_nom',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_dnai',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_codlnaiss',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_lnai',
      'type'       :  'string',
      'mode'       : 'w'
      },

      {'id'        : 'import_administ',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_dnaiadm',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_lnaiadm',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_adradm',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_codnatadm',
      'type'       :  'string',
      'mode'       : 'w'
      },

      {'id'        : 'import_secretgen',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_dnaisecret',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_lnaisecret',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_adrsecret',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_codnatsecr',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_gerant',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_dnaigr',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_lnaigr',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_adrgr',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_codnatgr',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_cogerant',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_dnaicogr',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_lnaicogr',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_adrcogr',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_codnatcogr',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_president',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_dnaipr',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_lnaipr',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_adrpr',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_codnatpr',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_directeur',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_dnaidg',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_lnaidg',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_adrdg',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_codnatdg',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_pcadm',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_dnaipcadm',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_lnaipcadm',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_adrpcadm',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_codnapcadm',
      'type'       :  'string',
      'mode'       : 'w'
      },

      {'id'        : 'import_numjugmt',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'        : 'import_dateaudien',
      'type'       :  'string',
      'mode'       : 'w'
      },
      {'id'         : 'import_codebatim',
      'type'        : 'string',
      'mode'        : 'w'
      },
      {'id'         : 'import_codesalle',
      'type'        : 'string',
      'mode'        : 'w'
      },
      {'id'         : 'import_coderayonn',
      'type'        : 'string',
      'mode'        : 'w'
      },
      {'id'         : 'import_coderayon',
      'type'        : 'string',
      'mode'        : 'w'
      },
      {'id'         : 'import_codetagere',
      'type'        : 'string',
      'mode'        : 'w'
      },
      )