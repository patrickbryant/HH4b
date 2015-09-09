
void cross_sections() {
    cout << "Ran cross_sections.C" << endl;
}

double xsec(int dsid) {
    
    // https://svnweb.cern.ch/trac/atlasphys-comm/browser/Physics/Generators/
    // PMGCrossSectionTool/trunk/data/list_Xsec_Exotics_Other_Download.txt

    if (dsid == 301495) return 0.033696;
    if (dsid == 301500) return 0.003453;
    if (dsid == 301501) return 0.00085923; // this is wrong
    if (dsid == 301503) return 0.00055923;
    if (dsid == 301505) return 0.00055923; // this is wrong
    if (dsid == 301507) return 2.7746e-05;

    cout << "DSID " << dsid << " -- cannot find xsec. Returning 1." << endl;
    return 1.0;
}

double nevents(int dsid) {

    if (dsid == 301495) return 100000.0;
    if (dsid == 301500) return  99400.0;
    if (dsid == 301501) return  99800.0;
    if (dsid == 301503) return  89800.0;
    if (dsid == 301505) return  60000.0;
    if (dsid == 301507) return  78000.0;

    cout << "DSID " << dsid << " -- cannot find nevents. Returning 1." << endl;
    return 1.0;
}

double weight_lumi(int dsid, double target_lumi) {

    // picobarns (pb)!
    return target_lumi * xsec(dsid) / (double)(nevents(dsid));

}


