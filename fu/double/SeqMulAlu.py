"""
==========================================================================
SeqMulAlu.py
==========================================================================
Mul followed by ALU in sequential for CGRA tile.

Author : Cheng Tan
  Date : November 28, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs  import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type     import *
from ..basic.TwoSeqCombo import TwoSeqCombo
from ..single.Mul        import Mul
from ..single.Alu        import Alu

class SeqMulAlu( TwoSeqCombo ):

  def construct( s, DataType, CtrlType, num_inports, num_outports,
                 data_mem_size ):

    super( SeqMulAlu, s ).construct( DataType, CtrlType, Mul, Alu,
           num_inports, num_outports, data_mem_size )

    @s.update
    def update_opt():

      s.Fu0.recv_opt.msg.fu_in[0] = Bits2(1)
      s.Fu0.recv_opt.msg.fu_in[1] = Bits2(2)
      s.Fu1.recv_opt.msg.fu_in[0] = Bits2(1)
      s.Fu1.recv_opt.msg.fu_in[1] = Bits2(2)

      if s.recv_opt.msg.ctrl == OPT_MUL_ADD:
        s.Fu0.recv_opt.msg.ctrl = OPT_MUL
        s.Fu1.recv_opt.msg.ctrl = OPT_ADD
      elif s.recv_opt.msg.ctrl == OPT_MUL_CONST_ADD:
        s.Fu0.recv_opt.msg.ctrl = OPT_MUL_CONST
        s.Fu1.recv_opt.msg.ctrl = OPT_ADD
      elif s.recv_opt.msg.ctrl == OPT_MUL_CONST:
        s.Fu0.recv_opt.msg.ctrl = OPT_MUL_CONST
        s.Fu1.recv_opt.msg.ctrl = OPT_PAS
      elif s.recv_opt.msg.ctrl == OPT_MUL_SUB:
        s.Fu0.recv_opt.msg.ctrl = OPT_MUL
        s.Fu1.recv_opt.msg.ctrl = OPT_SUB
      # TODO: need to handle the other cases

