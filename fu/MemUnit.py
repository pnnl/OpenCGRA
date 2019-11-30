"""
==========================================================================
MemUnit.py
==========================================================================
Mem access unit for CGRA tile.

Author : Cheng Tan
  Date : November 29, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ..ifcs.opt_type    import *
from .Fu                import Fu

class MemUnit( Fu ):

  def construct( s, DataType ):

    super( MemUnit, s ).construct( DataType )

    @s.update
    def comb_logic():
      if s.recv_opt.msg == OPT_LD:
        # address
        s.send_out.msg = s.recv_in0.msg
      elif s.recv_opt.msg == OPT_STR:
        s.send_out.msg = s.recv_in0.msg - s.recv_in1.msg

