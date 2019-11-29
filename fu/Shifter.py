"""
==========================================================================
Alu.py
==========================================================================
Simple generic Shifter for CGRA tile.

Author : Cheng Tan
  Date : November 28, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from .opt_type import *
from .Fu       import Fu

class Shifter( Fu ):

  def construct( s, DataType ):

    super( Shifter, s ).construct( DataType )

    @s.update
    def comb_logic():
      if s.recv_opt.msg == OPT_LLS:
        s.send_out.msg = s.recv_in0.msg << s.recv_in1.msg
      elif s.recv_opt.msg == OPT_LRS:
        s.send_out.msg = s.recv_in0.msg >> s.recv_in1.msg

