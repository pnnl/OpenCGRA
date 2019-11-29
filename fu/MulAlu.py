"""
==========================================================================
MulAlu.py
==========================================================================
Simple generic Mul followed by ALU for CGRA tile.

Author : Cheng Tan
  Date : November 28, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from .opt_type   import *
from .TwoSeqComb import TwoSeqComb
from .Mul        import Mul
from .Alu        import Alu

class MulAlu( TwoSeqComb ):

  def construct( s, DataType ):

    super( MulAlu, s ).construct( DataType, Mul, Alu )

