"""
==========================================================================
Alu.py
==========================================================================
Simple generic ALU for CGRA tile.

Author : Cheng Tan
  Date : November 27, 2019

"""

from pymtl3 import *

class Alu( Component ):

  def construct( s, DataType ):

    s.in0 = InPort ( DataType )
    s.in1 = InPort ( DataType )

    s.out = OutPort( DataType )

    @s.update
    def comb_logic():
      s.out = s.in0 + s.in1

  def line_trace( s ):
    return f'{s.in0} + {s.in1} = {s.out}'
