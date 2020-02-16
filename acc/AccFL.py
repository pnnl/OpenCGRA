"""
=========================================================================
AccFL.py
=========================================================================
A accelerator implemented in functional level for verification of the CL
and RTL designs. It takes the DFG as input, generate the outputs (live-in),
and write values into a list (mimic the scratchpad).

Author : Cheng Tan
  Date : Feb 13, 2020

"""

from pymtl3         import *
from ..lib.opt_type import *
from ..lib.messages import *

#------------------------------------------------------------------------
# Assuming that the elements in FuDFG are already ordered well.
#------------------------------------------------------------------------
def acc_fl( FuDFG, DataType, CtrlType, src_const, spm ):

  live_out = DataType( 0, 0 )

  print("data SPM: ", spm)

  while live_out.predicate == Bits1( 0 ):
    const_index = 0
    for node in FuDFG.nodes:
      current_input = []
      print("id: ", node.id, " node.num_const: ", node.num_const, "; node.num_input: ", node.num_input)
      if node.num_const != 0:
        for _ in range( node.num_const ):
          current_input.append( src_const[const_index] );
          const_index += 1
      if node.num_input != 0:
        for value in node.input_value:
          current_input.append(value);
  
      result  = [ DataType( 0, 1 ) for _ in node.num_output ]
      print( "id: ", node.id, " current_input: ", current_input )
      if node.opt == OPT_ADD:
        result[0].payload = current_input[0].payload + current_input[1].payload
      elif node.opt == OPT_SUB:
        result[0].payload = current_input[0].payload - current_input[1].payload
      elif node.opt == OPT_MUL:
        result[0].payload = current_input[0].payload * current_input[1].payload
      elif node.opt == OPT_PHI:
        if current_input[1].predicate == Bits1( 1 ):
          result[0].payload = current_input[1].payload
        else:
          result[0].payload = current_input[0].payload
      elif node.opt == OPT_LD:
        result[0].payload = spm[current_input[0].payload]
      elif node.opt == OPT_EQ:
#        if current_input[0].payload == current_input[1].payload:
        # FIXME: need to specify the constant input for each node
        if current_input[0].payload == current_input[1].payload:
          result[0] = DataType( 1, 1)
        else:
          result[0] = DataType( 0, 1)
      elif node.opt == OPT_BRH:
        result[0].payload  = current_input[0].payload
        # Cmp goes into [1] while value goes into [0]
        if current_input[1].payload == 0:
          result[0].predicate  = Bits1( 1 )
        else:
          result[0].predicate  = Bits1( 0 )
        if len( node.num_output ) > 1:
          result[1] = DataType( 0, 0 )
          result[1].payload = current_input[0].payload
          if current_input[1].payload == 0:
            result[1].predicate = Bits1( 0 )
          else:
            result[1].predicate = Bits1( 1 )
        if node.live_out != 0:
          live_out = DataType( 0, 0 )
          live_out.payload = current_input[0].payload
          if current_input[1].payload == 0:
            live_out.predicate = Bits1( 0 )
          else:
            live_out.predicate = Bits1( 1 )
  
      for i in range( len( node.num_output ) ):
        print( "see node.num_output[i]: ", node.num_output[i] )
        for j in range( node.num_output[i] ):
          node.updateOutput( i, j, result[i] )
          FuDFG.nodes[node.output_node[i][j]].updateInput( result[i] )
  
      print( "id: ", node.id, " current result: ", result )

    print( "current iteration live_out: ", live_out )
    print( "--------------------------------------" )
  
  print( "final live_out: ", live_out )
  return live_out, spm

