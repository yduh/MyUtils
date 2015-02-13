import ROOT
ROOT.gROOT.SetBatch(True)
#ROOT.PyConfig.IgnoreCommandLineOptions = True

from CMGTools.RootTools.statistics.Tree import Tree

#### ========= EDM/FRAMEWORK =======================
class Event:
    def __init__(self,tree,entry):
        self._tree = tree
        self._entry = entry
        self._sync()
        self._isEval = False
    def _sync(self):
        if self._tree.entry != self._entry:
            self._tree.GetEntry(self._entry)
            self._tree.entry = self._entry
    def __getattr__(self,name):
        if name in self.__dict__: return self.__dict__[name]
        if name == "metLD": return self._tree.met*0.00397 + self._tree.mhtJet25*0.00265
        self._sync()
        if "(" in name:
            self._isEval = True
            ret = eval(name, globals(), self)
            self._isEval = False
            return ret
        if self._isEval:
            import math
            if hasattr(self._tree,name): return getattr(self._tree,name)
            if hasattr(math, name): return getattr(math,name)
            if hasattr(__builtins__,name): return getattr(__builtins__,name)
            return getattr(ROOT,name)
        return getattr(self._tree,name)
    def __getitem__(self,attr):
        return self.__getattr__(attr)
    def eval(self,expr):
        if not hasattr(self._tree, '_exprs'):
            self._tree._exprs = {}
            # remove useless warning about EvalInstance()
            import warnings
            warnings.filterwarnings(action='ignore', category=RuntimeWarning, 
                                    message='creating converter for unknown type "const char\*\*"$')
        if expr not in self._tree._exprs:
            self._tree._exprs[expr] = ROOT.TTreeFormula(expr,expr,self._tree)
            # force sync, to be safe
            self._tree.GetEntry(self._entry)
            self._tree.entry = self._entry
        else:
            self._sync()
        return self._tree._exprs[expr].EvalInstance()
            

class Object:
    def __init__(self,event,prefix,index=None):
        self._event = event
        self._prefix = prefix+"_"
        self._index = index
    def __getattr__(self,name):
        if name in self.__dict__: return self.__dict__[name]
        if name == "pdgLabel": return self.pdgLabel_()
        val = getattr(self._event,self._prefix+name)
        if self._index != None:
            val = val[self._index]
        self.__dict__[name] = val ## cache
        return val
    def __getitem__(self,attr):
        return self.__getattr__(attr)
    def pdgLabel_(self):
        if self.pdgId == +13: return "#mu-";
        if self.pdgId == -13: return "#mu+";
        if self.pdgId == +11: return "e-";
        if self.pdgId == -11: return "e+";
    def p4(self):
        ret = ROOT.TLorentzVector()
        ret.SetPtEtaPhiM(self.pt,self.eta,self.phi,self.mass)
        return ret
    def subObj(self,prefix):
        return Object(self,self._event,self._prefix+prefix)

class Collection:
    def __init__(self,event,prefix,len=None,maxlen=None,testVar="pt"):
        self._event = event
        self._prefix = prefix
        self._testVar = testVar
	self._vector = hasattr(event,"n"+prefix)
        if len != None:
            self._len = getattr(event,len)
            if maxlen and self._len > maxlen: self._len = maxlen
        elif self._vector:
            self._len = getattr(event,"n"+prefix)
            if maxlen and self._len > maxlen: self._len = maxlen
        elif testVar != None:
            self._len = None
        else:
            raise RuntimeError, "must provide either len or testVar"
        self._cache = {}
    def __getitem__(self,index):
        if type(index) == int and index in self._cache: return self._cache[index]
        if self._testVar != None and self._len == None: self._countMe()
        if index >= self._len: raise IndexError, "Invalid index %r (len is %r) at %s" % (index,self._len,self._prefix)
        if self._vector:
            ret = Object(self._event,self._prefix,index=index)
        else: 
            ret = Object(self._event,"%s%d" % (self._prefix,index+1))
            print "%s%d" % (self._prefix,index+1)
        if type(index) == int: self._cache[index] = ret
        return ret
    def __len__(self):
        if self._testVar != None and self._len == None: self._countMe()
        return self._len
    def _countMe(self):
        n = 0; ok = True
        while ok:
            try:
                val = getattr(self._event,"%s%d_%s" % (self._prefix,n+1,self._testVar))
		print val
                ok = (val > -98) 
                if ok: n += 1
            except:
                ok = False
        self._len = n
class Module:
    def __init__(self,name,booker=None):
        self._name = name
        self._booker = booker
        self._parName = name
        self._bookerList = {}
        self._bookerList[name] = booker
    def mkdir(self,name,change=True):
        assert self._parName+"/"+name not in self._bookerList.keys()
        self._bookerList[self._parName+"/"+name] = self._booker.mkdir(name) if self._booker != None else None
        if change:
            self._booker = self._bookerList[self._parName+"/"+name]
            self._parName = self._parName+"/"+name
        pass
    def chdir(self,name,absName = False):
        if absName:
            assert name in self._bookerList.keys()
            self._booker = self._bookerList[name]
            self._parName = name
        else:
            assert self._parName+"/"+name in self._bookerList.keys()
            self._booker = self._bookerList[self._parName+"/"+name]
            self._parName = self._parName + "/" + name
        pass
    def home(self):
        self._parName = self._name
        self._booker = self._bookerList[self._name]

    def beginJob(self):
        pass
    def endJob(self):
        pass
    def analyze(self,event,key=None):
        pass
    def booker(self):
	return self._booker
    def book(self,what,name,*args):
        return self._booker.book(what,name,*args)
    def bookTree(self,name):
        return self._booker.bookTree(name)

class EventLoop:
    def __init__(self,modules):
        self._modules = modules
    def loop(self,trees,maxEvents=-1,cut=None,eventRange=None):
        modules = self._modules
        if type(trees) != dict:
            for m in modules: m.beginJob()
            if type(trees) != list: trees = [ trees ]
            for tree in trees:
                tree.entry = -1
                for i in xrange(tree.GetEntries()) if eventRange == None else eventRange:
                     if maxEvents > 0 and i >= maxEvents-1: break
                     e = Event(tree,i)
                     if cut != None and not e.eval(cut): 
                         continue
                     ret = True
                     for m in modules: 
                         ret = m.analyze(e)
                         if ret == False: break
                     if i > 0 and i % 10000 == 0:
                         print "Processed %8d/%8d entries of this tree" % (i,tree.GetEntries())
        else:
                keys = [key for key in trees]
                for m in modules: m.beginJob(keys)
                for key,tree in trees.iteritems():
                    tree.entry = -1
                    for i in xrange(tree.GetEntries()) if eventRange == None else eventRange:
                        if maxEvents > 0 and i >= maxEvents-1: break
                        e = Event(tree,i)
                        if cut != None and not e.eval(cut): 
                            continue
                        ret = True
                        for m in modules: 
                            ret = m.analyze(e,key)
                            if ret == False: break
                        if i > 0 and i % 10000 == 0:
                            print "Processed %8d/%8d entries of this tree" % (i,tree.GetEntries())
        for m in modules: m.endJob()

#### ========= NTUPLING AND HISTOGRAMMING =======================
class PyTree:
    def __init__(self,tree):
        self.tree = tree
        self._branches = {} ## must be the last line
    def branch(self,name,type,n=1,lenVar=None):
        arr = array(type.lower(), n*[0 if type in 'iI' else 0.]) 
        self._branches[name] = arr
        if n == 1:
            self.tree.Branch(name, arr, name+"/"+type.upper())
        else:
            if lenVar != None:
                self.tree.Branch(name, arr, "%s[%s]/%s" % (name,lenVar,type.upper()))
            else:
                self.tree.Branch(name, arr, "%s[%d]/%s" % (name,n,type.upper()))
    def __setattr__(self,name,val):
        if hasattr(self,'_branches'):
            arr = self._branches[name]
            if len(arr) == 1:
                arr[0] = val
            else:
                for i,v in enumerate(val):
                    if i >= len(arr): break
                    arr[i]  = v
        else:
            self.__dict__[name] = val
    def fill(self):
        self.tree.Fill()

class BookDir:
    def __init__(self,tdir):
        self.tdir    = tdir
        self._objects = {}
        self._subs = []
    def mkdir(self,name):
        ret = BookDir(self.tdir.mkdir(name))
        self._subs.append(ret)
        return ret
    def book(self,what,name,*args):
        gdir = ROOT.gDirectory
        self.tdir.cd()
        obj = getattr(ROOT,what)(name,*args)
        self._objects[name] = obj
        gdir.cd()
        return obj
    def bookTree(self,name):
        gdir = ROOT.gDirectory
        self.tdir.cd()
	userTree = Tree(name,name)
        self._objects[userTree.ttree.GetName()] = userTree.ttree
        gdir.cd()
        return userTree
    def objects(self):
	return self._objects
    def subs(self):
	return self._subs
    def done(self):
        for s in self._subs: s.done()
        for k,v in self._objects.iteritems():
            self.tdir.WriteTObject(v)

class Booker(BookDir):
    def __init__(self,fileName):
        BookDir.__init__(self,ROOT.TFile(fileName,"RECREATE"))
    def done(self):
        BookDir.done(self)
        self.tdir.Close()
