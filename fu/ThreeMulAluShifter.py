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
from .opt_type   import *
from .ThreeComb  import ThreeComb
from .Mul        import Mul
from .Alu        import Alu
from .Shifter    import Shifter

class ThreeMulAluShifter( ThreeComb ):

  def construct( s, DataType ):

    super( ThreeMulAluShifter, s ).construct( DataType, Mul, Alu, Shifter )

