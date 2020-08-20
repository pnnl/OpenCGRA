/*
 * ======================================================================
 * CGRALink.h
 * ======================================================================
 * CGRA link implementation header file.
 *
 * Author : Cheng Tan
 *   Date : July 16, 2019
 */

#ifndef CGRALink_H
#define CGRALink_H

//#include <llvm/Support/raw_ostream.h>
//#include <llvm/Support/FileSystem.h>

#include "CGRANode.h"
#include "DFGNode.h"

//using namespace llvm;
using namespace std;

class CGRANode;

class CGRALink
{
  private:
    int m_id;
    CGRANode *m_src;
    CGRANode *m_dst;
    int m_II;
    int m_ctrlMemSize;
    int m_bypassConstraint;
    int m_currentCtrlMemItems;

    int m_cycleBoundary;
    bool* m_occupied;
    bool* m_bypassed;
    bool* m_arrived;
    DFGNode** m_dfgNodes;
    bool satisfyBypassConstraint(int, int);

  public:
    CGRALink(int);
    void setID(int);
    int getID();
    CGRANode*  getSrc();
    CGRANode*  getDst();
    void connect(CGRANode*, CGRANode*);
    CGRANode* getConnectedNode(CGRANode*);

    void constructMRRG(int, int);
    bool canOccupy(int, int);
    bool isOccupied(int);
    bool isOccupied(int, int, bool);
    bool canOccupy(DFGNode*, int, int);
    void occupy(DFGNode*, int, int, int, bool, bool);
    bool isBypass(int);
    string getDirection(CGRANode*);
    int getDirectionID(CGRANode*);
    bool isReused(int);
    DFGNode* getMappedDFGNode(int);
    void setCtrlMemConstraint(int);
    void setBypassConstraint(int);
    int getBypassConstraint();
};

#endif
