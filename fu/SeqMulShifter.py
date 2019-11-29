"""
==========================================================================
SeqMulShifter.py
==========================================================================
Mul followed by Shifter in sequential for CGRA tile.

Author : Cheng Tan
  Date : November 28, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from .opt_type   import *
from .TwoSeqComb import TwoSeqComb
from .Mul        import Mul
from .Shifter    import Shifter

class SeqMulShifter( TwoSeqComb ):

  def construct( s, DataType ):

    super( SeqMulShifter, s ).construct( DataType, Mul, Shifter )

