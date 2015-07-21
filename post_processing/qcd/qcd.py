import array
import os
import ROOT

treename  = "XhhMiniNtuple"
#selection = "Pass2Btag || Pass3Btag"
#selection_mu = "(Pass2Btag || Pass3Btag || Pass4Btag) && PassSidebandMass"
selection = "PassTrackJetEta && (num_pass_btag(asso_trkjet_MV2c20[0][0], asso_trkjet_MV2c20[0][1], asso_trkjet_MV2c20[1][0], asso_trkjet_MV2c20[1][1], -0.9291) == 2 || num_pass_btag(asso_trkjet_MV2c20[0][0], asso_trkjet_MV2c20[0][1], asso_trkjet_MV2c20[1][0], asso_trkjet_MV2c20[1][1], -0.9291) == 3)"

selection_mu = "PassTrackJetEta && (num_pass_btag(asso_trkjet_MV2c20[0][0], asso_trkjet_MV2c20[0][1], asso_trkjet_MV2c20[1][0], asso_trkjet_MV2c20[1][1], -0.9291) == 2 || num_pass_btag(asso_trkjet_MV2c20[0][0], asso_trkjet_MV2c20[0][1], asso_trkjet_MV2c20[1][0], asso_trkjet_MV2c20[1][1], -0.9291) == 3 || num_pass_btag(asso_trkjet_MV2c20[0][0], asso_trkjet_MV2c20[0][1], asso_trkjet_MV2c20[1][0], asso_trkjet_MV2c20[1][1], -0.9291) == 4) && PassSidebandMass"

output    = "qcd_btag90wp.root"
overwrite = [("Pass2Btag", 0, "I"),
             ("Pass3Btag", 0, "I"),
             ("Pass4Btag", 1, "I"),
             ]

ntupledir = "root://eosatlas//eos/atlas/user/l/lazovich/microntup"
#datadir   = "user.lazovich.minintuple.data.270806_2_Boosted4bNTuple.root.35336043"
datadir   = "data"

ROOT.gROOT.Macro("../../plot/helpers.C")

def main():

    files = {}
    trees = {}
    skims = {}
    skims_mu = {}

    # inputs
    files["data"] = input_data()
    files["mc"]   = input_mc()

    for sample in ["data", "mc"]:

        # build
        trees[sample] = ROOT.TChain(treename)
        for fi in files[sample]:
           trees[sample].Add(fi)

        if trees[sample].GetEntries() > 0:
            skims[sample] = trees[sample].CopyTree(selection)
            skims_mu[sample] = trees[sample].CopyTree(selection_mu)
        else:
            skims[sample] = trees[sample]
            skims_mu[sample] = trees[sample]
            continue

        for name, value, type in overwrite:
            skims[sample].SetBranchStatus(name, 0)

        weight = 1 if sample == "data" else -1
        skims[sample] = add_branches(skims[sample], [("weight_qcd", weight, "I")]) # too slow?
        skims_mu[sample] = add_branches(skims_mu[sample], [("weight_qcd", weight, "I")]) # too slow?

    # merge
    inputs = ROOT.TList()
    inputs.Add(skims["data"])
    inputs.Add(skims["mc"])

    overwrite.append(("mu_qcd", get_mu_qcd(merge_trees(skims_mu["data"], skims_mu["mc"])), "F"))
    qcd = merge_trees(skims["data"], skims["mc"])
    # (over)write
    qcd = add_branches(qcd, overwrite)

    # write
    outfile = ROOT.TFile.Open(output, "recreate")
    outfile.cd()
    qcd.Write()

    # summarize
    template = "%15s | %12s | %12s | %12s"
    print
    print template % ("", "data entries", "mc entries", "qcd entries")
    print "-"*60
    print template % ("input trees",   trees["data"].GetEntries(), trees["mc"].GetEntries(), -1)
    print template % ("qcd selection", skims["data"].GetEntries(), skims["mc"].GetEntries(), qcd.GetEntries())
    print
    print " filesize: %.4f MB" % (outfile.GetSize()/pow(1024.0, 2))
    print

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
    return [ntupledir+"/"+datadir+"/"+"data_A4-C4.root"]

def input_mc():
    return []

def get_mu_qcd(tree):
    tmp_hist = ROOT.TH1F("tmp_hist", "tmp_hist", 1, 0, 1)
    tree.Draw("runNumber >> tmp_hist", "(" + selection + ")*PassSidebandMass*weight_qcd")
    denom = float(tmp_hist.Integral(0, tmp_hist.GetNbinsX()+1))

    tree.Draw("runNumber >> tmp_hist", "(PassTrackJetEta && (num_pass_btag(asso_trkjet_MV2c20[0][0], asso_trkjet_MV2c20[0][1], asso_trkjet_MV2c20[1][0], asso_trkjet_MV2c20[1][1], -0.9291) == 4))*PassSidebandMass*weight_qcd")
    num = float(tmp_hist.Integral(0, tmp_hist.GetNbinsX()+1))

    
    print "Mu QCD: %f, Num: %f, Denom: %f" % ((num/denom), num, denom)
    return num/denom

if __name__ == '__main__': 
    main()
