"""
==========================================================================
Branch.py
==========================================================================
Functional unit Branch for CGRA tile.

Author : Cheng Tan
  Date : December [1], 2[0][1]9

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type    import *
from ..basic.Fu         import Fu

class Branch( Fu ):

  def construct( s, DataType, ConfigType, num_inports, num_outports ):

    super( Branch, s ).construct( DataType, ConfigType, num_inports, num_outports,
                                  [OPT_BRH] )

    @s.update
    def comb_logic():
      if s.recv_opt.msg.ctrl == OPT_BRH:
        s.send_out[0].msg.payload = s.recv_in[0].msg.payload
        s.send_out[1].msg.payload = s.recv_in[0].msg.payload
        if s.recv_in[1].msg.payload == Bits16( 0 ):
          s.send_out[0].msg.predicate = Bits1( 1 )
          s.send_out[1].msg.predicate = Bits1( 0 )
        else:
          s.send_out[0].msg.predicate = Bits1( 0 )
          s.send_out[1].msg.predicate = Bits1( 1 )

  def line_trace( s ):
    symbol0 = "?"
    symbol1 = "?"
    winner  = "nobody"
    if s.send_out[0].msg.predicate == Bits1(1):
      symbol0 = "*"
      symbol1 = " "
      winner  = " if "
    elif s.send_out[1].msg.predicate == Bits1(1):
      symbol0 = " "
      symbol1 = "*"
      winner  = "else"
    return f'[{s.send_out[0].msg} {symbol0}] ({winner}) [{s.send_out[1].msg} {symbol1}]'
