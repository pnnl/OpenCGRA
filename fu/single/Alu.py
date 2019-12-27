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

  def construct( s, DataType, ConfigType, num_inports, num_outports,
                 data_mem_size ):

    super( Alu, s ).construct( DataType, ConfigType, num_inports, num_outports,
           data_mem_size, [OPT_ADD, OPT_INC, OPT_SUB] )

    @s.update
    def comb_logic():
      s.send_out[0].msg.predicate = s.recv_in[0].msg.predicate and\
                                    s.recv_in[1].msg.predicate
      if s.recv_opt.msg.ctrl == OPT_ADD:
        s.send_out[0].msg.payload = s.recv_in[0].msg.payload + s.recv_in[1].msg.payload
      elif s.recv_opt.msg.ctrl == OPT_INC:
        s.send_out[0].msg.payload = s.recv_in[0].msg.payload + DataType( 1, 1 ).payload
      elif s.recv_opt.msg.ctrl == OPT_SUB:
        s.send_out[0].msg.payload = s.recv_in[0].msg.payload - s.recv_in[1].msg.payload
      s.send_out[1].msg = s.send_out[0].msg

