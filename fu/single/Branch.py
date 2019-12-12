"""
==========================================================================
Branch.py
==========================================================================
Functional unit Branch for CGRA tile.

Author : Cheng Tan
  Date : December 1, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type    import *

class Branch( Component ):

  def construct( s, DataType, ConfigType ):

    # Interface

    s.recv_data      = RecvIfcRTL( DataType )
    s.recv_comp      = RecvIfcRTL( Bits1    )
    s.send_if        = SendIfcRTL( DataType )
    s.send_else      = SendIfcRTL( DataType )

    @s.update
    def update_signal():
      s.recv_data.rdy = s.send_if.rdy  and s.send_else.rdy 
      s.recv_comp.rdy = s.send_if.rdy  and s.send_else.rdy
      s.send_if.en    = s.recv_data.en and s.recv_comp.en
      s.send_else.en  = s.recv_data.en and s.recv_comp.en

    @s.update
    def comb_logic():
      s.send_if.msg.payload    = s.recv_data.msg.payload
      s.send_else.msg.payload  = s.recv_data.msg.payload
      if s.recv_comp.msg == Bits1( 1 ):
        s.send_if.msg.predicate   = Bits1( 1 )
        s.send_else.msg.predicate = Bits1( 0 )
      else:
        s.send_if.msg.predicate   = Bits1( 0 )
        s.send_else.msg.predicate = Bits1( 1 )

  def line_trace( s ):
    symbol0 = "?"
    symbol1 = "?"
    winner  = "nobody"
    if s.send_if.msg.predicate == Bits1(1):
      symbol0 = "*"
      symbol1 = " "
      winner  = " if "
    elif s.send_else.msg.predicate == Bits1(1):
      symbol0 = " "
      symbol1 = "*"
      winner  = "else"
    return f'[{s.send_if.msg} {symbol0}] ({winner}) [{s.send_else.msg} {symbol1}]'
