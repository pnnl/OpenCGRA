"""
==========================================================================
ThreeMulShifter.py
==========================================================================
Mul and ALU in parallel for CGRA tile.

Author : Cheng Tan
  Date : November 28, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type    import *
from ..basic.ThreeCombo import ThreeCombo
from ..single.Mul       import Mul
from ..single.Alu       import Alu
from ..single.Shifter   import Shifter

class ThreeMulAluShifter( ThreeCombo ):

  def construct( s, DataType, ConfigType ):

    super( ThreeMulAluShifter, s ).construct( DataType, ConfigType, Mul, Alu, Shifter )

