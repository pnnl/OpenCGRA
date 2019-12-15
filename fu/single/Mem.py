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
from ...lib.opt_type    import *
from ..basic.Fu         import Fu

class Mem( Fu ):

  def construct( s, DataType, ConfigType ):

    super( Mem, s ).construct( DataType, ConfigType )

    # Constant
    MEM_SIZE = 10

    # Components
    s.sram =  {}
    for i in range( MEM_SIZE ):
      s.sram[ DataType( i, 1 ).payload ] = DataType( i+1, 1 ).payload

    @s.update
    def comb_logic():
      if s.recv_opt.msg.ctrl == OPT_LD:
        s.send_out0.msg.predicate = s.recv_in0.msg.predicate
        s.send_out0.msg.payload = s.sram[s.recv_in0.msg.payload]
      elif s.recv_opt.msg.ctrl == OPT_STR:
        s.sram[s.recv_in0.msg.payload] = s.recv_in1.msg.payload
