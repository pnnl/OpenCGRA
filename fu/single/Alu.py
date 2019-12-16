"""
==========================================================================
Alu.py
==========================================================================
ALU for CGRA tile.

Author : Cheng Tan
  Date : November 27, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type    import *
from ..basic.Fu         import Fu

class Alu( Fu ):

  def construct( s, DataType, ConfigType ):

    super( Alu, s ).construct( DataType, ConfigType )

    @s.update
    def comb_logic():
      s.send_out0.msg.predicate = s.recv_in0.msg.predicate and s.recv_in1.msg.predicate
      if s.recv_opt.msg.ctrl == OPT_ADD:
        s.send_out0.msg.payload = s.recv_in0.msg.payload + s.recv_in1.msg.payload
      elif s.recv_opt.msg.ctrl == OPT_INC:
        s.send_out0.msg.payload = s.recv_in0.msg.payload + Bits32( 1 )
      elif s.recv_opt.msg.ctrl == OPT_SUB:
        s.send_out0.msg.payload = s.recv_in0.msg.payload - s.recv_in1.msg.payload
      s.send_out1.msg = s.send_out0.msg

