"""
==========================================================================
MemUnit.py
==========================================================================
Scratchpad memory access unit for (the left most) CGRA tiles.

Author : Cheng Tan
  Date : November 29, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ..ifcs.opt_type    import *
from .Fu                import Fu

class MemUnit( Fu ):

  def construct( s, DataType ):

    super( MemUnit, s ).construct( DataType )

    # Constant
    MEM_SIZE = 10

#    # Interface
#    s.recv_addr = RecvIfcRTL( DataType )
#    s.recv_data = RecvIfcRTL( DataType )
#    s.recv_opt  = RecvIfcRTL( DataType )
#    s.send_out  = SendIfcRTL( DataType )

    # Components
    s.sram =  {}
    for i in range( MEM_SIZE ):
      s.sram[ DataType( i ) ] = DataType( i+1 )
    print( 'Data SPM[', DataType( i ), ']: ', len( s.sram ) )

#    @s.update
#    def update_signal():
#      s.recv_addr.rdy = s.send_out.rdy
#      s.recv_data.rdy = s.send_out.rdy
#      s.recv_opt.rdy  = s.send_out.rdy
#      s.send_out.en   = s.recv_addr.en and s.recv_data.en and s.recv_opt.en

    @s.update
    def comb_logic():
      if s.recv_opt.msg == OPT_LD:
        s.send_out.msg = s.sram[s.recv_in0.msg]
      elif s.recv_opt.msg == OPT_STR:
        s.sram[s.recv_in0.msg] = s.recv_in1.msg

  def line_trace( s ):
    if s.recv_opt.msg == OPT_LD:
      return f'{OPT_SYMBOL_DICT[s.recv_opt.msg]} [{s.recv_in0.msg}] = [{s.send_out.msg}]'
    elif s.recv_opt.msg == OPT_STR:
      return f'{OPT_SYMBOL_DICT[s.recv_opt.msg]} [{s.recv_in0.msg}] = [{s.recv_in1.msg}]'
