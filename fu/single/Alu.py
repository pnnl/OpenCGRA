"""
==========================================================================
Alu.py
==========================================================================
Simple generic ALU for CGRA tile.

Author : Cheng Tan
  Date : November 27, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ..ifcs.opt_type    import *
from .Fu                import Fu

class Alu( Fu ):

  def construct( s, DataType ):

    super( Alu, s ).construct( DataType )

    @s.update
    def comb_logic():
      if s.recv_opt.msg == OPT_ADD:
        s.send_out.msg = s.recv_in0.msg + s.recv_in1.msg
      elif s.recv_opt.msg == OPT_SUB:
        s.send_out.msg = s.recv_in0.msg - s.recv_in1.msg

