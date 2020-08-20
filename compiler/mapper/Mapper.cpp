/*
 * ======================================================================
 * Mapper.cpp
 * ======================================================================
 * Mapper implementation.
 *
 * Author : Cheng Tan
 *   Date : July 16, 2019
 */

#include "Mapper.h"
#include <cmath>
#include <iostream>
#include <string>
#include <list>
#include <map>
#include <fstream>

//#include <nlohmann/json.hpp>
//using json = nlohmann::json;

int Mapper::getResMII(DFG* t_dfg, CGRA* t_cgra) {
  int ResMII = ceil(float(t_dfg->getNodeCount()) / t_cgra->getFUCount());
  return ResMII;
}

int Mapper::getRecMII(DFG* t_dfg) {
  float RecMII = 0.0;
  float temp_RecMII = 0.0;
  list<list<DFGEdge*>*>* cycles = t_dfg->getCycles();
  errs()<<"... number of cycles: "<<cycles->size()<<" ...\n";
  // TODO: RecMII = MAX (delay(c) / distance(c))
  for( list<DFGEdge*>* cycle: *cycles) {
    temp_RecMII = float(cycle->size()) / 1.0;
    if(temp_RecMII > RecMII)
      RecMII = temp_RecMII;
  }
  return ceil(RecMII);
}

void Mapper::constructMRRG(DFG* t_dfg, CGRA* t_cgra, int t_II) {
  m_mapping.clear();
  m_mappingTiming.clear();
  t_cgra->constructMRRG(t_II);
  m_maxMappingCycle = t_cgra->getFUCount()*t_II*t_II;
  for (DFGNode* dfgNode: t_dfg->nodes) {
    dfgNode->clearMapped();
  }
}

// TODO: assume that the arriving data can stay inside the input buffer
map<CGRANode*, int>* Mapper::dijkstra_search(CGRA* t_cgra, DFG* t_dfg,
    int t_II, DFGNode* t_srcDFGNode, DFGNode* t_targetDFGNode,
    CGRANode* t_dstCGRANode) {
  list<CGRANode*> searchPool;
  map<CGRANode*, int> distance;
  map<CGRANode*, int> timing;
  map<CGRANode*, CGRANode*> previous;
//  if (t_srcDFGNode->getID() == 0) {
//    errs()<<"DEBUG -1, srcDFGNode: "<<(t_srcDFGNode->getID())<<"; CGRANode: "<<m_mapping[t_srcDFGNode]->getID()<<"\n";
//    errs()<<"DEBUG -2, t_dstCGRANode: "<<t_dstCGRANode->getID()<<"; timing for src: "<<m_mappingTiming[t_srcDFGNode]<<"\n";
//  }
  timing[m_mapping[t_srcDFGNode]] = m_mappingTiming[t_srcDFGNode];
  for (int i=0; i<t_cgra->getRows(); ++i) {
    for (int j=0; j<t_cgra->getColumns(); ++j) {
      CGRANode* node = t_cgra->nodes[i][j];
      distance[node] = m_maxMappingCycle;
      timing[node] = m_mappingTiming[t_srcDFGNode];
      // TODO: should also consider the xbar here?
//      if (!cgra->nodes[i][j]->canOccupyFU(timing[node], II)) {
//        int temp_cycle = timing[node];
//        timing[node] = m_maxMappingCycle;
//        while (temp_cycle < m_maxMappingCycle) {
//          if (cgra->nodes[i][j]->canOccupyFU(temp_cycle, II)) {
//            timing[node] = temp_cycle;
//            break;
//          }
//          ++temp_cycle;
//        }
//      }
      previous[node] = NULL;
      searchPool.push_back(t_cgra->nodes[i][j]);
    }
  }
  distance[m_mapping[t_srcDFGNode]] = 0;
  while (searchPool.size() != 0) {
    int minCost = m_maxMappingCycle + 1;
    CGRANode* minNode;
    for (CGRANode* currentNode: searchPool) {
      if (distance[currentNode] < minCost) {
        minCost = distance[currentNode];
        minNode = currentNode;
      }
    }
    assert(minNode != NULL);
    searchPool.remove(minNode);
    // found the target point in the shortest path
    if (minNode == t_dstCGRANode) {
      timing[t_dstCGRANode] = minNode->getMinIdleCycle(timing[minNode], t_II);
      break;
    }
    list<CGRANode*>* currentNeighbors = minNode->getNeighbors();
//    errs()<<"DEBUG no need?\n";

    for (CGRANode* neighbor: *currentNeighbors) {
      int cycle = timing[minNode];
      while (1) {
        CGRALink* currentLink = minNode->getOutLink(neighbor);
        // TODO: should also consider the cost of the register file
        if (currentLink->canOccupy(t_srcDFGNode, cycle, t_II)) {
          // rough estimate the cost based on the suspend cycle
          int cost = distance[minNode] + (cycle - timing[minNode]) + 1;
          if (cost < distance[neighbor]) {
            distance[neighbor] = cost;
            timing[neighbor] = cycle + 1;
            previous[neighbor] = minNode;
          }
          break;
        }
        ++cycle;
        if(cycle > m_maxMappingCycle)
          break;
      }
    }
  }

  // Get the shortest path.
  map<CGRANode*, int>* path = new map<CGRANode*, int>();
  CGRANode* u = t_dstCGRANode;
  if(previous[u] != NULL or u == m_mapping[t_srcDFGNode])
  {
    while(u != NULL)
    {
      (*path)[u] = timing[u];
      u = previous[u];
    }
  }
  if(timing[t_dstCGRANode] > m_maxMappingCycle or
      !t_dstCGRANode->canOccupy(t_targetDFGNode,
      timing[t_dstCGRANode], t_II)) {
//    path.clear();
    delete path;
    return NULL;
  }
  return path;
}

list<map<CGRANode*, int>*>* Mapper::getOrderedPotentialPaths(CGRA* t_cgra,
    DFG* t_dfg, int t_II, DFGNode* t_dfgNode, list<map<CGRANode*, int>*>* t_paths) {
  map<map<CGRANode*, int>*, float>* pathsWithCost =
      new map<map<CGRANode*, int>*, float>();
  for (list<map<CGRANode*, int>*>::iterator path=t_paths->begin();
      path!=t_paths->end(); ++path) {
    if ((*path)->size() == 0)
      continue;

    map<int, CGRANode*>* reorderPath = getReorderPath(*path);
//    for (map<CGRANode*, int>::iterator rp=(*path)->begin(); rp!=(*path)->end(); ++rp)
//      reorderPath[(*rp).second] = (*rp).first;
//    assert(reorderPath.size() == (*path)->size());

    map<int, CGRANode*>::reverse_iterator riter=reorderPath->rbegin();

    int distanceCost = (*riter).first;
    CGRANode* targetCGRANode = (*riter).second;
    int targetCycle = (*riter).first;
    if (distanceCost >= m_maxMappingCycle)
      continue;
//    if (t_dfgNode->getID() == 2 or t_dfgNode->getID() == 1) {
//      errs()<<"DEBUG what?! distance: "<<distanceCost<<"; target CGRA node: "<<targetCGRANode->getID()<<"\n";
//    }
    // Consider the cost of the distance.
    float cost = distanceCost + 1;

    // Consider the cost of the utilization of contrl memory.
    cost += targetCGRANode->getCurrentCtrlMemItems()/2;

    // Consider the cost of the outgoing ports.
    if (t_dfgNode->getSuccNodes()->size() > 1) {
      cost += 4 - targetCGRANode->getOutLinks()->size() +
          abs(t_cgra->getColumns()/2-targetCGRANode->getX()) +
          abs(t_cgra->getRows()/2-targetCGRANode->getX());
    }
    if (t_dfgNode->getPredNodes()->size() > 0) {
      list<DFGNode*>* tempPredNodes = t_dfgNode->getPredNodes();
      for (DFGNode* predDFGNode: *tempPredNodes) {
        if (predDFGNode->getSuccNodes()->size() > 2
            and m_mapping.find(predDFGNode) != m_mapping.end()) {
          if (m_mapping[predDFGNode] == targetCGRANode)
            cost -= 0.5;
        }
      }
    }

    /*
    // Prefer to map the DFG nodes from left to right rather than
    // always picking CGRA node at left.
    if (t_dfgNode->getPredNodes()->size() > 0) {
      list<DFGNode*>* tempPredNodes = t_dfgNode->getPredNodes();
      for (DFGNode* predDFGNode: *tempPredNodes) {
        if (m_mapping.find(predDFGNode) != m_mapping.end()) {
          if (m_mapping[predDFGNode]->getX() > targetCGRANode->getX() or
              m_mapping[predDFGNode]->getY() > targetCGRANode->getY()) {
            cost += 0.5;
          }
        }
      }
    }
    */

    // Consider the cost of that the DFG node with multiple successor
    // might potentially occupy the surrounding CGRA nodes.
    list<CGRANode*>* neighbors = targetCGRANode->getNeighbors();
    for (CGRANode* neighbor: *neighbors) {
      list<DFGNode*>* dfgNodes = getMappedDFGNodes(t_dfg, neighbor);
      for (DFGNode* dfgNode: *dfgNodes) {
        if (dfgNode->getSuccNodes()->size() > 2) {
          cost += 0.4;
        }
      }
    }

    // Consider the cost of occupying the leftmost (rightmost) CGRA
    // nodes that are reserved for load.
    if ((!t_dfgNode->isLoad() and targetCGRANode->canLoad()) or
        (!t_dfgNode->isStore() and targetCGRANode->canStore())) {
      cost += 2;
    }

    // Consider the bonus of reusing the same link for delivery the
    // same data to different destination CGRA nodes (multicast).
    map<int, CGRANode*>::iterator lastCGRANodeItr=reorderPath->begin();
    for (map<int, CGRANode*>::iterator cgraNodeItr=reorderPath->begin();
        cgraNodeItr!=reorderPath->end(); ++cgraNodeItr) {
      if (cgraNodeItr != reorderPath->begin()) {
        CGRANode* left = (*lastCGRANodeItr).second;
        CGRANode* right = (*cgraNodeItr).second;
        int leftCycle = (*lastCGRANodeItr).first;
//        errs()<<"$$$$$$$$$$ wrong?! left node: "<<left->getID()<<" -> right node: "<<right->getID()<<"\n";
        CGRALink* l = left->getOutLink(right);
        if (l != NULL and l->isReused(leftCycle)) {
          cost -= 0.5;
        }
      }
      lastCGRANodeItr = cgraNodeItr;
    }

    // Consider the bonus of available links on the target CGRA nodes.
    cost -= targetCGRANode->getOccupiableInLinks(targetCycle, t_II)->size()*0.3 +
        targetCGRANode->getOccupiableOutLinks(targetCycle, t_II)->size()*0.3;

    (*pathsWithCost)[*path] = cost;
  }

  list<map<CGRANode*, int>*>* potentialPaths = new list<map<CGRANode*, int>*>();
  while(pathsWithCost->size() != 0) {
    float minCost = (*pathsWithCost->begin()).second;
    map<CGRANode*, int>* currentPath = (*pathsWithCost->begin()).first;
    for (map<map<CGRANode*, int>*, float>::iterator pathItr=pathsWithCost->begin();
        pathItr!=pathsWithCost->end(); ++pathItr) {
      if ((*pathItr).second < minCost) {
        minCost = (*pathItr).second;
        currentPath = (*pathItr).first;
      }
    }
    pathsWithCost->erase(currentPath);
    potentialPaths->push_back(currentPath);
  }

  delete pathsWithCost;
  return potentialPaths;
}

map<CGRANode*, int>* Mapper::getPathWithMinCostAndConstraints(CGRA* t_cgra,
    DFG* t_dfg, int t_II, DFGNode* t_dfgNode, list<map<CGRANode*, int>*>* t_paths) {

  list<map<CGRANode*, int>*>* potentialPaths =
      getOrderedPotentialPaths(t_cgra, t_dfg, t_II, t_dfgNode, t_paths);

  // The paths are already ordered well based on the cost in getPotentialPaths().
  list<map<CGRANode*, int>*>::iterator pathItr=potentialPaths->begin();
  return (*pathItr);
}

list<DFGNode*>* Mapper::getMappedDFGNodes(DFG* t_dfg, CGRANode* t_cgraNode) {
  list<DFGNode*>* dfgNodes = new list<DFGNode*>();
  for (DFGNode* dfgNode: t_dfg->nodes) {
    if (m_mapping.find(dfgNode) != m_mapping.end())
      if ( m_mapping[dfgNode] == t_cgraNode)
        dfgNodes->push_back(dfgNode);
  }
  return dfgNodes;
}

// TODO: will grant award for the overuse the same link for the
//       same data delivery
map<CGRANode*, int>* Mapper::calculateCost(CGRA* t_cgra, DFG* t_dfg,
    int t_II, DFGNode* t_dfgNode, CGRANode* t_fu) {
  map<CGRANode*, int>* path = NULL;
  list<DFGNode*>* predNodes = t_dfgNode->getPredNodes();
  int latest = -1;
  bool isAnyPredDFGNodeMapped = false;
  for(DFGNode* pre: *predNodes) {
//      errs()<<"[TAN DEBUG] how dare to pre node: "<<pre->getID()<<"; CGRA node: "<<t_fu->getID()<<"\n";
    if(m_mapping.find(pre) != m_mapping.end()) {
      // Leverage Dijkstra algorithm to search the shortest path between
      // the mapped 'CGRANode' of the 'pre' and the target 'fu'.
      map<CGRANode*, int>* tempPath = NULL;
      if (t_fu->canSupport(t_dfgNode))
        tempPath = dijkstra_search(t_cgra, t_dfg, t_II, pre,
            t_dfgNode, t_fu);
      if (tempPath == NULL)
        return NULL;
      else if ((*tempPath)[t_fu] >= m_maxMappingCycle) {
        delete tempPath;
        return NULL;
      }
      if ((*tempPath)[t_fu] > latest) {
        latest = (*tempPath)[t_fu];
        path = tempPath;
      }
      isAnyPredDFGNodeMapped = true;
    }
  }
  // TODO: should not be any CGRA node, should consider the memory access.
  // TODO  A DFG node can be mapped onto any CGRA node if no predecessor
  //       of it has been mapped.
  // TODO: should also consider the current config mem iterms.
  if (!isAnyPredDFGNodeMapped) {
    if (!t_fu->canSupport(t_dfgNode))
      return NULL;
    int cycle = 0;
    while (cycle < m_maxMappingCycle) {
      if (t_fu->canOccupy(t_dfgNode, cycle, t_II)) {
        path = new map<CGRANode*, int>();
        (*path)[t_fu] = cycle;
//        errs()<<"DEBUG how dare to map DFG node: "<<t_dfgNode->getID()<<"; CGRA node: "<<t_fu->getID()<<" at cycle "<< cycle<<"\n";
        return path;
      }
      ++cycle;
    }
//    errs() << "DEBUG: failed in mapping the starting DFG node "<<t_dfg->getID(t_dfgNode)<<" on CGRA node "<<t_fu->getID()<<"\n";
  }
  return path;
}

// Schedule is based on the modulo II, the 'path' contains one
// predecessor that can be definitely mapped, but the pathes
// containing other predecessors have possibility to fail in mapping.
bool Mapper::schedule(CGRA* t_cgra, DFG* t_dfg, int t_II,
    DFGNode* t_dfgNode, map<CGRANode*, int>* t_path, bool t_isStaticElasticCGRA) {

  map<int, CGRANode*>* reorderPath = getReorderPath(t_path);
//
//  // Since cycle on path increases gradually, re-order will not miss anything.
//  for (map<CGRANode*, int>::iterator iter=t_path->begin(); iter!=t_path->end(); ++iter)
//    reorderPath[(*iter).second] = (*iter).first;
//  assert(reorderPath.size() == t_path->size());

  map<int, CGRANode*>::reverse_iterator ri = reorderPath->rbegin();
  CGRANode* fu = (*ri).second;
//  errs()<<"schedule dfg node["<<t_dfg->getID(t_dfgNode)<<"] onto fu["<<fu->getID()<<"] at cycle "<<(*t_path)[fu]<<" within II: "<<t_II<<"\n";

  // Map the DFG node onto the CGRA nodes across cycles.
  m_mapping[t_dfgNode] = fu;
  fu->setDFGNode(t_dfgNode, (*t_path)[fu], t_II, t_isStaticElasticCGRA);
  m_mappingTiming[t_dfgNode] = (*t_path)[fu];

  // Route the dataflow onto the CGRA links across cycles.
  CGRANode* onePredCGRANode;
  int onePredCGRANodeTiming;
  map<int, CGRANode*>::iterator previousIter;
  map<int, CGRANode*>::iterator next;
  if (reorderPath->size() > 0) {
    next = reorderPath->begin();
    if (next != reorderPath->end())
      ++next;
  }
  map<int, CGRANode*>::reverse_iterator riter=reorderPath->rbegin();
  for (map<int, CGRANode*>::iterator iter=reorderPath->begin();
      iter!=reorderPath->end(); ++iter) {
    if (iter != reorderPath->begin()) {
      CGRANode* srcCGRANode = (*(reorderPath->begin())).second;
      int srcCycle = (*(reorderPath->begin())).first;
      CGRALink* l = t_cgra->getLink((*previousIter).second, (*iter).second);

      // Distinguish the bypassed and utilized data delivery on xbar.
      bool isBypass = false;
      int duration = (t_II+((*iter).first-(*previousIter).first)%t_II)%t_II;
      if ((*riter).second != (*iter).second and
          (*previousIter).first+1 == (*iter).first)
        isBypass = true;
      else
        duration = (m_mappingTiming[t_dfgNode]-(*previousIter).first)%t_II;
      l->occupy(srcCGRANode->getMappedDFGNode(srcCycle),
                (*previousIter).first, duration,
                t_II, isBypass, t_isStaticElasticCGRA);
    } else {
      onePredCGRANode = (*iter).second;
      onePredCGRANodeTiming = (*iter).first;
    }
    previousIter = iter;
  }
  delete reorderPath;

  // Try to route the path with other predecessors.
  // TODO: should consider the timing for static CGRA (two branches should
  //       joint at the same time or the register file size equals to 1)
  for (DFGNode* node: *t_dfgNode->getPredNodes()) {
    if (m_mapping.find(node) != m_mapping.end()) {
      if (m_mapping[(node)] == onePredCGRANode and
          onePredCGRANode->getMappedDFGNode(onePredCGRANodeTiming)==node) {
        errs()<<"[CHENG] skip predecessor routing -- dfgNode: "<<node->getID()<<"\n";
        continue;
      }
//      if (m_mapping[(node)] != onePredCGRANode) {
      if (!tryToRoute(t_cgra, t_dfg, t_II, node, m_mapping[node], fu,
          m_mappingTiming[t_dfgNode], false, t_isStaticElasticCGRA)){
        errs()<<"DEBUG target DFG node: "<<t_dfgNode->getID()<<" on fu: "<<fu->getID()<<" failed, mapped pred DFG node: "<<node->getID()<<"; return false\n";
        return false;
      }
//    }
    }
  }

  // Try to route the path with the mapped successors.
  for (DFGNode* node: *t_dfgNode->getSuccNodes()) {
    if (m_mapping.find(node) != m_mapping.end()) {
      if (!tryToRoute(t_cgra, t_dfg, t_II, t_dfgNode, fu, m_mapping[node],
          m_mappingTiming[node], true, t_isStaticElasticCGRA)) {
        errs()<<"DEBUG target DFG node: "<<t_dfgNode->getID()<<" on fu: "<<fu->getID()<<" failed, mapped succ DFG node: "<<node->getID()<<"; return false\n";
        return false;
      }
    }
  }
  return true;
}

int Mapper::getMaxMappingCycle() {
  return m_maxMappingCycle;
}

void Mapper::showSchedule(CGRA* t_cgra, DFG* t_dfg, int t_II,
    bool t_isStaticElasticCGRA) {
  int cycle = 0;
  int displayRows = t_cgra->getRows() * 2 - 1;
  int displayColumns = t_cgra->getColumns() * 2;
  string** display = new std::string*[displayRows];
  for (int i=0; i<displayRows; ++i)
    display[i] = new std::string[displayColumns];
  for (int i=0; i<displayRows; ++i) {
    for (int j=0; j<displayColumns; ++j) {
      display[i][j] = "     ";
      if (j == displayColumns - 1)
        display[i][j] = "\n";
    }
  }
  int showCycleBoundary = t_cgra->getFUCount();
  if (t_isStaticElasticCGRA)
    showCycleBoundary = t_dfg->getNodeCount();
  while (cycle <= showCycleBoundary) {
    errs()<<"--------------------------- cycle:"<<cycle<<" ---------------------------\n";
    for (int i=0; i<t_cgra->getRows(); ++i) {
      for (int j=0; j<t_cgra->getColumns(); ++j) {

        // Display the CGRA node occupancy.
        bool fu_occupied = false;
        DFGNode* dfgNode;
        for (DFGNode* currentDFGNode: t_dfg->nodes) {
          if (m_mappingTiming[currentDFGNode] == cycle and
              m_mapping[currentDFGNode] == t_cgra->nodes[i][j]) {
            fu_occupied = true;
            dfgNode = currentDFGNode;
            break;
          } else if (m_mapping[currentDFGNode] == t_cgra->nodes[i][j]) {
            int temp_cycle = cycle - t_II;
            while (temp_cycle >= 0) {
              if (m_mappingTiming[currentDFGNode] == temp_cycle) {
                fu_occupied = true;
                dfgNode = currentDFGNode;
                break;
              }
              temp_cycle -= t_II;
            }
          }
        }
        string str_fu;
        if (fu_occupied) {
          if (t_dfg->getID(dfgNode) < 10)
            str_fu = "[  " + to_string(dfgNode->getID()) + "  ]";
          else
            str_fu = "[ " + to_string(dfgNode->getID()) + "  ]";
        } else {
          str_fu = "[     ]";
        }
        display[i*2][j*2] = str_fu;

        // FIXME: some arrows are not display correctly (e.g., 7).
        // Display the CGRA link occupancy.
        // \u2190: left; \u2191: up; \u2192: right; \u2193: down;
        // \u21c4: left&right; \u21c5: up&down.
        // TODO: [dashed for bypass]
        // \u21e0: left; \u21e1: up; \u21e2: right; \u21e3: down;
        if (i < t_cgra->getRows() - 1) {
          string str_link = "";
          CGRALink* lu = t_cgra->getLink(t_cgra->nodes[i][j], t_cgra->nodes[i+1][j]);
          CGRALink* ld = t_cgra->getLink(t_cgra->nodes[i+1][j], t_cgra->nodes[i][j]);
          if (ld->isOccupied(cycle, t_II, t_isStaticElasticCGRA) and
              lu->isOccupied(cycle, t_II, t_isStaticElasticCGRA)) {
            str_link = "   \u21c5 ";
          } else if (ld->isOccupied(cycle, t_II, t_isStaticElasticCGRA)) {
            if (!ld->isBypass(cycle))
              str_link = "   \u2193 ";
            else
              str_link = "   \u2193 ";
          } else if (lu->isOccupied(cycle, t_II, t_isStaticElasticCGRA)) {
            if (!lu->isBypass(cycle))
              str_link = "   \u2191 ";
            else
              str_link = "   \u2191 ";
          } else {
            str_link = "     ";
          }
          display[i*2+1][j*2] = str_link;
        }
        if (j < t_cgra->getColumns() - 1) {
          string str_link = "";
          CGRALink* lr = t_cgra->getLink(t_cgra->nodes[i][j], t_cgra->nodes[i][j+1]);
          CGRALink* ll = t_cgra->getLink(t_cgra->nodes[i][j+1], t_cgra->nodes[i][j]);
          if (lr->isOccupied(cycle, t_II, t_isStaticElasticCGRA) and
              ll->isOccupied(cycle, t_II, t_isStaticElasticCGRA)) {
            str_link = " \u21c4 ";
          } else if (lr->isOccupied(cycle, t_II, t_isStaticElasticCGRA)) {
            if (!lr->isBypass(cycle))
              str_link = " \u2192 ";
            else
              str_link = " \u2192 ";
          } else if (ll->isOccupied(cycle, t_II, t_isStaticElasticCGRA)) {
            if (!ll->isBypass(cycle))
              str_link = " \u2190 ";
            else
              str_link = " \u2190 ";
          } else {
            str_link = "   ";
          }
          display[i*2][j*2+1] = str_link;
        }
      }
    }

    // Display mapping and routing cycle by cycle.
//    for (int i=0; i<displayRows; ++i) {
    for (int i=displayRows-1; i>=0; --i) {
      for (int j=0; j<displayColumns; ++j) {
        errs()<<display[i][j];
      }
    }
    ++cycle;
  }
  errs()<<"II: "<<t_II<<"\n";
}

void Mapper::generateJSON(CGRA* t_cgra, DFG* t_dfg, int t_II,
    bool t_isStaticElasticCGRA) {
  ofstream jsonFile;
  jsonFile.open("config.json");
  jsonFile<<"[\n";
  if (!t_isStaticElasticCGRA) {
    // TODO: will support dynamic CGRA JSON output soon.
    errs()<<"Will support dynamic CGRA JSON output soon.\n";

    bool first = true;
    for (int t=0; t<t_II+1; ++t) {
      for (int i=0; i<t_cgra->getRows(); ++i) {
        for (int j=0; j<t_cgra->getColumns(); ++j) {
          CGRANode* currentCGRANode = t_cgra->nodes[i][j];
          DFGNode* targetDFGNode = NULL;
          for (DFGNode* dfgNode: t_dfg->nodes) {
            if (m_mapping[dfgNode] == currentCGRANode and
                currentCGRANode->getMappedDFGNode(t) == dfgNode) {
              targetDFGNode = dfgNode;
              break;
            }
          }
          list<CGRALink*>* inLinks = currentCGRANode->getInLinks();
          list<CGRALink*>* outLinks = currentCGRANode->getOutLinks();
          bool hasInform = false;
          if (targetDFGNode != NULL) {
            hasInform = true;
          } else {
            for (CGRALink* il: *inLinks) {
              if (il->isOccupied(t, t_II, t_isStaticElasticCGRA)) {
                hasInform = true;
                break;
              }
            }
            for (CGRALink* ol: *outLinks) {
              if (ol->isOccupied(t, t_II, t_isStaticElasticCGRA)) {
                hasInform = true;
                break;
              }
            }
          }
          if (!hasInform)
            continue;
          if (first)
            first = false;
          else
            jsonFile<<",\n";
    
          jsonFile<<"  {\n";
          jsonFile<<"    \"x\"         : "<<j<<",\n";
          jsonFile<<"    \"y\"         : "<<i<<",\n";
          jsonFile<<"    \"cycle\"     : "<<t<<",\n";
          string targetOpt = "OPT_NAH";
          string stringDst[8];
          stringDst[0] = "none";
          stringDst[1] = "none";
          stringDst[2] = "none";
          stringDst[3] = "none";
          stringDst[4] = "none";
          stringDst[5] = "none";
          stringDst[6] = "none";
          stringDst[7] = "none";
          int stringDstIndex = 0;
          // handle function unit's output
          if (targetDFGNode != NULL) {
            targetOpt = targetDFGNode->getJSONOpt();
            // handle funtion unit's outputs for this cycle
            for (CGRALink* ol: *outLinks) {
              if (ol->isOccupied(t, t_II, t_isStaticElasticCGRA) and
                  ol->getMappedDFGNode(t) == targetDFGNode) {
                // FIXME: should support multiple outputs and distinguish them.
                stringDst[ol->getDirectionID(currentCGRANode)] = "4";
              }
            }
//            for (CGRALink* il: *inLinks) {
//              if (i==1 and j==1 and il->getMappedDFGNode(t) != NULL)
//                errs()<<"il->getMappedDFGNode("<<t<<"): "<<il->getMappedDFGNode(t)->getID()<<"; link: "<<il->getDirection(currentCGRANode)<<"; nextDFGNode: "<<nextDFGNode->getID()<<"\n";
//
//              if (il->isOccupied(t, t_II, t_isStaticElasticCGRA) and
//                  il->getMappedDFGNode(t) == nextDFGNode) {
//                stringDst[out_index++] = to_string(il->getDirectionID(currentCGRANode))+" (never happen?)";
//                assert(out_index <= max_index+1);
//              }
//            }
          } else {
            targetOpt = "OPT_NAH";
          }

          // handle function unit's inputs for next cycle
          int out_index = 4;
          int max_index = 7;
          for (int reg_index=0; reg_index<4; ++reg_index) {
            int direction = currentCGRANode->getRegsAllocation(t)[reg_index];
            if (direction != -1) {
              stringDst[out_index] = to_string(direction);
//              errs()<<"out_"<<out_index<<": "<<stringDst[out_index]<<"\n";
            }
            out_index++;
            assert(out_index <= max_index+1);
          }

          jsonFile<<"    \"opt"<<"\"       : \""<<targetOpt<<"\",\n";

          // handle bypass: need consider next cycle, i.e., t+1
          int next_t = t+1;
          for (CGRALink* ol: *outLinks) {
            if (ol->isOccupied(next_t, t_II, t_isStaticElasticCGRA)) {
              int outIndex = -1;
              outIndex = ol->getDirectionID(currentCGRANode);
              // skip the outport as function unit inport, since they are
              // not regarded as bypass links.
              if (outIndex>=4) continue;
              for (CGRALink* il: *inLinks) {
                for (int t_tmp=next_t-t_II; t_tmp<next_t; ++t_tmp) {
                  if (il->isOccupied(t_tmp, t_II, t_isStaticElasticCGRA) and
                      il->isBypass(t_tmp) and
                      il->getMappedDFGNode(t_tmp) == ol->getMappedDFGNode(next_t)) {
                    errs()<<"[cheng] inside roi for CGRA node "<<currentCGRANode->getID()<<"...\n";
                    if (il->getMappedDFGNode(t_tmp) == NULL)
                      errs()<<"[cheng] none..."<<il->getMappedDFGNode(t_tmp)<<"\n";
                    stringDst[outIndex] = to_string(il->getDirectionID(currentCGRANode));//+"; t_tmp: "+to_string(t_tmp)+"; dfg node: " + to_string(il->getMappedDFGNode(t_tmp)->getID());
                  }
                }
              }
            }
          }
          for (int out_index=0; out_index<8; ++out_index) {  
            jsonFile<<"    \"out_"<<to_string(out_index)<<"\"     : \""<<stringDst[out_index]<<"\"";
            if (out_index < 7)
              jsonFile<<",\n";
            else
              jsonFile<<"\n";
          }
          jsonFile<<"  }";
        }
      }
    }
    jsonFile<<"\n]\n";
    jsonFile.close();

    return;
  }
  // TODO: should use nop/constant rather than none/self.
  bool first = true;
  for (int i=0; i<t_cgra->getRows(); ++i) {
    for (int j=0; j<t_cgra->getColumns(); ++j) {
      CGRANode* currentCGRANode = t_cgra->nodes[i][j];
      DFGNode* targetDFGNode = NULL;
      for (DFGNode* dfgNode: t_dfg->nodes) {
        if (m_mapping[dfgNode] == currentCGRANode) {
          targetDFGNode = dfgNode;
          break;
        }
      }
      list<CGRALink*>* inLinks = currentCGRANode->getInLinks();
      list<CGRALink*>* outLinks = currentCGRANode->getOutLinks();
      bool hasInform = false;
      if (targetDFGNode != NULL) {
        hasInform = true;
      } else {
        for (CGRALink* il: *inLinks) {
          if (il->isOccupied(0, t_II, t_isStaticElasticCGRA)) {
            hasInform = true;
            break;
          }
        }
        for (CGRALink* ol: *outLinks) {
          if (ol->isOccupied(0, t_II, t_isStaticElasticCGRA)) {
            hasInform = true;
            break;
          }
        }
      }
      if (!hasInform)
        continue;
      if (first)
        first = false;
      else
        jsonFile<<",\n";

      jsonFile<<"  {\n";
      jsonFile<<"    \"x\"         : "<<j<<",\n";
      jsonFile<<"    \"y\"         : "<<i<<",\n";
      string targetOpt = "none";
      string stringSrc[2];
      stringSrc[0] = "self";
      stringSrc[1] = "self";
      string stringDst[5];
      stringDst[0] = "none";
      stringDst[1] = "none";
      stringDst[2] = "none";
      stringDst[3] = "none";
      stringDst[4] = "none";
      int stringDstIndex = 0;
      if (targetDFGNode != NULL) {
        targetOpt = targetDFGNode->getOpcodeName();
        for (CGRALink* il: *inLinks) {
          if (il->isOccupied(0, t_II, t_isStaticElasticCGRA)
              and !il->isBypass(0)) {
            if (targetDFGNode->isBranch() and
                il->getMappedDFGNode(0)->isCmp()) {
              stringSrc[1] = il->getDirection(currentCGRANode);
            } else if (targetDFGNode->isBranch() and
                !il->getMappedDFGNode(0)->isCmp()) {
              stringSrc[0] = il->getDirection(currentCGRANode);
            } else {
              stringSrc[stringDstIndex++] = il->getDirection(currentCGRANode);
            }
          } else if (il->isOccupied(0, t_II, t_isStaticElasticCGRA) and 
              il->isBypass(0) and
              il->getMappedDFGNode(0)->isPredecessorOf(targetDFGNode)) {
            // This is the case that the data is used in the CGRA node and
            // also bypassed to the next.
            if (targetDFGNode->isBranch() and
                il->getMappedDFGNode(0)->isCmp()) {
              stringSrc[1] = il->getDirection(currentCGRANode);
            } else if (targetDFGNode->isBranch() and
                !il->getMappedDFGNode(0)->isCmp()) {
              stringSrc[0] = il->getDirection(currentCGRANode);
            } else {
              stringSrc[stringDstIndex++] = il->getDirection(currentCGRANode);
            }
          }
          if (stringDstIndex == 2)
            break;
        }
        stringDstIndex = 0;
        for (CGRALink* ir: *outLinks) {
          if (ir->isOccupied(0, t_II, t_isStaticElasticCGRA)
              and ir->getMappedDFGNode(0) == targetDFGNode) {
            stringDst[stringDstIndex++] = ir->getDirection(currentCGRANode);
          }
        }
      }
      DFGNode* bpsDFGNode = NULL;
      map<string, list<string>> stringBpsSrcDstMap;
      for (CGRALink* il: *inLinks) {
        if (il->isOccupied(0, t_II, t_isStaticElasticCGRA)
            and il->isBypass(0)) {
          bpsDFGNode = il->getMappedDFGNode(0);
          list<string> stringBpsDst;
          for (CGRALink* ir: *outLinks) {
            if (ir->isOccupied(0, t_II, t_isStaticElasticCGRA)
                and ir->getMappedDFGNode(0) == bpsDFGNode) {
              stringBpsDst.push_back(ir->getDirection(currentCGRANode));
            }
          }
          stringBpsSrcDstMap[il->getDirection(currentCGRANode)] = stringBpsDst;
        }
      }
      jsonFile<<"    \"op\"        : \""<<targetOpt<<"\",\n";
      if (targetDFGNode!=NULL and targetDFGNode->isBranch()) {
        jsonFile<<"    \"src_data\"  : \""<<stringSrc[0]<<"\",\n";
        jsonFile<<"    \"src_bool\"  : \""<<stringSrc[1]<<"\",\n";
      } else {
        jsonFile<<"    \"src_a\"     : \""<<stringSrc[0]<<"\",\n";
        jsonFile<<"    \"src_b\"     : \""<<stringSrc[1]<<"\",\n";
      }
      // There are multiple outputs.
      if (targetDFGNode!=NULL and targetDFGNode->isBranch()) {
        jsonFile<<"    \"dst_false\"  : [ ";
      } else {
        jsonFile<<"    \"dst\"       : [ ";
      }
      assert(stringDstIndex < 5);
      if (stringDstIndex > 0) {
        jsonFile<<"\""<<stringDst[0]<<"\"";
        for (int i=1; i<stringDstIndex; ++i) {
          jsonFile<<", \""<<stringDst[i]<<"\"";
        }
      }
      jsonFile<<" ],\n";
      if (targetDFGNode!=NULL and targetDFGNode->isBranch()) {
        jsonFile<<"    \"dst_true\" : \"self\",\n";
      }
      int bpsIndex = 0;
      for (map<string,list<string>>::iterator iter=stringBpsSrcDstMap.begin();
          iter!=stringBpsSrcDstMap.end(); ++iter) {
        jsonFile<<"    \"bps_src"<<bpsIndex<<"\"  : \""<<(*iter).first<<"\",\n";
        // There are multiple bypass outputs.
        jsonFile<<"    \"bps_dst"<<bpsIndex<<"\"  : [ ";
        bool firstBpsDst = true;
        for (string bpsDst: (*iter).second) {
          if (firstBpsDst)
            firstBpsDst = false;
          else
            jsonFile<<",";
          jsonFile<<"\""<<bpsDst<<"\"";
        }
        jsonFile<<" ],\n";
        ++bpsIndex;
      }
      jsonFile<<"    \"dvfs\"      : "<<"\"nominal\""<<"\n";
      jsonFile<<"  }";
    }
  }
  jsonFile<<"\n]\n";
  jsonFile.close();
}

// TODO: Assume that the arriving data can stay inside the input buffer.
// TODO: Should traverse from dst to src?
// TODO: Should consider the unmapped predecessors.
// TODO: Should consider the type of CGRA, say, a static in-elastic CGRA should
//       join at the same successor at exact same cycle without pending.
bool Mapper::tryToRoute(CGRA* t_cgra, DFG* t_dfg, int t_II,
    DFGNode* t_srcDFGNode, CGRANode* t_srcCGRANode, CGRANode* t_dstCGRANode,
    int t_dstCycle, bool t_isBackedge, bool t_isStaticElasticCGRA) {
  errs()<<"[cheng] tryToRoute -- srcDFGNode: "<<t_srcDFGNode->getID()<<" srcCGRANode: "<<t_srcCGRANode->getID()<<" dstCGRANode: "<<t_dstCGRANode->getID()<<"\n";
  list<CGRANode*> searchPool;
  map<CGRANode*, int> distance;
  map<CGRANode*, int> timing;
  map<CGRANode*, CGRANode*> previous;
  timing[t_srcCGRANode] = m_mappingTiming[t_srcDFGNode];
  for (int i=0; i<t_cgra->getRows(); ++i) {
    for (int j=0; j<t_cgra->getColumns(); ++j) {
      CGRANode* node = t_cgra->nodes[i][j];
      distance[node] = m_maxMappingCycle;
      timing[node] = timing[t_srcCGRANode];
      // TODO: should also consider the xbar here?
//      if (!cgra->nodes[i][j]->canOccupyFU(timing[node])) {
//        int temp_cycle = timing[node];
//        timing[node] = m_maxMappingCycle;
//        while (temp_cycle < m_maxMappingCycle) {
//          if (cgra->nodes[i][j]->canOccupyFU(temp_cycle)) {
//            timing[node] = temp_cycle;
//            break;
//          }
//          ++temp_cycle;
//        }
//      }
      previous[node] = NULL;
      searchPool.push_back(t_cgra->nodes[i][j]);
    }
  }
  distance[t_srcCGRANode] = 0;
  while (searchPool.size()!=0) {
    int minCost = m_maxMappingCycle + 1;
    CGRANode* minNode;
    for (CGRANode* currentNode: searchPool) {
      if (distance[currentNode] < minCost) {
        minCost = distance[currentNode];
        minNode = currentNode;
      }
    }
    searchPool.remove(minNode);
    // found the target point in the shortest path
    if (minNode == t_dstCGRANode) {
      if (previous[minNode] == NULL)
      break;
    }
    list<CGRANode*>* currentNeighbors = minNode->getNeighbors();

    for (CGRANode* neighbor: *currentNeighbors) {
      int cycle = timing[minNode];
      while (1) {
        CGRALink* currentLink = minNode->getOutLink(neighbor);
        // TODO: should also consider the cost of the register file
        if (currentLink->canOccupy(t_srcDFGNode, cycle, t_II)) {
          // rough estimate the cost based on the suspend cycle
          int cost = distance[minNode] + (cycle - timing[minNode]) + 1;
          if (cost < distance[neighbor]) {
            distance[neighbor] = cost;
            timing[neighbor] = cycle + 1;
            previous[neighbor] = minNode;
          }
          break;
        }
        ++cycle;
        if(cycle > m_maxMappingCycle)
          break;
      }
    }
  }

  // Construct the shortest path for routing.
  map<CGRANode*, int> path;
  CGRANode* u = t_dstCGRANode;
  if (previous[u] != NULL or u == t_srcCGRANode) {
    while (u != NULL) {
      path[u] = timing[u];
      u = previous[u];
    }
  } else {
    return false;
  }

  // Not a valid mapping if it exceeds the 'm_maxMappingCycle'.
  if(timing[t_dstCGRANode] > m_maxMappingCycle or
     timing[t_dstCGRANode] - timing[t_srcCGRANode] > t_II) {
// or
//    }
    return false;
  }

//  errs()<<"[CHENG] believes this is correct or wrong... timing[t_dstCGRANode]: "<<timing[t_dstCGRANode]<<" t_dstCycle: "<<t_dstCycle<<"\n";

//  if (timing[t_dstCGRANode] > t_dstCycle) {
//    if (timing[t_dstCGRANode] > t_dstCycle + t_II) {
//      for (map<CGRANode*,int>::iterator iter = path.begin();
//          iter!=path.end(); ++iter) {
//        errs()<<"[tan] the failed path -- cycle: "<<(*iter).second<<" CGRANode: "<<(*iter).first->getID()<<"\n";
//      }
//      return false;
//    }
//  }

//  if (timing[t_dstCGRANode]%t_II >= t_dstCycle%t_II)
  // Try to route the data flow.
  map<int, CGRANode*>* reorderPath = getReorderPath(&path);
//  //Since the cycle on path increases gradually, re-order will not miss anything.
//  for(map<CGRANode*, int>::iterator iter=path.begin(); iter!=path.end(); ++iter) {
//    reorderPath[(*iter).second] = (*iter).first;
//  }
//  assert(reorderPath.size() == path.size());

  map<int, CGRANode*>::iterator previousIter;
  map<int, CGRANode*>::reverse_iterator riter = reorderPath->rbegin();
  errs()<<"[cheng] check route size: "<<reorderPath->size()<<"\n";
  if (reorderPath->size() == 1) {
    int duration = (t_II+(t_dstCycle-(*riter).first)%t_II)%t_II;
    errs()<<"[cheng] allocate for local reg maintain... duration="<<duration<<" last cycle: "<<(*riter).first<<"\n";
    (*riter).second->allocateReg(4, (*riter).first, duration, t_II);
  }
  for (map<int, CGRANode*>::iterator iter = reorderPath->begin();
      iter!=reorderPath->end(); ++iter) {
    if (iter != reorderPath->begin()) {
      CGRALink* l = t_cgra->getLink((*previousIter).second, (*iter).second);
      bool isBypass = false;
      int duration = ((*iter).first-(*previousIter).first)%t_II;
      if ((*riter).second != (*iter).second and
          (*previousIter).first+1 == (*iter).first)
        isBypass = true;
      else {
        duration = (t_II+(t_dstCycle-(*previousIter).first)%t_II)%t_II;
        errs()<<"[cheng] reset duration: "<<duration<<" t_dstCycle: "<<t_dstCycle<<" previous: "<<(*previousIter).first<<" II: "<<t_II<<"\n";
      }
      if (duration == 0) {
        duration = t_II;
      }
      l->occupy(t_srcDFGNode, (*previousIter).first,
                duration, t_II, isBypass, t_isStaticElasticCGRA);
    }
    previousIter = iter;
  }

  map<int, CGRANode*>::iterator begin = reorderPath->begin();
  map<int, CGRANode*>::reverse_iterator end = reorderPath->rbegin();

  // Check whether the backward data can be delivered within II.
  if (!t_isStaticElasticCGRA) {
    if (t_isBackedge and (*end).first - (*begin).first >= t_II) {
      return false;
    }
  }
  return true;
}

int Mapper::heuristicMap(CGRA* t_cgra, DFG* t_dfg, int t_II,
    bool t_isStaticElasticCGRA) {
  bool fail = false;
  while (1) {
    errs()<<"----------------------------------------\n";
    errs()<<"DEBUG start heuristic algorithm with II="<<t_II<<"\n";
    int cycle = 0;
    constructMRRG(t_dfg, t_cgra, t_II);
    fail = false;
    for (list<DFGNode*>::iterator dfgNode=t_dfg->nodes.begin();
        dfgNode!=t_dfg->nodes.end(); ++dfgNode) {
      list<map<CGRANode*, int>*> paths;
      for (int i=0; i<t_cgra->getRows(); ++i) {
        for (int j=0; j<t_cgra->getColumns(); ++j) {
          CGRANode* fu = t_cgra->nodes[i][j];
//          errs()<<"DEBUG cgrapass: dfg node: "<<*(*dfgNode)->getInst()<<",["<<i<<"]["<<j<<"]\n";
          map<CGRANode*, int>* tempPath =
              calculateCost(t_cgra, t_dfg, t_II, *dfgNode, fu);
          if(tempPath != NULL and tempPath->size() != 0) {
            paths.push_back(tempPath);
          }
            else
              errs()<<"DEBUG no available path for DFG node "<<(*dfgNode)->getID()
                  <<" on CGRA node "<<fu->getID()<<" within II "<<t_II<<"; path size: "<<paths.size()<<".\n";
        }
      }
      // Found some potential mappings.
      if (paths.size() != 0) {
        map<CGRANode*, int>* optimalPath =
            getPathWithMinCostAndConstraints(t_cgra, t_dfg, t_II, *dfgNode, &paths);
        if (optimalPath->size() != 0) {
          if (!schedule(t_cgra, t_dfg, t_II, *dfgNode, optimalPath,
              t_isStaticElasticCGRA)) {
            errs()<<"DEBUG fail1 in schedule() II: "<<t_II<<"\n";
            for (map<CGRANode*,int>::iterator iter = optimalPath->begin();
                iter!=optimalPath->end(); ++iter) {
              errs()<<"[tan] the failed path -- cycle: "<<(*iter).second<<" CGRANode: "<<(*iter).first->getID()<<"\n";
            }

            fail = true;
            break;
          }
          errs()<<"DEBUG success in schedule()\n";
        } else {
          errs()<<"DEBUG fail2 in schedule() II: "<<t_II<<"\n";
          fail = true;
          break;
        }
      } else {
        fail = true;
        errs()<<"DEBUG [else] no available path for DFG node "<<(*dfgNode)->getID()
            <<" within II "<<t_II<<".\n";
        break;
      }
    }
    if (!fail)
      break;
    else if (t_isStaticElasticCGRA) {
      break;
    }
    ++t_II;
  }
  if (!fail)
    return t_II;
  else
    return -1;
}

int Mapper::exhaustiveMap(CGRA* t_cgra, DFG* t_dfg, int t_II,
    bool t_isStaticElasticCGRA) {
  list<map<CGRANode*, int>*>* exhaustivePaths = new list<map<CGRANode*, int>*>();
  list<DFGNode*>* mappedDFGNodes = new list<DFGNode*>();
  bool success = DFSMap(t_cgra, t_dfg, t_II, mappedDFGNodes,
      exhaustivePaths, t_isStaticElasticCGRA);
  if (success)
    return t_II;
  else
    return -1;
}

bool Mapper::DFSMap(CGRA* t_cgra, DFG* t_dfg, int t_II,
    list<DFGNode*>* t_mappedDFGNodes,
    list<map<CGRANode*, int>*>* t_exhaustivePaths,
    bool t_isStaticElasticCGRA) {
//  , DFGNode* t_badMappedDFGNode) {

//  list<map<CGRANode*, int>*>* exhaustivePaths = t_exhaustivePaths;

  constructMRRG(t_dfg, t_cgra, t_II);

//  list<DFGNode*> dfgNodeSearchPool;
//  for (list<DFGNode*>::iterator dfgNodeItr=dfg->nodes.begin();
//      dfgNodeItr!=dfg->nodes.end(); ++dfgNodeItr) {
//    dfgNodeSearchPool.push_back(*dfgNodeItr);
//  }

  list<DFGNode*>::iterator mappedDFGNodeItr = t_mappedDFGNodes->begin();
  list<DFGNode*>::iterator dfgNodeItr = t_dfg->getDFSOrderedNodes()->begin();
//  errs()<<"----copying previous schedule in exhaustive----\n";
  for (map<CGRANode*, int>* path: *t_exhaustivePaths) {
//    errs()<<"----copying previous schedule in exhaustive---- targetDFGNode: "<<(*mappedDFGNodeItr)->getID()<<"\n";
    if (!schedule(t_cgra, t_dfg, t_II, *mappedDFGNodeItr, path,
        t_isStaticElasticCGRA)) {
      errs()<<"DEBUG <this is impossible> fail3 in DFS() II: "<<t_II<<"\n";
      assert(0);
      break;
    }
    ++mappedDFGNodeItr;
//    dfgNodeSearchPool.remove(*dfgNodeItr);
    ++dfgNodeItr;
  }
//  if (dfgNodeSearchPool.size() == 0) {
  if (dfgNodeItr == t_dfg->getDFSOrderedNodes()->end())
    return true;
//  }

  DFGNode* targetDFGNode = *dfgNodeItr;

//  errs()<<"DEBUG just now finished the previous path copying...\n";
//  for (list<DFGNode*>::iterator dfgNodeItr=dfgNodeSearchPool.begin();
//      dfgNodeItr!=dfgNodeSearchPool.end(); ++dfgNodeItr) {
  list<map<CGRANode*, int>*> paths;
  for (int i=0; i<t_cgra->getRows(); ++i) {
    for (int j=0; j<t_cgra->getColumns(); ++j) {
      CGRANode* fu = t_cgra->nodes[i][j];
      map<CGRANode*, int>* tempPath =
          calculateCost(t_cgra, t_dfg, t_II, targetDFGNode, fu);
      if(tempPath != NULL and tempPath->size() != 0) {
        paths.push_back(tempPath);
      }
    }
  }

  list<map<CGRANode*, int>*>* potentialPaths =
      getOrderedPotentialPaths(t_cgra, t_dfg, t_II, targetDFGNode, &paths);
  bool success = false;
//  errs()<<"----try to schedule in exhaustive---- targetDFGNode: "<<targetDFGNode->getID()<<"\n";
  while (potentialPaths->size() != 0) {
    map<CGRANode*, int>* currentPath = potentialPaths->front();
    potentialPaths->pop_front();
    assert(currentPath->size() != 0);
//    errs()<<"----try to schedule in exhaustive---- targetDFGNode: "<<targetDFGNode->getID()<<"\n";
    if (schedule(t_cgra, t_dfg, t_II, targetDFGNode, currentPath,
        t_isStaticElasticCGRA)) {
      t_exhaustivePaths->push_back(currentPath);
      t_mappedDFGNodes->push_back(targetDFGNode);
//      errs()<<"--- success in mapping target DFG node: "<<targetDFGNode->getID()<<"\n";
      success = DFSMap(t_cgra, t_dfg, t_II, t_mappedDFGNodes,
          t_exhaustivePaths, t_isStaticElasticCGRA);
      if (success)
        return true;
    }
    // If the schedule fails and need to try the other schedule,
    // should re-construct m_mapping and m_mappingTiming.
    constructMRRG(t_dfg, t_cgra, t_II);
    list<DFGNode*>::iterator mappedDFGNodeItr = t_mappedDFGNodes->begin();
//    errs()<<"-- second copying previous schedule in while --\n";
    for (map<CGRANode*, int>* path: *t_exhaustivePaths) {
      if (!schedule(t_cgra, t_dfg, t_II, *mappedDFGNodeItr, path,
          t_isStaticElasticCGRA)) {
        errs()<<"DEBUG <this is impossible> fail7 in DFS() II: "<<t_II<<"\n";
        assert(0);
        break;
      }
      ++mappedDFGNodeItr;
    }
  }
  if (t_exhaustivePaths->size() != 0) {
    errs()<<"======= go backward one step ======== popped DFG node ["<<t_mappedDFGNodes->back()->getID()<<"] from CGRA node ["<<m_mapping[t_mappedDFGNodes->back()]->getID()<<"]\n";
    t_mappedDFGNodes->pop_back();
    t_exhaustivePaths->pop_back();
//    m_exit++;
//    if (m_exit == 2)
//      exit(0);
  }
  delete potentialPaths;
  return false;
}

// This helper function assume the cycle for each mapped CGRANode increases
// gradually along the path. Otherwise, the map struct will get conflict key.
map<int, CGRANode*>* Mapper::getReorderPath(map<CGRANode*, int>* t_path) {
  map<int, CGRANode*>* reorderPath = new map<int, CGRANode*>();
  for (map<CGRANode*, int>::iterator iter=t_path->begin();
      iter!=t_path->end(); ++iter) {
    assert(reorderPath->find((*iter).second) == reorderPath->end());
    (*reorderPath)[(*iter).second] = (*iter).first;
  }
  assert(reorderPath->size() == t_path->size());
  return reorderPath;
}

