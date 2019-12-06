"""
==========================================================================
ThreeComb.py
==========================================================================
Simple generic two parallelly combined functional units followd by single
functional unit for CGRA tile.

Author : Cheng Tan
  Date : November 28, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type    import *

class ThreeComb( Component ):

  def construct( s, DataType, ConfigType, Fu0, Fu1, Fu2 ):

    # Constant
    OptType = Bits5

    # Interface
    s.recv_in0  = RecvIfcRTL( DataType   )
    s.recv_in1  = RecvIfcRTL( DataType   )
    s.recv_in2  = RecvIfcRTL( DataType   )
    s.recv_in3  = RecvIfcRTL( DataType   )
    s.recv_opt0 = RecvIfcRTL( ConfigType )
    s.recv_opt1 = RecvIfcRTL( ConfigType )
    s.recv_opt2 = RecvIfcRTL( ConfigType )
    s.send_out  = SendIfcRTL( DataType   )

    # Components
    s.Fu0 = Fu0( DataType, ConfigType )
    s.Fu1 = Fu1( DataType, ConfigType )
    s.Fu2 = Fu2( DataType, ConfigType )

    # Connections
    s.recv_in0.msg     //= s.Fu0.recv_in0.msg
    s.recv_in1.msg     //= s.Fu0.recv_in1.msg
    s.recv_in2.msg     //= s.Fu1.recv_in0.msg
    s.recv_in3.msg     //= s.Fu1.recv_in1.msg

    s.Fu0.recv_opt.msg //= s.recv_opt0.msg
    s.Fu1.recv_opt.msg //= s.recv_opt1.msg
    s.Fu2.recv_opt.msg //= s.recv_opt2.msg

    s.Fu0.send_out.msg //= s.Fu2.recv_in0.msg
    s.Fu1.send_out.msg //= s.Fu2.recv_in1.msg
    s.Fu2.send_out.msg //= s.send_out.msg

    @s.update
    def update_signal():
      s.recv_in0.rdy  = s.send_out.rdy
      s.recv_in1.rdy  = s.send_out.rdy
      s.recv_in2.rdy  = s.send_out.rdy
      s.recv_in3.rdy  = s.send_out.rdy
      s.recv_opt0.rdy = s.send_out.rdy
      s.recv_opt1.rdy = s.send_out.rdy
      s.recv_opt2.rdy = s.send_out.rdy
      s.send_out.en   = s.recv_in0.en  and s.recv_in1.en  and\
                        s.recv_in2.en  and s.recv_in3.en  and\
                        s.recv_opt0.en and s.recv_opt1.en and\
                        s.recv_opt2.en

  def line_trace( s ):
    return f'([{s.recv_in0.msg}] {OPT_SYMBOL_DICT[s.recv_opt0.msg.config]} [{s.recv_in1.msg}]) {OPT_SYMBOL_DICT[s.recv_opt2.msg.config]} ([{s.recv_in2.msg}] {OPT_SYMBOL_DICT[s.recv_opt1.msg.config]} [{s.recv_in3.msg}]) = [{s.send_out.msg}]'
