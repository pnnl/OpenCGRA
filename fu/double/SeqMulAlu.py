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
from ...lib.opt_type    import *
from ..basic.TwoSeqComb import TwoSeqComb
from ..single.Mul       import Mul
from ..single.Alu       import Alu

class SeqMulAlu( TwoSeqComb ):

  def construct( s, DataType, ConfigType ):

    super( SeqMulAlu, s ).construct( DataType, ConfigType, Mul, Alu )

