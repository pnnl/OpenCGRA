"""
==========================================================================
ctrl_helper.py
==========================================================================
Helper classes and functions to wrap configure signal for each tile on 
CGRA.

Author : Cheng Tan
  Date : Feb 22, 2020

"""

from .messages                import *
from .map_helper              import *
from ..fu.flexible.FlexibleFu import FlexibleFu

import json

class TileCtrl:

  def __init__( s, FuType, CtrlType, RouteType, x, y, num_outports, II ):
    s.FuType = FuType
    s.CtrlType = CtrlType
    s.RouteType = RouteType
    s.x      = x
    s.y      = y
    s.II     = II
#    s.opts   = [ CtrlType( 0, 0 ) ] * II
#    s.routes = [ [ RouteType( 0 ) ] * num_outports ] * II
    s.ctrl   = [ CtrlType( OPT_NAH, [ RouteType( 0 ) ] * num_outports ) ] * II

  def update_ctrl( s, cycle, ctrl ):
#    s.opts[cycle]   = opt
#    s.routes[cycle] = route
    s.ctrl[ cycle ] = ctrl

  def get_ctrl( s ):
    return s.ctrl

def get_tile( x, y, tiles ):
  for tile in tiles:
    if tile.x == x and tile.y == y:
      return tile
  return None

class CGRACtrl:

  def __init__( s, json_file_name, CtrlType, RouteType, width, height,
                num_outports, II ):
    s.tiles = []
    for x in range( width ):
      for y in range( height ):
        s.tiles.append( TileCtrl( FlexibleFu, CtrlType, RouteType,
                                  x, y, num_outports, II ) )
    with open( json_file_name ) as json_file:
      ctrls = json.load( json_file )
      for ctrl in ctrls:
        tile  = get_tile( ctrl['x'], ctrl['y'], s.tiles )
        route = [] 
        for i in range( num_outports ):
          out = ctrl['out_'+str(i)]
          out = RouteType( out + 1 ) if out != "none" else RouteType( 0 )
          route.append( out )
        tile.update_ctrl( ctrl['cycle']%II, CtrlType( opt_map[ ctrl['opt'] ], route ) )
#        print( tile.ctrl )

  def get_ctrl( s ):
    ctrls = []
    for tile in s.tiles:
      ctrls.append( tile.ctrl )
    return ctrls

