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

class Phi( Component ):

  def construct( s, DataType ):

    # Interface

    s.recv_in0 = RecvIfcRTL( DataType   )
    s.recv_in1 = RecvIfcRTL( DataType   )
    s.send_out = SendIfcRTL( DataType   )

    @s.update
    def update_signal():
      s.recv_in0.rdy = s.send_out.rdy
      s.recv_in1.rdy = s.send_out.rdy
      s.send_out.en  = s.recv_in0.en and s.recv_in1.en

    @s.update
    def comb_logic():
      assert( not (s.recv_in0.msg.predicate==Bits1(1) and\
                   s.recv_in1.msg.predicate==Bits1(1)) )
      if s.recv_in0.msg.predicate == Bits1( 1 ):
        s.send_out.msg = s.recv_in0.msg
      elif s.recv_in1.msg.predicate == Bits1( 1 ):
        s.send_out.msg = s.recv_in1.msg

  def line_trace( s ):
    symbol0 = "#"
    symbol1 = "#"
    if s.recv_in0.msg.predicate == Bits1(1):
      symbol0 = "*"
      symbol1 = " "
    elif s.recv_in1.msg.predicate == Bits1(1):
      symbol0 = " "
      symbol1 = "*"
    return f'[{s.recv_in0.msg} {symbol0}] [{s.recv_in1.msg} {symbol1}] = [{s.send_out.msg}]'
