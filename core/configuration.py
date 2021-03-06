import os,socket

def ttreecacheMB() : return 20
def trace() : return True
def nCoresDefault() : return 4
def useCachedFileLists() : return True
def maxArrayLength() : return 256
def computeEntriesForReport() : return False
def printNodesUsed() : return False
def fakeString() : return ";FAKE"
def stepsToDisableForData() : return ["genMotherHistogrammer", "photonPurityPlots", "photonEfficiencyPlots"]
def stepsToDisableForMc() : return ["l1Filter", "hltFilter", "hltFilterList", "lowestUnPrescaledTriggerFilter", "lowestUnPrescaledTriggerHistogrammer", "hbheNoiseFilter", "bxFilter", "physicsDeclaredFilter", "techBitFilter", "hbheNoise"]
def histogramsToDisableForData() : return ["^gen"]
def histogramsToDisableForMc() : return []
def cppFiles() : return ["cpp/linkdef.cxx"]

def detectorSpecs() :
    return {
        "cms": {"etaBE": 1.479, #from CMS PAS EGM-10-005
                "barrelEtaMax": 1.4442,
                "endcapEtaMin": 1.560,
                "CaloSubdetectors": ["Eb", "Ee", "Hbhe", "Hf"],
                "PFSubdetectors": ["Ecal", "Hcal", "Hfem", "Hfhad", "Ps"],
                "CaloRecHitCollections": [""],
                "PFRecHitCollections": ["","cluster"],
                },
        }

def sitePrefix() :
    d = {"hep.ph.ic.ac.uk":"ic",
         "sesame1":"pu",
         "cern.ch":"cern",
         "fnal.gov":"fnal",
         }
    hostName = socket.gethostname()
    for match,prefix in d.iteritems() :
        if match in hostName : return prefix
    return "other"

def siteSpecs() :
    user = os.environ["USER"]
    return {
        "ic"  :{"localOutputDir" : "/vols/cms02/%s/tmp/"%user,
                "globalOutputDir": "/vols/cms02/%s/tmp/"%user,
                #"dCachePrefix"   : "dcap://gfe02.grid.hep.ph.ic.ac.uk",
                #"dCacheTrim"     : "",
                "dCachePrefix"   : "root://gfe02.grid.hep.ph.ic.ac.uk",
                "dCacheTrim"     : "/pnfs/hep.ph.ic.ac.uk/data/cms",
                "srmPrefix"      : "srm://gfe02.grid.hep.ph.ic.ac.uk:8443/srm/managerv2?SFN=/pnfs/hep.ph.ic.ac.uk/data/cms/store/user",
                "queueHeaders"   : ["job-ID", "prior", "name", "user", "state", "submit1", "submit2", "queue", "slots", "ja-task-ID"],
                "queueVars"      : {"queue":"queue", "user":"user", "state":"state", "run":"r", "summary":"qstat -u '*'", "sample":"qstat | head"},
                "CMSSW_lumi"     : "/vols/sl5_exp_software/cms/slc5_ia32_gcc434/cms/cmssw/CMSSW_3_8_7/src/",
                },
        "pu"  :{"localOutputDir" : "/tmp/%s"%user,
                "globalOutputDir": "/tigress-hsm/%s/tmp/"%user,
                "dCachePrefix"   : "",
                "dCacheTrim"     : "",
                "srmPrefix"      : "",
                "queueHeaders"   : ["Job id","Name","User","Time Use","S","Queue"],
                "queueVars"      : {"queueName":"hep", "queue": "Queue", "user":"User", "state":"S", "run":"R", "summary":"qstat", "sample": "qstat -u %s | head"%user},
                "CMSSW_lumi"     : None,
                },
        "cern":{"localOutputDir" : "/tmp/%s"%user,
                "globalOutputDir": "/tmp/%s"%user,
                "dCachePrefix"   : "",
                "dCacheTrim"     : "",
                "srmPrefix"      : "",
                "queueHeaders"   : ["JOBID", "USER", "STAT", "QUEUE", "FROM_HOST", "EXEC_HOST", "JOB_NAME", "SUBMIT_TIME"],
                "queueVars"      : {"queueName":"8nm", "queue":"QUEUE", "user":"USER", "state":"STAT", "run":"RUN", "summary":"bjobs -u all", "sample": "bjobs | head"},
                "CMSSW_lumi"     : None,
                },
        "fnal":{"localOutputDir" : os.environ["_CONDOR_SCRATCH_DIR"] if "_CONDOR_SCRATCH_DIR" in os.environ else "/tmp/%s"%user,
                "globalOutputDir": "%s/supyOutput/"%os.environ["HOME"],
                #"globalOutputDir":"/pnfs/cms/WAX/resilient/%s/tmp/"%user,
                "dCachePrefix"   : "dcap://cmsgridftp.fnal.gov:24125/pnfs/fnal.gov/usr/cms/WAX/",
                "dCacheTrim"     : "",
                "srmPrefix"      : "srm://cmssrm.fnal.gov:8443/",
                "queueHeaders"   : ["ID", "OWNER", "SUBMITTED1", "SUBMITTED2", "RUN_TIME", "ST", "PRI", "SIZE", "CMD"],
                "queueVars"      : {"user":"OWNER", "state":"ST", "run":"R", "summary":"condor_q -global", "sample": "condor_q -global -submitter %s | head"%user},
                "CMSSW_lumi"     : None,
                },
        "other":{"localOutputDir" : "/tmp/%s"%user,
                 "globalOutputDir": "/tmp/%s"%user,
                 "dCachePrefix"   : "",
                 "dCacheTrim"     : "",
                 "srmPrefix"      : "",
                 "queueHeaders"   : [],
                 "queueVars"      : {},
                 "CMSSW_lumi"     : None,
                 },
        }

def siteInfo(site = None, key = None) :
    if site==None : site = sitePrefix()
    ss = siteSpecs()
    assert site in ss, "site %s does not appear in siteSpecs()"%site
    assert key in ss[site], "site %s does not have key %s"%(site, key)
    return ss[site][key]

def batchScripts() :
    p = "site/"+sitePrefix()
    return ("%sSub.sh"%p, "%sJob.sh"%p, "%sTemplate.condor"%p)

def mvCommand(site = None, src = None, dest = None) :
    d = {"ic":"mv %s %s"%(src, dest),
         "pu":"mv %s %s"%(src, dest),
         "cern":"mv %s %s"%(src, dest),
         "fnal":"mv %s %s"%(src, dest),
         #"fnal":"srmcp file:///%s %s/%s"%(src, srmPrefix("fnal"), dest.replace("/pnfs/cms/WAX/","/")),
         "other":"mv %s %s"%(src, dest),
        }
    assert site in d, "site %s does not have a mvCommand defined"%site
    return d[site]

def dictionariesToGenerate() :
    return [
        ("pair<string,bool>", "string"),
        ("map<std::string,bool>", "string;map"),
        ("pair<string,string>", "string"),
        ("map<std::string,string>", "string;map"),
        ("ROOT::Math::Cartesian3D<float>", "Math/Point3D.h"),
        ("ROOT::Math::DisplacementVector3D<ROOT::Math::Cartesian3D<float>,ROOT::Math::DefaultCoordinateSystemTag>", "Math/Vector3D.h"),
        ("vector<ROOT::Math::DisplacementVector3D<ROOT::Math::Cartesian3D<float>,ROOT::Math::DefaultCoordinateSystemTag> >", "vector;Math/Vector3D.h"),
        ("ROOT::Math::PositionVector3D<ROOT::Math::Cartesian3D<float>,ROOT::Math::DefaultCoordinateSystemTag>", "Math/Point3D.h"),
        ("vector<ROOT::Math::PositionVector3D<ROOT::Math::Cartesian3D<float>,ROOT::Math::DefaultCoordinateSystemTag> >", "vector;Math/Point3D.h"),
        #ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> > etc. is addressed in linkdef.cxx
        ("vector<ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> > >", "vector;Math/LorentzVector.h"),
        ]

def srmFunc() :
    return 'utils.fileListFromSrmLs(dCachePrefix = "%s", dCacheTrim = "%s", location="%s'%(siteInfo(key = "dCachePrefix"),
                                                                                           siteInfo(key = "dCacheTrim"),
                                                                                           siteInfo(key = "srmPrefix"))
srm = srmFunc()
