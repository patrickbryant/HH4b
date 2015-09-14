"""
qcd.py: a script to convert ntuples into a multijet ntuple.

$ python qcd.py --wp=70
"""
import argparse
import array
import copy
import os
import sys
import ROOT

treename  = "XhhMiniNtuple"

ROOT.gROOT.SetBatch()
ROOT.gROOT.Macro("../utils/helpers.C")

def main():

    ops = options()

    if not ops.wp in ["70", "80", "85", "90"]:
        fatal("Please give a supported --wp like 70 or 90")

    # config
    # replace this with Xhh* btagging decisions when ready
    cuts = {"70": -0.3098,
            "80": -0.7132,
            "85": -0.8433,
            "90": -0.9291,
            }

    format = {"mv2": "asso_trkjet_MV2c20", 
              "cut": cuts[ops.wp],
              }
    
    # select 2,3,4-tag sample
    selection = ["n_calo_jets >= 2",
                 "calo_jet_pt[0] > 350*1000 && abs(calo_jet_eta[0]) < 2.0",
                 "calo_jet_pt[1] > 250*1000 && abs(calo_jet_eta[1]) < 2.0",
                 "abs(calo_jet_eta[0] - calo_jet_eta[1]) < 1.7",
                 "n_asso_track_jets[0] >= 2",
                 "n_asso_track_jets[1] >= 2",
                 "asso_trkjet_pt[0][0] > 20*1000 && abs(asso_trkjet_eta[0][0]) < 2.5",
                 "asso_trkjet_pt[0][1] > 20*1000 && abs(asso_trkjet_eta[0][1]) < 2.5",
                 "asso_trkjet_pt[1][0] > 20*1000 && abs(asso_trkjet_eta[1][0]) < 2.5",
                 "asso_trkjet_pt[1][1] > 20*1000 && abs(asso_trkjet_eta[1][1]) < 2.5",
                 "(%(mv2)s[0][0] > %(cut)s && %(mv2)s[0][1] > %(cut)s) || (%(mv2)s[1][0] > %(cut)s && %(mv2)s[1][1] > %(cut)s)" % format,
                 ]
    selection = " && ".join(["(%s)" % sel for sel in selection])

    fourtag = "%(mv2)s[0][0] > %(cut)s && %(mv2)s[0][1] > %(cut)s && %(mv2)s[1][0] > %(cut)s && %(mv2)s[1][1] > %(cut)s" % format
    sideband = "PassSidebandMass"
    
    output    = "qcd_%swp.root" % (ops.wp)
    overwrite = [("Pass2Btag", 0, "I"),
                 ("Pass3Btag", 0, "I"),
                 ("Pass4Btag", 1, "I"),
                 ]

    files = {}
    trees = {}
    skims = {}

    # inputs
    files["data"] = input_data()
    files["mc"]   = input_mc()

    for sample in ["data", "mc"]:

        trees[sample] = ROOT.TChain(treename)
        for fi in files[sample]:
           trees[sample].Add(fi)

        if trees[sample].GetEntries() > 0:
            skims[sample] = trees[sample].CopyTree(selection)
        else:
            skims[sample] = trees[sample]
            continue

        for name, value, type in overwrite:
            skims[sample].SetBranchStatus(name, 0)

        weight = 1 if sample == "data" else -1
        skims[sample] = add_branches(skims[sample], [("weight_qcd", weight, "I")])

    if skims["data"].GetEntries() == 0:
        fatal("No data entries found. Exiting.")

    # merge
    qcd = merge_trees(skims["data"], skims["mc"])

    # derive mu_qcd and uncertainty
    mu_qcd, mu_qcd_stat = get_mu_qcd(qcd, fourtag=fourtag, topo=sideband, weight="weight_qcd")
    overwrite.append(("weight_mu_qcd",      mu_qcd,      "F"))
    overwrite.append(("weight_mu_qcd_stat", mu_qcd_stat, "F"))

    # discard the 4-tag region
    qcd = qcd.CopyTree("!(%s)" % (fourtag))

    # update branches
    qcd = add_branches(qcd, overwrite)

    # write
    outfile = ROOT.TFile.Open(output, "recreate")
    outfile.cd()
    qcd.Write()

    # summarize
    template = "%15s | %12s | %12s"
    print
    print " skim summary"
    print "-"*45
    print template % ("", "data entries", "mc entries")
    print "-"*45
    print template % ("input trees",   trees["data"].GetEntries(), trees["mc"].GetEntries())
    print template % ("2,3,4-tag",     skims["data"].GetEntries(), skims["mc"].GetEntries())
    print
    print
    print " output filesize"
    print "-"*45
    print " %.4f MB" % (outfile.GetSize()/pow(1024.0, 2))
    print

    outfile.Close()

def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wp")
    return parser.parse_args()

def fatal(message):
    sys.exit("Error in %s: %s" % (__file__, message))

def merge_trees(skims_data, skims_mc):
    inputs = ROOT.TList()
    inputs.Add(skims_data)
    inputs.Add(skims_mc)
    dummy = ROOT.TTree(treename, treename)

    return dummy.MergeTrees(inputs)

def add_branches(tree, pairs):

    contents = {}
    branches = {}

    for name, value, type in pairs:
        contents[name] = array.array(type.lower(), [value])
        branches[name] = tree.Branch(name, contents[name], name+"/"+type)

    for entry in tree:
        for name, value, type in pairs:
            branches[name].Fill()
    
    return tree

def input_data():
    return ["root://eosatlas//eos/atlas/user/l/lazovich/microntup/data/data_A4-C4.root"]
    # return ["/Users/alexandertuna/HH4b_data/data_A4-C4.root"]

def input_mc():
    return []

def get_mu_qcd(tree, fourtag, topo, weight):
    """ 
    If we make this topology-dependent, 
    maybe we return an entire histogram? TBD.
    """
    numer = ROOT.TH1F("numer", "numer", 1, 0, 1)
    denom = ROOT.TH1F("denom", "denom", 1, 0, 1)
    for hist in [numer, denom]:
        hist.Sumw2()

    tree.Draw("0.5 >> numer", "( (%s) && (%s))*(%s)" % (fourtag, topo, weight), "goff")
    tree.Draw("0.5 >> denom", "(!(%s) && (%s))*(%s)" % (fourtag, topo, weight), "goff")

    divide = copy.copy(numer)
    divide.Reset()
    divide.Divide(numer, denom)

    print 
    print " mu_qcd calculation:"
    print "-"*45
    print " %5.1f / %7.1f  =  %7.5f (%7.5f)" % (numer.GetBinContent(1), denom.GetBinContent(1), divide.GetBinContent(1), divide.GetBinError(1))
    print

    return [divide.GetBinContent(1), 
            divide.GetBinError(1),
            ]


if __name__ == '__main__': 
    main()
