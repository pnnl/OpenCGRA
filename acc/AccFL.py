"""
=========================================================================
AccFL.py
=========================================================================
A accelerator implemented in functional level for verification of the CL
and RTL designs.
It takes the DFG as input, generate the outputs (live-in), and write
values into a list (mimic the scratchpad).

Author : Cheng Tan
  Date : Feb 13, 2020

"""

from pymtl3         import *
from ..lib.opt_type import *
from ..lib.messages import *

#------------------------------------------------------------------------
# Assuming that the elements in FuDFG are already ordered well.
#------------------------------------------------------------------------
def acc_fl( FuDFG, DataType, CtrlType, src_const ):

  spm = [ 2 ] * 10
  live_out = []

  print("data SPM: ", spm)

  const_index = 0
  for e in FuDFG.elements:
    current_input = []
    print("e.const: ", e.num_const, "; e.num_input: ", e.num_input)
    if e.num_const != 0:
      for _ in range(e.num_const):
        current_input.append(src_const[const_index][0]);
        const_index += 1
    if e.num_input != 0:
      for value in e.input_value:
        current_input.append(value);

    result  = DataType( 0, 1 )
    result2 = None
    print("current_input: ", current_input)
    if e.opt == OPT_ADD:
      result.payload = current_input[0].payload + current_input[1].payload
    elif e.opt == OPT_SUB:
      result.payload = current_input[0].payload - current_input[1].payload
    elif e.opt == OPT_MUL:
      result.payload = current_input[0].payload * current_input[1].payload
    elif e.opt == OPT_PHI:
      if current_input[1].predicate == Bits1( 1 ):
        result.payload = current_input[1].payload
      else:
        result.payload = current_input[0].payload
    elif e.opt == OPT_LD:
      result.payload = spm[current_input[0].payload]
    elif e.opt == OPT_EQ:
      if current_input[0].payload == current_input[1].payload:
        result.payload = DataType( 1, 1)
      else:
        result.payload = DataType( 0, 1)
    elif e.opt == OPT_BRH:
      result.payload  = current_input[0].payload
      if current_input[1].payload == Bits16( 0 ):
        result.predicate  = Bits1( 1 )
      else:
        result.predicate  = Bits1( 0 )
      if e.live_out != 0:
        result2 = DataType( 0, 0 )
        result2.payload = current_input[0].payload
        if current_input[1].payload == Bits16( 0 ):
          result2.predicate = Bits1( 0 )
        else:
          result2.predicate = Bits1( 1 )

    if e.num_output != 0:
      for i in range( e.num_output ):
        e.updateOutput( i, result )
        FuDFG.elements[e.output_element[i]].updateInput( result )

    if e.live_out != 0:
      live_out.append(result2)

    print( "current result: ", result )
  
  print( "live_out: ", live_out )
  return live_out

