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
from ..ifcs.opt_type    import *
from .TwoPrlComb        import TwoPrlComb
from .Mul               import Mul
from .Alu               import Alu

class PrlMulAlu( TwoPrlComb ):

  def construct( s, DataType ):

    super( PrlMulAlu, s ).construct( DataType, Mul, Alu )

