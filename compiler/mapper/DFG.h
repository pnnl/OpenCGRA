/*
 * ======================================================================
 * DFG.cpp
 * ======================================================================
 * DFG implementation header file.
 *
 * Author : Cheng Tan
 *   Date : July 16, 2019
 */

#include <llvm/IR/Function.h>
#include <llvm/IR/BasicBlock.h>
#include <llvm/IR/Value.h>
#include <llvm/IR/Instruction.h>
#include <llvm/IR/Instructions.h>
#include <llvm/Support/raw_ostream.h>
#include <llvm/Support/FileSystem.h>
#include <llvm/IR/Use.h>
#include <llvm/Analysis/CFG.h>
#include <llvm/Analysis/LoopInfo.h>
#include <list>

#include "DFGNode.h"
#include "DFGEdge.h"

using namespace llvm;
using namespace std;

class DFG {
  private:
    int m_num;
    list<DFGNode*>* m_orderedNodes;
    list<Loop*>* m_targetLoops;

    //edges of data flow
    list<DFGEdge*> m_DFGEdges;
    list<DFGEdge*> m_ctrlEdges;

    string changeIns2Str(Instruction* ins);
    //get value's name or inst's content
    StringRef getValueName(Value* v);
    void DFS_on_DFG(DFGNode*, DFGNode*, list<DFGEdge*>*,
        list<DFGEdge*>*, list<list<DFGEdge*>*>*);
    DFGNode* getNode(Value*);
    bool hasNode(Value*);
    DFGEdge* getDFGEdge(DFGNode*, DFGNode*);
    void deleteDFGEdge(DFGNode*, DFGNode*);
    void replaceDFGEdge(DFGNode*, DFGNode*, DFGNode*, DFGNode*);
    bool hasDFGEdge(DFGNode*, DFGNode*);
    DFGEdge* getCtrlEdge(DFGNode*, DFGNode*);
    bool hasCtrlEdge(DFGNode*, DFGNode*);
    bool shouldIgnore(Instruction*);
    void tuneForBranch();
    void tuneForBitcast();
    void tuneForLoad();
    void tuneForPattern();
    void combineCmpBranch();
    void combineMulAdd();
    void combinePhiAdd();
    void combine(string, string);
    void trimForStandalone();
    void detectMemDataDependency();
    void eliminateOpcode(string);
    bool searchDFS(DFGNode*, DFGNode*, list<DFGNode*>*);
    void connectDFGNodes();

  public:
    DFG(Function&, list<Loop*>*, bool);
    //initial ordering of insts
    list<DFGNode*> nodes;

    list<DFGNode*>* getBFSOrderedNodes();
    list<DFGNode*>* getDFSOrderedNodes();
    int getNodeCount();
    void construct(Function&);
    list<list<DFGEdge*>*>* getCycles();
    int getID(DFGNode*);
    bool isLoad(DFGNode*);
    bool isStore(DFGNode*);
    void showOpcodeDistribution();
    void generateDot(Function&, bool);
    void generateJSON();
};
