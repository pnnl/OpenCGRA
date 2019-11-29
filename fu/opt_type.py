#=========================================================================
# opt_type.py
#=========================================================================
# Operation types for all functional units.
#
# Author : Cheng Tan
#   Date : Nov 27, 2019

#-------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------

from pymtl3 import *

OPT_NAH     = Bits16( 0 ) 
OPT_ADD     = Bits16( 1 )
OPT_SUB     = Bits16( 2 )
OPT_LLS     = Bits16( 3 )
OPT_LRS     = Bits16( 4 )
OPT_MUL     = Bits16( 5 )
OPT_MUL_ADD = Bits16( 6 )
OPT_MUL_SUB = Bits16( 7 )
OPT_MUL_LLS = Bits16( 8 )
OPT_MUL_LRS = Bits16( 9 )

OPT_SYMBOL_DICT = {
  OPT_NAH: "?",
  OPT_ADD: "+",
  OPT_SUB: "-",
  OPT_LLS: "<",
  OPT_LRS: ">",
  OPT_MUL: "x"
}
