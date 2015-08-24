import ROOT, rootlogon
import argparse
import array
import copy
import glob
import helpers
import os
import sys
import time
import yaml

ROOT.gROOT.SetBatch(True)
ROOT.gROOT.Macro("../utils/helpers.C")

timestamp = time.strftime("%Y-%m-%d-%Hh%Mm%Ss")

debug = True
stack = True

def main():

    ops = options()

    if not ops.plotter:
        fatal("Need --plotter for configuration.")
    plotter = yaml.load(open(ops.plotter))

    if not "directory" in plotter:
        plotter["directory"] = "."
        warn("No directory given. Writing output to cwd.")

    trees   = {}
    plots   = {}
    weights = {}
    colors  = {}
    labels  = {}
    stack   = {}
    overlay = {}
    is_data = {}

    # retrieve inputs
    for sample in plotter["samples"]:

        name = sample["name"]

        # input trees
        paths = sample["path"]
        if not glob.glob(paths):
            fatal("Found no files at %s" % (paths))

        trees[name] = ROOT.TChain(plotter["tree"])
        for path in glob.glob(paths):
            trees[name].Add(path)

        # misc
        weights[name] = " * ".join(sample["weights"]) if "weights" in sample else "1"
        colors[name]  = eval(sample["color"]) if sample["color"].startswith("ROOT") else sample["color"] 
        labels[name]  = sample["label"]
        stack[name]   = sample["stack"]
        overlay[name] = sample["overlay"]
        is_data[name] = sample["is_data"]

    # create output file
    if not os.path.isdir(plotter["directory"]):
        os.makedirs(plotter["directory"])
    output = ROOT.TFile.Open("%s/plots.%s.canv.root" % (plotter["directory"], timestamp), "recreate")

    # make money
    for plot in plotter["plots"]:

        hists = {}
        draw = {}
        if "bins" in plot:
            draw["bins"]  = array.array("d", plot["bins"])
        draw["title"]     = ";%s;%s" % (plot["xtitle"], plot["ytitle"])
        draw["variable"]  = plot["variable"]
        draw["selection"] = " && ".join(plotter["selection"])

        canv = ROOT.TCanvas(plot["name"], plot["name"], 800, 800)
        canv.Draw()
        canv.SetLogy(plot["logY"])

        stacks   = ROOT.THStack(plot["name"]+"stacks",   draw["title"])
        overlays = ROOT.THStack(plot["name"]+"overlays", draw["title"])
        do_stack = False
        do_overlay = False
        
        for sample in trees:

            draw["name"]   = plot["name"]+"__"+sample
            draw["weight"] = weights[sample]
            for option in ["weight"]:
                draw[option] = "(%s)" % (draw[option])


            if "bins" in plot:
                hists[sample] = ROOT.TH1F(draw["name"], draw["title"], len(draw["bins"])-1, draw["bins"])
            else:
                hists[sample] = ROOT.TH1F(draw["name"], draw["title"], plot["n_bins"], plot["bin_low"], plot["bin_high"])
            hists[sample].Sumw2()

            trees[sample].Draw("%(variable)s >> %(name)s" % draw, "(%(selection)s) * %(weight)s" % draw, "goff")
            output.cd()
            # hists[sample].Write() # todo
            
            #hists[sample].Scale(1/hists[sample].Integral(0, hists[sample].GetNbinsX()))

            if stack[sample]:
                do_stack = True
                hists[sample].SetFillColor(colors[sample])
                hists[sample].SetLineColor(ROOT.kBlack)
                hists[sample].SetLineWidth(2)
                stacks.Add(copy.copy(hists[sample]), ("ep" if is_data[sample] else "hist"))

            if overlay[sample]:
                do_overlay = True
                hists[sample].SetFillColor(0)
                hists[sample].SetLineColor(colors[sample])
                hists[sample].SetLineWidth(3)
                overlays.Add(copy.copy(hists[sample]), ("ep" if is_data[sample] else "hist"))

        # draw
        maximum = max([stacks.GetMaximum(), overlays.GetMaximum("nostack")])
        maximum = maximum*(100.0 if plot["logY"]     else 2.0)
        maximum = maximum*(1.2   if plotter["ratio"] else 1.0)

        if do_stack:
            stacks.SetMaximum(maximum)
            stacks.Draw()

        if do_overlay and do_stack:
            overlays.SetMaximum(maximum)
            overlays.Draw("nostack,same")
        elif do_overlay:
            overlays.SetMaximum(maximum)
            overlays.Draw("nostack")

        if plotter["data"]:
            pass

        if plotter["ratio"] and stacks.GetStack():

            # numerator definition is a placeholder.
            # only works if overlay[0]=data.
            ratio = helpers.ratio(name   = canv.GetName()+"_ratio",
                                  numer  = overlays.GetHists()[0],   # AHH KILL ME
                                  denom  = stacks.GetStack().Last(),
                                  min    = 0.45,
                                  max    = 1.55,
                                  ytitle = "Data / pred."
                                  )
            share = helpers.same_xaxis(name          = canv.GetName()+"_share",
                                       top_canvas    = canv,
                                       bottom_canvas = ratio,
                                       )
            canv.SetName(canv.GetName()+"_noratio")
            share.SetName(share.GetName().replace("_share", ""))
            canv = share

        elif plotter["ratio"] and not stacks.GetStack():
            warn("Want to make ratio plot but dont have stack. Skipping ratio.")

        # stack legend
        xleg, yleg = 0.6, 0.7
        legend = ROOT.TLegend(xleg, yleg, xleg+0.2, yleg+0.2)

        if do_stack:
            for hist in reversed(stacks.GetHists()):
                legend.AddEntry(hist, labels[hist.GetName().split("__")[1]], "f")

        if do_overlay:
            for hist in reversed(overlays.GetHists()):
                legend.AddEntry(hist, labels[hist.GetName().split("__")[1]], "l")
        
        legend.SetBorderSize(0)
        legend.SetFillColor(0)
        legend.SetMargin(0.3)
        legend.SetTextSize(0.04)
        legend.Draw()

        # watermarks
        xatlas, yatlas = 0.38, 0.87
        atlas = ROOT.TLatex(xatlas,      yatlas, "ATLAS Internal")
        hh4b  = ROOT.TLatex(xatlas, yatlas-0.06, "X #rightarrow HH #rightarrow 4b")
        lumi  = ROOT.TLatex(xatlas, yatlas-0.12, "#sqrt{s} = 13 TeV")
        watermarks = [atlas, hh4b, lumi]

        # KS, chi2
        if stacks.GetStack():
            if plotter.get("ks"):
                kolg, chi2, ndf = helpers.compare(overlays.GetHists()[0],
                                                  stacks.GetStack().Last(),
                                                  ) # AH KILL ME
                yks   = 0.975
                ychi2 = 0.975
                xks   = 0.27
                xchi2 = 0.55
                
                ks = ROOT.TLatex(xks,   yks,   "KS = %5.3f" % (kolg))
                ch = ROOT.TLatex(xchi2, ychi2, "#chi^{2} / ndf = %.1f / %i" % (chi2, ndf))
                watermarks += [ks, ch]

        # draw watermarks
        for wm in watermarks:
            wm.SetTextAlign(22)
            wm.SetTextSize(0.04)
            wm.SetTextFont(42)
            wm.SetNDC()
            wm.Draw()

        canv.SaveAs(os.path.join(plotter["directory"], canv.GetName()+".pdf"))

        output.Close()

def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plotter")
    return parser.parse_args()

def fatal(message):
    sys.exit("Error in %s: %s" % (__file__, message))

def warn(message):
    print
    print "Warning in %s: %s" % (__file__, message)
    print

if __name__ == "__main__":
    main()
        
