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

  def construct( s, DataType, CtrlType ):

    super( SeqMulAlu, s ).construct( DataType, CtrlType, Mul, Alu )

    @s.update
    def update_opt():
      if s.recv_opt.msg.ctrl == OPT_MUL_ADD:
        s.Fu0.recv_opt.msg = CtrlType( OPT_MUL )
        s.Fu1.recv_opt.msg = CtrlType( OPT_ADD )
      elif s.recv_opt.msg.ctrl == OPT_MUL_SUB:
        s.Fu0.recv_opt.msg = CtrlType( OPT_MUL )
        s.Fu1.recv_opt.msg = CtrlType( OPT_SUB )
      # TODO: need to handle the other cases
