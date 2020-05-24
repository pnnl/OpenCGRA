"""
==========================================================================
Sel.py
==========================================================================
Functional unit Select for CGRA tile.

Author : Cheng Tan
  Date : May 23, 2020

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type    import *
from ..basic.Fu         import Fu

class Sel( Fu ):

  def construct( s, DataType, ConfigType, num_inports, num_outports,
                 data_mem_size ):

    super( Sel, s ).construct( DataType, ConfigType, num_inports, num_outports,
           data_mem_size )

    s.true = DataType(1, 1)

    @s.update
    def comb_logic():
      for j in range( num_outports ):
        s.send_out[j].en = s.recv_opt.en# and s.send_out[j].rdy and s.recv_in[0].en
      if s.recv_opt.msg.ctrl == OPT_SEL:
        if s.recv_in[0].msg.payload == s.true.payload:
          s.send_out[0].msg = s.recv_in[1].msg
        else:
          s.send_out[0].msg = s.recv_in[2].msg
      else:
        for j in range( num_outports ):
          s.send_out[j].en = b1( 0 )

  def line_trace( s ):
#    symbol = "#"
    symbol = "T"
    if s.recv_in[0].msg.predicate == Bits1(1):
      symbol = "T" if s.recv_in[0].msg.payload == s.true.payload else "F"
    return f'[{s.recv_in[1].msg}] {symbol} [{s.recv_in[2].msg}] = [{s.send_out[0].msg}]'
