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

    FuInType = mk_bits( clog2( num_inports + 1 ) )

    @s.update
    def comb_logic():

      # For pick input register
      in0 = FuInType( 0 )
      in1 = FuInType( 0 )
      for i in range( num_inports ):
        s.recv_in[i].rdy = b1( 0 )
      if s.recv_opt.en and s.recv_opt.msg.fu_in[0] != FuInType( 0 ) and s.recv_opt.msg.fu_in[1] != FuInType( 0 ):
        in0 = s.recv_opt.msg.fu_in[0] - FuInType( 1 )
        in1 = s.recv_opt.msg.fu_in[1] - FuInType( 1 )
        s.recv_in[in0].rdy = b1( 1 )
        s.recv_in[in1].rdy = b1( 1 )

      s.send_out[0].msg.predicate = s.recv_in[in0].msg.predicate and\
                                    s.recv_in[in1].msg.predicate
      for j in range( num_outports ):
        s.send_out[j].en = s.recv_opt.en# and s.send_out[j].rdy and s.recv_in[0].en and s.recv_in[1].en
      if s.recv_opt.msg.ctrl == OPT_MUL:
        s.send_out[0].msg.payload = s.recv_in[in0].msg.payload * s.recv_in[in1].msg.payload
      elif s.recv_opt.msg.ctrl == OPT_MUL_CONST:
        s.send_out[0].msg.payload = s.recv_in[in0].msg.payload * s.recv_const.msg.payload
        s.send_out[0].msg.predicate = s.recv_in[in0].msg.predicate
      elif s.recv_opt.msg.ctrl == OPT_DIV:
        s.send_out[0].msg.payload = s.recv_in[in0].msg.payload / s.recv_in[in1].msg.payload

      else:
        for j in range( num_outports ):
          s.send_out[j].en = b1( 0 )
#      print("see const in MUL: ", s.recv_in[0].msg.payload, " x ", s.recv_const.msg.payload, "; out: ", s.send_out[0].msg, "; en: ", s.send_out[0].en, "; ", s)
      #s.send_out[1].msg = s.send_out[0].msg
