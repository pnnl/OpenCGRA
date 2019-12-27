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
from ...lib.opt_type    import *
from ..basic.Fu         import Fu

class Logic( Fu ):

  def construct( s, DataType, ConfigType, num_inports, num_outports,
                 data_mem_size ):

    super( Logic, s ).construct( DataType, ConfigType, num_inports, num_outports,
           data_mem_size, [OPT_OR, OPT_AND, OPT_NOT, OPT_XOR] )

    @s.update
    def comb_logic():
      s.send_out[0].msg.predicate = s.recv_in[0].msg.predicate and\
                                    s.recv_in[1].msg.predicate
      if s.recv_opt.msg.ctrl == OPT_OR:
        s.send_out[0].msg.payload = s.recv_in[0].msg.payload | s.recv_in[1].msg.payload
      elif s.recv_opt.msg.ctrl == OPT_AND:
        s.send_out[0].msg.payload = s.recv_in[0].msg.payload & s.recv_in[1].msg.payload
      elif s.recv_opt.msg.ctrl == OPT_NOT:
        s.send_out[0].msg.payload = ~ s.recv_in[0].msg.payload
      elif s.recv_opt.msg.ctrl == OPT_XOR:
        s.send_out[0].msg.payload = s.recv_in[0].msg.payload ^ s.recv_in[1].msg.payload

