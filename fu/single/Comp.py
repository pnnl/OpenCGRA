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
from ..basic.Fu         import Fu

class Comp( Fu ):

  def construct( s, DataType, ConfigType ):

    super( Comp, s ).construct( DataType, ConfigType )
    # data:      s.recv_in0
    # reference: s.recv_in1

    @s.update
    def comb_logic():
      predicate = s.recv_in0.msg.predicate & s.recv_in1.msg.predicate
      if s.recv_opt.msg.ctrl == OPT_EQ:
        if s.recv_in0.msg.payload == s.recv_in1.msg.payload:
          s.send_out0.msg = DataType( 1, predicate )
        else:
          s.send_out0.msg = DataType( 0, predicate )
      elif s.recv_opt.msg.ctrl == OPT_LE:
        if s.recv_in0.msg.payload < s.recv_in1.msg.payload:
          s.send_out0.msg = DataType( 1, predicate )
        else:
          s.send_out0.msg = DataType( 0, predicate )

