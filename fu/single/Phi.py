"""
==========================================================================
Phi.py
==========================================================================
Functional unit Phi for CGRA tile.

Author : Cheng Tan
  Date : November 30, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type    import *
from ..basic.Fu         import Fu

class Phi( Fu ):

  def construct( s, DataType, ConfigType, num_inports, num_outports,
                 data_mem_size ):

    super( Phi, s ).construct( DataType, ConfigType, num_inports, num_outports,
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

      for j in range( num_outports ):
        s.send_out[j].en = s.recv_opt.en# and s.send_out[j].rdy and s.recv_in[0].en
#      s.send_out[0].en = s.recv_opt.en

      if s.recv_opt.msg.ctrl == OPT_PHI:
        if s.recv_in[in0].msg.predicate == Bits1( 1 ):
          s.send_out[0].msg.payload   = s.recv_in[in0].msg.payload
          s.send_out[0].msg.predicate = Bits1( 1 )
        elif s.recv_in[in1].msg.predicate == Bits1( 1 ):
          s.send_out[0].msg.payload   = s.recv_in[in1].msg.payload
          s.send_out[0].msg.predicate = Bits1( 1 )
        else:
          s.send_out[0].msg.payload   = s.recv_in[in0].msg.payload
          s.send_out[0].msg.predicate = Bits1( 1 )

      elif s.recv_opt.msg.ctrl == OPT_PHI_CONST:
        if s.recv_in[in0].msg.predicate == Bits1( 1 ):
          s.send_out[0].msg.payload   = s.recv_in[in0].msg.payload
          s.send_out[0].msg.predicate = Bits1( 1 )
        else:
          s.send_out[0].msg.payload   = s.recv_const.msg.payload
          s.send_out[0].msg.predicate = Bits1( 1 )

      else:
        for j in range( num_outports ):
          s.send_out[j].en = b1( 0 )

      # FIXME: This is used for walk around.
      #        When a value comes earlier but need to be computed later,
      #        it should be stored inside reg2 or reg3, and then go into
      #        reg0 or reg1 at the next cycle for computation.
      # TODO:  But an ideal solution is to make these FU take arbitory
      #        input regs (say, reg1&reg3 or reg0&reg2) for computation,
      #        which requires another dimension in our control signals.
      #        And prevent the from consuming the value in the 'holding'
      #        reg.
#      for j in range( 1, num_outports ):
#        if j+1 < num_inports:
#          s.send_out[j].msg = s.recv_in[j+1].msg

  def line_trace( s ):
#    symbol0 = "#"
#    symbol1 = "#"
#    if s.recv_in[0].msg.predicate == Bits1(1):
#      symbol0 = "*"
#      symbol1 = " "
#    elif s.recv_in[1].msg.predicate == Bits1(1):
#      symbol0 = " "
#      symbol1 = "*"
#    return f'[{s.recv_in[0].msg} {symbol0}] [{s.recv_in[1].msg} {symbol1}] = [{s.send_out[0].msg}]'
    opt_str = " #"
#    if s.send_out[0].en:
#      opt_str = OPT_SYMBOL_DICT[s.recv_opt.msg.ctrl]
#    return f'[{s.recv_in[0].msg}] {opt_str} [{s.recv_in[1].msg} ({s.recv_const.msg}) ] = [{s.send_out[0].msg}]'
    if s.recv_opt.en:
      opt_str = OPT_SYMBOL_DICT[s.recv_opt.msg.ctrl]
    out_str = ",".join([str(x.msg) for x in s.send_out])
    recv_str = ",".join([str(x.msg) for x in s.recv_in])
    return f'[recv: {recv_str}] {opt_str} (const: {s.recv_const.msg}) ] = [out: {out_str}] (s.recv_opt.rdy: {s.recv_opt.rdy}, {OPT_SYMBOL_DICT[s.recv_opt.msg.ctrl]}, send[0].en: {s.send_out[0].en}) '
