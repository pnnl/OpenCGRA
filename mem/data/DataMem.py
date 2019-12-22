"""
==========================================================================
DataMem.py
==========================================================================
Data memory for CGRA.

Author : Cheng Tan
  Date : Dec 20, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type    import *
from pymtl3.stdlib.rtl  import RegisterFile

class DataMem( Component ):

  def construct( s, DataType, nregs=8, rd_ports=1, wr_ports=1 ):

    # Constant

    AddrType = mk_bits( clog2( nregs ) )

    # Interface

    s.recv_raddr = [ RecvIfcRTL( AddrType ) for _ in range( rd_ports ) ]
    s.send_rdata = [ SendIfcRTL( DataType ) for _ in range( rd_ports ) ]
    s.recv_waddr = [ RecvIfcRTL( AddrType ) for _ in range( wr_ports ) ]
    s.recv_wdata = [ RecvIfcRTL( DataType ) for _ in range( wr_ports ) ]

    # Component

    s.reg_file   = RegisterFile( DataType, nregs, rd_ports, wr_ports )

    # Connections

    for i in range( rd_ports ):
      s.reg_file.raddr[i] //= s.recv_raddr[i].msg
      s.send_rdata[i].msg //= s.reg_file.rdata[i]

    for i in range( wr_ports ):
      s.reg_file.waddr[i] //= s.recv_waddr[i].msg
      s.reg_file.wdata[i] //= s.recv_wdata[i].msg
      s.reg_file.wen[i]   //= s.recv_wdata[i].en and s.recv_waddr[i].en

    @s.update
    def update_signal():
      for i in range( rd_ports ):
        s.recv_raddr[i].rdy = b1( 1 ) # s.send_rdata[i].rdy
        s.send_rdata[i].en  = s.send_rdata[i].rdy # s.recv_raddr[i].en
      for i in range( wr_ports ):
        s.recv_waddr[i].rdy = Bits1( 1 )
        s.recv_wdata[i].rdy = Bits1( 1 )

  def line_trace( s ):
    recv_str = "|".join([ str(data.msg) for data in s.recv_wdata    ])
    out_str  = "|".join([ str(data)     for data in s.reg_file.regs ])
    send_str = "|".join([ str(data.msg) for data in s.send_rdata    ])
    return f'{recv_str} : [{out_str}] : {send_str}'

