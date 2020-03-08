"""
==========================================================================
Mul.py
==========================================================================
Muliplier for CGRA tile.

Author : Cheng Tan
  Date : November 28, 2019
"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type    import *
from ..basic.Fu         import Fu

class Mul( Fu ):

  def construct( s, DataType, ConfigType, num_inports, num_outports,
                 data_mem_size ):

    super( Mul, s ).construct( DataType, ConfigType, num_inports, num_outports,
           data_mem_size )

    @s.update
    def comb_logic():
      s.send_out[0].msg.predicate = s.recv_in[0].msg.predicate and\
                                 s.recv_in[1].msg.predicate
      for j in range( num_outports ):
        s.send_out[j].en = s.recv_opt.en# and s.send_out[j].rdy and s.recv_in[0].en and s.recv_in[1].en
      if s.recv_opt.msg.ctrl == OPT_MUL:
        s.send_out[0].msg.payload = s.recv_in[0].msg.payload * s.recv_in[1].msg.payload
      else:
        for j in range( num_outports ):
          s.send_out[j].en = b1( 0 )
      s.send_out[1].msg = s.send_out[0].msg
