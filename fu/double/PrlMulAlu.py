"""
==========================================================================
PrlMulAlu.py
==========================================================================
Mul and ALU in parallel for CGRA tile.

Author : Cheng Tan
  Date : November 28, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type    import *
from ..basic.TwoPrlComb import TwoPrlComb
from ..single.Mul       import Mul
from ..single.Alu       import Alu

class PrlMulAlu( TwoPrlComb ):

  def construct( s, DataType, ConfigType ):

    super( PrlMulAlu, s ).construct( DataType, ConfigType, Mul, Alu )

