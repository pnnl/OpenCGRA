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

    FuInType = mk_bits( clog2( num_inports + 1 ) )

    @s.update
    def comb_logic():

      # For pick input register
      in0 = FuInType( 0 )
      in1 = FuInType( 0 )
      if s.recv_opt.en:
        in0 = s.recv_opt.msg.fu_in[0] - FuInType( 1 )
        in1 = s.recv_opt.msg.fu_in[1] - FuInType( 1 )
        print("alu see: ", in0, in1, num_inports, s.recv_opt.msg)
        s.recv_in[in0].rdy = b1( 1 )
        s.recv_in[in1].rdy = b1( 1 )

      s.send_out[0].msg.predicate = s.recv_in[in0].msg.predicate and\
                                    s.recv_in[in1].msg.predicate
      for j in range( num_outports ):
        s.send_out[j].en = s.recv_opt.en# and s.send_out[j].rdy and s.recv_in[0].en and s.recv_in[1].en
      if s.recv_opt.msg.ctrl == OPT_ADD:
        s.send_out[0].msg.payload = s.recv_in[in0].msg.payload + s.recv_in[in1].msg.payload
#        print("in adder: s.in1: ", s.recv_in[0].msg, "; in2: ", s.recv_in[1].msg, "; out: ", s.send_out[0].msg, "; s.recv_opt.en: ", s.recv_opt.en, "; send[0].en: ", s.send_out[0].en)
      elif s.recv_opt.msg.ctrl == OPT_ADD_CONST:
        s.send_out[0].msg.payload = s.recv_in[in0].msg.payload + s.recv_const.msg.payload
        s.send_out[0].msg.predicate = s.recv_in[in0].msg.predicate
      elif s.recv_opt.msg.ctrl == OPT_INC:
        s.send_out[0].msg.payload = s.recv_in[in0].msg.payload + s.const_one.payload
      elif s.recv_opt.msg.ctrl == OPT_SUB:
        s.send_out[0].msg.payload = s.recv_in[in0].msg.payload - s.recv_in[in1].msg.payload
      elif s.recv_opt.msg.ctrl == OPT_PAS:
        s.send_out[0].msg.payload = s.recv_in[in0].msg.payload
        s.send_out[0].msg.predicate = s.recv_in[in0].msg.predicate
      else:
        for j in range( num_outports ):
          s.send_out[j].en = b1( 0 )
      #s.send_out[1].msg = s.send_out[0].msg

