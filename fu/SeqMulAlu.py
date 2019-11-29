"""
==========================================================================
SeqMulAlu.py
==========================================================================
Mul followed by ALU in sequential for CGRA tile.

Author : Cheng Tan
  Date : November 28, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from .opt_type   import *
from .TwoSeqComb import TwoSeqComb
from .Mul        import Mul
from .Alu        import Alu

class SeqMulAlu( TwoSeqComb ):

  def construct( s, DataType ):

    super( SeqMulAlu, s ).construct( DataType, Mul, Alu )

