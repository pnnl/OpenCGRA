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

OPT_START = Bits5( 0  )
OPT_NAH   = Bits5( 1  )
OPT_ADD   = Bits5( 2  )
OPT_ADD_CONST = Bits5( 25 )
OPT_INC   = Bits5( 3  )
OPT_SUB   = Bits5( 4  )
OPT_LLS   = Bits5( 5  )
OPT_LRS   = Bits5( 6  )
OPT_MUL   = Bits5( 7  )
OPT_DIV   = Bits5( 26  )
OPT_OR    = Bits5( 8  )
OPT_XOR   = Bits5( 9  )
OPT_AND   = Bits5( 10 )
OPT_NOT   = Bits5( 11 )
OPT_LD    = Bits5( 12 )
OPT_STR   = Bits5( 13 )
OPT_EQ    = Bits5( 14 )
OPT_LE    = Bits5( 15 )
OPT_BRH   = Bits5( 16 )
OPT_PHI   = Bits5( 17 )
OPT_SEL   = Bits5( 27 )
OPT_LD_CONST = Bits5( 28 )
OPT_MUL_ADD = Bits5( 18 )
OPT_MUL_SUB = Bits5( 19 )
OPT_MUL_LLS = Bits5( 20 )
OPT_MUL_LRS = Bits5( 21 )
OPT_MUL_ADD_LLS = Bits5( 22 )
OPT_MUL_SUB_LLS = Bits5( 23 )
OPT_MUL_SUB_LRS = Bits5( 24 )

OPT_SYMBOL_DICT = {
  OPT_START : "(start)",
  OPT_NAH   : "( )",
  OPT_ADD   : "(+)",
  OPT_ADD_CONST : "(+')",
  OPT_INC   : "(++)",
  OPT_SUB   : "(-)",
  OPT_LLS   : "(<<)",
  OPT_LRS   : "(>>)",
  OPT_MUL   : "(x)",
  OPT_DIV   : "(/)",
  OPT_OR    : "(|)",
  OPT_XOR   : "(^)",
  OPT_AND   : "(&)",
  OPT_NOT   : "(~)",
  OPT_LD    : "(ld)",
  OPT_STR   : "(st)",
  OPT_EQ    : "(?=)",
  OPT_LE    : "(?<)",
  OPT_BRH   : "(br)",
  OPT_PHI   : "(ph)",
  OPT_SEL   : "(sel)",
  OPT_LD_CONST : "(ldcst)",
  OPT_MUL_ADD : "(x +)",
  OPT_MUL_SUB : "(x -)",
  OPT_MUL_LLS : "(x <<)",
  OPT_MUL_LRS : "(x >>)",
  OPT_MUL_ADD_LLS : "(x + <<)",
  OPT_MUL_SUB_LLS : "(x + <<)",
  OPT_MUL_SUB_LRS : "(x - >>)"

}
