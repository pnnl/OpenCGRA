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

    @s.update
    def comb_logic():
      for j in range( num_outports ):
        s.send_out[j].en = s.recv_opt.en and s.send_out[j].rdy and s.recv_in[0].en
      if s.recv_opt.msg.ctrl == OPT_PHI:
        if s.recv_in[0].msg.predicate == Bits1( 1 ):
          s.send_out[0].msg = s.recv_in[0].msg
        elif s.recv_in[1].msg.predicate == Bits1( 1 ):
          s.send_out[0].msg = s.recv_in[1].msg
        else:
          s.send_out[0].msg = s.recv_in[0].msg
          s.send_out[0].msg.predicate = Bits1( 1 )
      else:
        for j in range( num_outports ):
          s.send_out[j].en = b1( 0 )

  def line_trace( s ):
    symbol0 = "#"
    symbol1 = "#"
    if s.recv_in[0].msg.predicate == Bits1(1):
      symbol0 = "*"
      symbol1 = " "
    elif s.recv_in[1].msg.predicate == Bits1(1):
      symbol0 = " "
      symbol1 = "*"
    return f'[{s.recv_in[0].msg} {symbol0}] [{s.recv_in[1].msg} {symbol1}] = [{s.send_out[0].msg}]'
