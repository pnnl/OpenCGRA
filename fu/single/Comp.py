"""
==========================================================================
Comp.py
==========================================================================
Functional unit for performing comparison.

Author : Cheng Tan
  Date : December 2, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type    import *

class Comp( Component ):

  def construct( s, DataType ):

    # Interface

    s.recv_data = RecvIfcRTL( DataType )
    s.recv_ref  = RecvIfcRTL( DataType )
    s.recv_opt  = RecvIfcRTL( DataType )
    s.send_pred = SendIfcRTL( Bits1    )

    @s.update
    def update_signal():
      s.recv_data.rdy = s.send_pred.rdy
      s.recv_ref.rdy  = s.send_pred.rdy
      s.recv_opt.rdy  = s.send_pred.rdy
      s.send_pred.en  = s.recv_data.en and s.recv_ref.en

    @s.update
    def comb_logic():
      if s.recv_opt.msg == OPT_EQ:
        if s.recv_data.msg == s.recv_ref.msg:
          s.send_pred.msg = Bits1( 1 )
        else:
          s.send_pred.msg = Bits1( 0 )
      elif s.recv_opt.msg == OPT_LE:
        if s.recv_data.msg < s.recv_ref.msg:
          s.send_pred.msg = Bits1( 1 )
        else:
          s.send_pred.msg = Bits1( 0 )

  def line_trace( s ):
    return f'[{s.recv_data.msg}] {OPT_SYMBOL_DICT[s.recv_opt.msg]} [{s.recv_ref.msg}] = {s.send_pred.msg}'

