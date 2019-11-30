"""
==========================================================================
Logic.py
==========================================================================
Functional Unit of logic compute for CGRA tile.

Author : Cheng Tan
  Date : November 28, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ..ifcs.opt_type    import *
from .Fu                import Fu

class Logic( Fu ):

  def construct( s, DataType ):

    super( Logic, s ).construct( DataType )

    @s.update
    def comb_logic():
      if s.recv_opt.msg == OPT_OR:
        s.send_out.msg = s.recv_in0.msg | s.recv_in1.msg
      elif s.recv_opt.msg == OPT_AND:
        s.send_out.msg = s.recv_in0.msg & s.recv_in1.msg
      elif s.recv_opt.msg == OPT_NOT:
        s.send_out.msg = ~ s.recv_in0.msg
      elif s.recv_opt.msg == OPT_XOR:
        s.send_out.msg = s.recv_in0.msg ^ s.recv_in1.msg

