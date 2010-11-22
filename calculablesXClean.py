from wrappedChain import *
import copy,bisect
import ROOT as r
##############################
class xcJet(wrappedChain.calculable) :
    def name(self) : return "%sCorrectedP4%s"%self.xcjets

    def __init__(self,xcjets = None, applyResidualCorrectionsToData = None,
                 gamma    = None, gammaDR    = 0,
                 electron = None, electronDR = 0,
                 muon     = None, muonDR     = 0,
                 correctForMuons = None,
                 jesAbs = 1,
                 jesRel = 0 ) :
        self.value = r.std.vector('LorentzV')()
        self.jetP4Source = ("%sCorrectedP4%s"%xcjets)[2:]

        for item in ["xcjets", "applyResidualCorrectionsToData", "correctForMuons", "jesAbs", "jesRel"] :
            setattr(self, item, eval(item))

        self.other = dict( [ (i,(eval(i),eval(i+"DR"))) for i in ["gamma","electron","muon"]] )
        self.resCorr = ("%sResidualCorrectionsFromFile%s"%self.xcjets)
        self.moreName = "; ".join(["%s%sDR<%.2f"%(v[0]+(v[1],)) for v in filter(lambda v: v[0], self.other.values())])
        if jesAbs!=1.0 or jesRel!=0.0:
            self.moreName2 += "jes corr: %.2f*(1+%.2f|eta|)"%(jesAbs,jesRel)

    def resFactor(self, isData, p4) :
        if self.applyResidualCorrectionsToData and isData :
            index = bisect.bisect(self.source[self.resCorr]["etaLo"], p4.eta())-1
            if index<0 : index = 0
            resFactor = self.source[self.resCorr]["factor"][index]
            return resFactor
        else :
            return 1.0
        
    def jes(self, isData, p4) : return p4 * self.jesAbs*(1+self.jesRel*abs(p4.eta())) * self.resFactor(isData, p4)

    def update(self,ignored) :
        jetP4s = self.source[self.jetP4Source]
        killed = self.source["%sIndicesKilled%s"%self.xcjets]
        matchedMuons = []

        isData = self.source["isRealData"]
        self.value.clear()
        for iJet in range(len(jetP4s)) :
            self.value.push_back(self.jes(isData, jetP4s[iJet]))
            
            if self.matchesIn("gamma",self.value[iJet]) \
            or self.matchesIn("electron",self.value[iJet]) :
                killed.add(iJet)
                continue

            for p4 in self.matchesIn("muon",self.value[iJet], exitEarly=False, indicesStr="%sIndicesNonIso%s") :
                matchedMuons.append(p4)
                if self.correctForMuons: self.value[iJet] += p4

        if self.other["muon"][0] :
            nonisomu = self.source["%sIndicesNonIso%s"%self.other["muon"][0]]
            self.source["crock"]["%s%sNonIsoMuonsUniquelyMatched"%self.xcjets]= (len(set(matchedMuons)) == len(nonisomu) == len(matchedMuons))

    def matchesIn(self,label,p4, exitEarly = True, indicesStr = "%sIndices%s") :
        collection,dR = self.other[label]
        if not collection : return False
        indices = self.source[indicesStr % collection]
        objects = self.source["%sP4%s"%collection]
        matches = []
        for i in indices :
            objP4 = objects.at(i)
            if dR > r.Math.VectorUtil.DeltaR(objP4,p4) :
                if exitEarly: return True
                else: matches.append(objP4)
        return matches
##############################
class IndicesUnmatched(wrappedChain.calculable) :
    def __init__(self, collection = None, xcjets=None, DR = 0) :
        self.fixes = collection
        self.stash(["P4","IndicesOther"])
        self.compareJets = ("%sCorrectedP4%s"%xcjets)[2:]
        self.moreName = "%sIndicesOther%s; no dR<%.1f match in %s"%(collection+(DR,self.compareJets))
        for item in ["collection","DR"]: setattr(self,item,eval(item))

    def noJetMatch(self, i) :
        p4 = self.source[self.P4].at(i)
        for jet in self.source[self.compareJets]:
            if self.DR > r.Math.VectorUtil.DeltaR(p4,jet) :
                return False
        return True
        
    def update(self,ignored) :
        self.value = filter(self.noJetMatch, self.source[self.IndicesOther])
##############################
