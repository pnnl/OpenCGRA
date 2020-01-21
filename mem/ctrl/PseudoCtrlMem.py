"""
==========================================================================
PseudoCtrlMem.py
==========================================================================
Pseudo control memory used for simulation.

Author : Cheng Tan
  Date : Dec 27, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type    import *
from pymtl3.stdlib.rtl  import RegisterFile

class PseudoCtrlMem( Component ):

  def construct( s, CtrlType, ctrl_mem_size, num_ctrl=4, opt_list=None ):

    # Constant

    AddrType = mk_bits( clog2( ctrl_mem_size ) )
    TimeType = mk_bits( clog2( num_ctrl+1 ) )

    # Interface

    s.send_ctrl  = SendIfcRTL( CtrlType )

    # Component

    s.sram = [ CtrlType( 0 ) for _ in range( ctrl_mem_size ) ]
    for i in range( len( opt_list ) ):
      s.sram[ i ] = opt_list[i]
    s.times = Wire( TimeType )
    s.cur  = Wire( AddrType )

    @s.update
    def load():
      s.send_ctrl.msg = s.sram[ s.cur ]

    @s.update
    def update_signal():
      if s.times == TimeType( num_ctrl ) or s.sram[s.cur].ctrl == OPT_START:
        s.send_ctrl.en = b1( 0 )
      else:
        s.send_ctrl.en  = s.send_ctrl.rdy

    @s.update_ff
    def update_raddr():
      if s.send_ctrl.rdy:
        if s.times < TimeType( num_ctrl ):
          s.times <<= s.times + TimeType( 1 )
        if s.cur + AddrType( 1 )  == AddrType( num_ctrl ):
          s.cur <<= AddrType( 0 )
        else:
          s.cur <<= s.cur + AddrType( 1 )

  def line_trace( s ):
    out_str  = "||".join([ str(data) for data in s.sram ])
    return f'[{out_str}] : {s.send_ctrl.msg}'

