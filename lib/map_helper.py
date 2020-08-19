"""
==========================================================================
map_helper.py
==========================================================================
Helper map and functions to get corresponding functional unit and ctrl.

Author : Cheng Tan
  Date : Feb 22, 2020

"""

from .opt_type           import *
from ..fu.single.Alu     import Alu
from ..fu.single.Shifter import Shifter
from ..fu.single.Logic   import Logic
from ..fu.single.Mul     import Mul
from ..fu.single.MemUnit import MemUnit
from ..fu.single.Comp    import Comp
from ..fu.single.Phi     import Phi
from ..fu.single.Branch  import Branch

# -----------------------------------------------------------------------
# Global dictionary for UnitType and OptType
# -----------------------------------------------------------------------

unit_map = { "Alu"             : Alu,
             "Mul"             : Mul,
             "Phi"             : Phi,
             "Comp"            : Comp,
             "Branch"          : Branch,
             "Logic"           : Logic,
             "Shifter"         : Shifter,
             "MemUnit"         : MemUnit }

opt_map  = { "OPT_START"       : OPT_START,
             "OPT_NAH"         : OPT_NAH,
             "OPT_ADD"         : OPT_ADD,
             "OPT_ADD_CONST"   : OPT_ADD_CONST,
             "OPT_INC"         : OPT_INC,
             "OPT_SUB"         : OPT_SUB,
             "OPT_LLS"         : OPT_LLS,
             "OPT_LRS"         : OPT_LRS,
             "OPT_MUL"         : OPT_MUL,
             "OPT_OR"          : OPT_OR,
             "OPT_XOR"         : OPT_XOR,
             "OPT_AND"         : OPT_AND,
             "OPT_NOT"         : OPT_NOT,
             "OPT_LD"          : OPT_LD,
             "OPT_STR"         : OPT_STR,
             "OPT_EQ"          : OPT_EQ,
             "OPT_LE"          : OPT_LE,
             "OPT_BRH"         : OPT_BRH,
             "OPT_PHI"         : OPT_PHI,
             "OPT_PHI_CONST"   : OPT_PHI_CONST,
             "OPT_MUL_ADD"     : OPT_MUL_ADD,
             "OPT_MUL_SUB"     : OPT_MUL_SUB,
             "OPT_MUL_LLS"     : OPT_MUL_LLS,
             "OPT_MUL_LRS"     : OPT_MUL_LRS,
             "OPT_MUL_ADD_LLS" : OPT_MUL_ADD_LLS,
             "OPT_MUL_SUB_LLS" : OPT_MUL_SUB_LLS,
             "OPT_MUL_SUB_LRS" : OPT_MUL_SUB_LRS }


def getUnitType( fu_name ):
  return unit_map[ fu_name ]

def getOptType( opt_name ):
  return opt_map[ opt_name ]

