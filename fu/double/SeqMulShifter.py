"""
==========================================================================
SeqMulShifter.py
==========================================================================
Mul followed by Shifter in sequential for CGRA tile.

Author : Cheng Tan
  Date : November 28, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs  import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type     import *
from ..basic.TwoSeqCombo import TwoSeqCombo
from ..single.Mul        import Mul
from ..single.Shifter    import Shifter

class SeqMulShifter( TwoSeqCombo ):

  def construct( s, DataType, CtrlType, num_inports, num_outports,
                 data_mem_size ):

    super( SeqMulShifter, s ).construct( DataType, CtrlType, Mul, Shifter,
           num_inports, num_outports, data_mem_size )

    @s.update
    def update_opt():
      if s.recv_opt.msg.ctrl == OPT_MUL_LLS:
        s.Fu0.recv_opt.msg = CtrlType( OPT_MUL )
        s.Fu1.recv_opt.msg = CtrlType( OPT_LLS )
      elif s.recv_opt.msg.ctrl == OPT_MUL_LRS:
        s.Fu0.recv_opt.msg = CtrlType( OPT_MUL )
        s.Fu1.recv_opt.msg = CtrlType( OPT_LRS )
      # TODO: need to handle the other cases

