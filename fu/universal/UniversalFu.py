"""
==========================================================================
UniversalFu.py
==========================================================================
A universal functional unit that can do everything for conventional
CGRA tile.

Author : Cheng Tan
  Date : Dec 14, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs  import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type     import *
from ..single.Mul        import Mul
from ..single.Alu        import Alu

class UniversalFu( Component ):

  def construct( s, DataType, CtrlType ):

    # Interface

    s.recv_in0  = RecvIfcRTL( DataType )
    s.recv_in1  = RecvIfcRTL( DataType )
    s.recv_in2  = RecvIfcRTL( DataType )
    s.recv_in3  = RecvIfcRTL( DataType )
    s.recv_opt  = RecvIfcRTL( CtrlType )
    s.send_out0 = SendIfcRTL( DataType )
    s.send_out1 = SendIfcRTL( DataType )

    @s.update
    def update_signal():
      s.recv_in0.rdy = s.send_out0.rdy or s.send_out1.rdy
      s.recv_in1.rdy = s.send_out0.rdy or s.send_out1.rdy
      s.recv_in2.rdy = s.send_out0.rdy or s.send_out1.rdy
      s.recv_in3.rdy = s.send_out0.rdy or s.send_out1.rdy
      s.recv_opt.rdy = s.send_out0.rdy or s.send_out1.rdy
      s.send_out0.en = s.recv_in0.en   or s.recv_in1.en   or\
                       s.recv_in2.en   or s.recv_in3.en   or s.recv_opt.en
      s.send_out1.en = s.recv_in0.en   or s.recv_in1.en   or\
                       s.recv_in2.en   or s.recv_in3.en   or s.recv_opt.en

    @s.update
    def comb_logic():
      s.send_out0.msg.predicate = s.recv_in0.msg.predicate and s.recv_in1.msg.predicate

      # Alu
      if s.recv_opt.msg.ctrl == OPT_ADD:
        s.send_out0.msg.payload = s.recv_in0.msg.payload + s.recv_in1.msg.payload
      elif s.recv_opt.msg.ctrl == OPT_INC:
        s.send_out0.msg.payload = s.recv_in0.msg.payload + Bits16( 1 )
      elif s.recv_opt.msg.ctrl == OPT_SUB:
        s.send_out0.msg.payload = s.recv_in0.msg.payload - s.recv_in1.msg.payload

      # Mul 
      elif s.recv_opt.msg.ctrl == OPT_MUL:
        s.send_out0.msg.payload = s.recv_in0.msg.payload * s.recv_in1.msg.payload

      # Shifter
      elif s.recv_opt.msg.ctrl == OPT_LLS:
        s.send_out0.msg.payload = s.recv_in0.msg.payload << s.recv_in1.msg.payload
      elif s.recv_opt.msg.ctrl == OPT_LRS:
        s.send_out0.msg.payload = s.recv_in0.msg.payload >> s.recv_in1.msg.payload

      # Logic
      elif s.recv_opt.msg.ctrl == OPT_OR:
        s.send_out0.msg.payload = s.recv_in0.msg.payload | s.recv_in1.msg.payload
      elif s.recv_opt.msg.ctrl == OPT_AND:
        s.send_out0.msg.payload = s.recv_in0.msg.payload & s.recv_in1.msg.payload
      elif s.recv_opt.msg.ctrl == OPT_NOT:
        s.send_out0.msg.payload = ~ s.recv_in0.msg.payload
      elif s.recv_opt.msg.ctrl == OPT_XOR:
        s.send_out0.msg.payload = s.recv_in0.msg.payload ^ s.recv_in1.msg.payload

      # Comp
      elif s.recv_opt.msg.ctrl == OPT_EQ:
        if s.recv_in0.msg.payload == s.recv_in1.msg.payload:
          s.send_out0.msg = DataType( 1, 1 )
        else:
          s.send_out0.msg = DataType( 1, 1 )
      elif s.recv_opt.msg.ctrl == OPT_LE:
        if s.recv_in0.msg.payload < s.recv_in1.msg.payload:
          s.send_out0.msg = DataType( 1, 1 )
        else:
          s.send_out0.msg = DataType( 1, 1 )

      # Branch
      elif s.recv_opt.msg.ctrl == OPT_BRH:
        s.send_out0.msg.payload  = s.recv_in0.msg.payload
        s.send_out1.msg.payload  = s.recv_in0.msg.payload
        if s.recv_in0.msg == DataType( 1, 1 ):
          s.send_out0.msg.predicate = Bits1( 1 )
          s.send_out1.msg.predicate = Bits1( 0 )
        else:
          s.send_out0.msg.predicate = Bits1( 0 )
          s.send_out1.msg.predicate = Bits1( 1 )

      # Phi
      elif s.recv_opt.msg.ctrl == OPT_PHI:
        if s.recv_in0.msg.predicate == Bits1( 1 ):
          s.send_out0.msg = s.recv_in0.msg
        elif s.recv_in1.msg.predicate == Bits1( 1 ):
          s.send_out0.msg = s.recv_in1.msg

  def line_trace( s ):
    return f'[{s.recv_in0.msg}] {OPT_SYMBOL_DICT[s.recv_opt.msg.ctrl]} [{s.recv_in1.msg}] = [{s.send_out0.msg}]'

