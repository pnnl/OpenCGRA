"""
==========================================================================
SeqMulShifter.py
==========================================================================
Mul followed by Shifter in sequential for CGRA tile.

Author : Cheng Tan
  Date : November 28, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs  import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type     import *
from ..basic.TwoSeqCombo import TwoSeqCombo
from ..single.Mul        import Mul
from ..single.Shifter    import Shifter

class SeqMulShifter( TwoSeqCombo ):

  def construct( s, DataType, ConfigType ):

    super( SeqMulShifter, s ).construct( DataType, ConfigType, Mul, Shifter )

