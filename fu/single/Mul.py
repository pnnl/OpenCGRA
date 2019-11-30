"""
==========================================================================
Mul.py
==========================================================================
Simple generic Muliplier for CGRA tile.
Author : Cheng Tan
  Date : November 28, 2019
"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ..ifcs.opt_type    import *
from .Fu                import Fu

class Mul( Fu ):

  def construct( s, DataType ):

    super( Mul, s ).construct( DataType )

    @s.update
    def comb_logic():
      if s.recv_opt.msg == OPT_MUL:
        s.send_out.msg = s.recv_in0.msg * s.recv_in1.msg

