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

  spm = []
  live_out = []

  const_index = 0
  for e in FuDFG.elements:
    current_input = []
    if e.num_const != 0:
      for _ in range(e.num_const):
        current_input.append(src_const[const_index][0]);
        const_index += 1
    if e.num_input != 0:
      for value in e.input_value:
        current_input.append(value);

    result = DataType( 0, 1 )
    if e.opt == OPT_ADD:
      result.payload = current_input[0].payload + current_input[1].payload
    elif e.opt == OPT_SUB:
      result.payload = current_input[0].payload - current_input[1].payload
    elif e.opt == OPT_MUL:
      result.payload = current_input[0].payload * current_input[1].payload
      
    if e.num_output != 0:
      for i in range( e.num_output ):
        e.updateOutput( i, result )
        FuDFG.elements[e.output_element[i]].updateInput( result )
    else:
      live_out.append(result)
  
  print( live_out )
  return live_out

