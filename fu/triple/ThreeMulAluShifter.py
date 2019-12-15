"""
==========================================================================
ThreeMulShifter.py
==========================================================================
Mul and ALU in parallel for CGRA tile.

Author : Cheng Tan
  Date : November 28, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type    import *
from ..basic.ThreeCombo import ThreeCombo
from ..single.Mul       import Mul
from ..single.Alu       import Alu
from ..single.Shifter   import Shifter

class ThreeMulAluShifter( ThreeCombo ):

  def construct( s, DataType, CtrlType ):

    super( ThreeMulAluShifter, s ).construct( DataType, CtrlType, Mul, Alu, Shifter )

    @s.update
    def update_opt():
      if s.recv_opt.msg.ctrl == OPT_MUL_ADD_LLS:
        s.Fu0.recv_opt.msg = CtrlType( OPT_MUL )
        s.Fu1.recv_opt.msg = CtrlType( OPT_ADD )
        s.Fu2.recv_opt.msg = CtrlType( OPT_LLS )
      elif s.recv_opt.msg.ctrl == OPT_MUL_SUB_LLS:
        s.Fu0.recv_opt.msg = CtrlType( OPT_MUL )
        s.Fu1.recv_opt.msg = CtrlType( OPT_SUB )
        s.Fu2.recv_opt.msg = CtrlType( OPT_LLS )
      elif s.recv_opt.msg.ctrl == OPT_MUL_SUB_LRS:
        s.Fu0.recv_opt.msg = CtrlType( OPT_MUL )
        s.Fu1.recv_opt.msg = CtrlType( OPT_SUB )
        s.Fu2.recv_opt.msg = CtrlType( OPT_LRS )

      # TODO: need to handle the other cases
