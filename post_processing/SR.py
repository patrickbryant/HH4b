"""
SR.py: a script to convert ntuples into SR ntuple

$ python SR.py --wp=70
"""
import argparse
import array
import copy
import glob
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
    if not ops.input:
        fatal("Please give a path to --input files for processing")
    if not ops.output:
        fatal("Please give a path to a --output file to write to.")

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
                 "%(mv2)s[0][0] > %(cut)s && %(mv2)s[0][1] > %(cut)s && %(mv2)s[1][0] > %(cut)s && %(mv2)s[1][1] > %(cut)s" % format,
                 ]
    selection = " && ".join(["(%s)" % sel for sel in selection])

    files = {}
    trees = {}
    skims = {}

    # inputs
    tree = ROOT.TChain(treename)
    for fi in input(ops.input):
       tree.Add(fi)

    # skim
    if tree.GetEntries() > 0:
        skim = tree.CopyTree(selection)
    else:
        skim = tree

    # write
    outfile = ROOT.TFile.Open(ops.output, "recreate")
    outfile.cd()
    skim.Write()

    # summarize
    template = "%15s | %12s"
    print
    print " skim summary"
    print "-"*45
    print template % ("", "entries")
    print "-"*45
    print template % (" input", tree.GetEntries())
    print template % ("output", skim.GetEntries())
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
    parser.add_argument("--input")
    parser.add_argument("--output")
    return parser.parse_args()

def fatal(message):
    sys.exit("Error in %s: %s" % (__file__, message))

def input(string):
    if "root://" in string and "*" in string:
        fatal("Sorry, wildcards not yet supported for root:// filesystems.")
    elif "*" in string:
        return glob.glob(string)
    else:
        return [string]

if __name__ == '__main__': 
    main()
