"""
==========================================================================
PrlMulAdderRTL.py
==========================================================================
Mul and Adder in parallel for CGRA tile.

Author : Cheng Tan
  Date : November 28, 2019

"""

from pymtl3              import *
from pymtl3.stdlib.ifcs  import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type     import *
from ..basic.TwoPrlCombo import TwoPrlCombo
from ..single.MulRTL     import MulRTL
from ..single.AdderRTL   import AdderRTL

class PrlMulAdderRTL( TwoPrlCombo ):

  def construct( s, DataType, CtrlType, num_inports, num_outports,
                 data_mem_size ):

    super( PrlMulAdderRTL, s ).construct( DataType, CtrlType, MulRTL, AdderRTL,
           num_inports, num_outports, data_mem_size )

    @s.update
    def update_opt():
      if s.recv_opt.msg.ctrl == OPT_MUL_ADD:
        s.Fu0.recv_opt.msg = CtrlType( OPT_MUL, [ Bits2(1), Bits2(2) ] )
        s.Fu1.recv_opt.msg = CtrlType( OPT_ADD, [ Bits2(1), Bits2(2) ] )
      elif s.recv_opt.msg.ctrl == OPT_MUL_SUB:
        s.Fu0.recv_opt.msg = CtrlType( OPT_MUL, [ Bits2(1), Bits2(2) ] )
        s.Fu1.recv_opt.msg = CtrlType( OPT_SUB, [ Bits2(1), Bits2(2) ] )

      # TODO: need to handle the other cases

