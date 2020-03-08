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
           data_mem_size )

    s.const_one = DataType(1, 1)

    @s.update
    def comb_logic():
      s.send_out[0].msg.predicate = s.recv_in[0].msg.predicate and\
                                    s.recv_in[1].msg.predicate
      for j in range( num_outports ):
        s.send_out[j].en = s.recv_opt.en# and s.send_out[j].rdy and s.recv_in[0].en and s.recv_in[1].en
      if s.recv_opt.msg.ctrl == OPT_ADD:
        s.send_out[0].msg.payload = s.recv_in[0].msg.payload + s.recv_in[1].msg.payload
      elif s.recv_opt.msg.ctrl == OPT_ADD_CONST:
        s.send_out[0].msg.payload = s.recv_in[0].msg.payload + s.recv_const.msg.payload
      elif s.recv_opt.msg.ctrl == OPT_INC:
        s.send_out[0].msg.payload = s.recv_in[0].msg.payload + s.const_one.payload
      elif s.recv_opt.msg.ctrl == OPT_SUB:
        s.send_out[0].msg.payload = s.recv_in[0].msg.payload - s.recv_in[1].msg.payload
      else:
        for j in range( num_outports ):
          s.send_out[j].en = b1( 0 )
      s.send_out[1].msg = s.send_out[0].msg

