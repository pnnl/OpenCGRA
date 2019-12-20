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

  def construct( s, DataType, nregs=8, rd_ports=4, wr_ports=4 ):

    # Constant

    AddrType = mk_bits( clog2( nregs ) )

    # Interface

    s.recv_waddr = [ RecvIfcRTL( AddrType ) for _ in range( wr_ports ) ]
    s.recv_wdata = [ RecvIfcRTL( DataType ) for _ in range( wr_ports ) ]
    s.recv_raddr = [ RecvIfcRTL( AddrType ) for _ in range( rd_ports ) ]
    s.send_rdata = [ SendIfcRTL( DataType ) for _ in range( rd_ports ) ]

    # Component

    s.reg_file   = RegisterFile( DataType, nregs, rd_ports, wr_ports )

    # Connections

    for i in range( rd_ports ):
      s.reg_file.raddr[i] //= s.recv_raddr[i].msg
      s.send_rdata[i].msg //= s.reg_file.rdata[i]

    for i in range( wr_ports ):
      s.reg_file.waddr[i] //= s.recv_waddr[i].msg
      s.reg_file.wdata[i] //= s.recv_wdata[i].msg
      s.reg_file.wen[i]   //= b1( 1 )

    @s.update
    def update_signal():
      for i in range( rd_ports ):
        s.recv_raddr[i].rdy = s.send_rdata[i].rdy
        s.send_rdata[i].en  = s.recv_raddr[i].en
      for i in range( wr_ports ):
        s.recv_waddr[i].rdy = s.send_rdata[i].rdy
        s.recv_wdata[i].rdy = s.send_rdata[i].rdy

  def line_trace( s ):
    out_str = "|".join([ str(data) for data in s.reg_file.regs ])
    return f'[{out_str}] : {s.recv_wdata.msg}'

