
void cross_sections() {
    cout << "Ran cross_sections.C" << endl;
}

double xsec(int dsid) {

    // twiki/GtoHHorZZtobbbbMC15Validation
    
    // https://svnweb.cern.ch/trac/atlasphys-comm/browser/Physics/Generators/
    // PMGCrossSectionTool/trunk/data/list_Xsec_Exotics_Other_Download.txt

    double hh4b = pow(5.77E-01, 2);

    // RSG hh 4b, c = 0.5
    if (dsid == 301486) return (hh4b)*0.22213;
    if (dsid == 301487) return (hh4b)*0.008543;

    // RSG hh 4b, c = 1.0
    if (dsid == 301488) return (hh4b)*1.3199;
    if (dsid == 301489) return (hh4b)*1.901;
    if (dsid == 301490) return (hh4b)*0.8924;
    if (dsid == 301491) return (hh4b)*0.4104;
    if (dsid == 301492) return (hh4b)*0.20148;
    if (dsid == 301493) return (hh4b)*0.10549;
    if (dsid == 301494) return (hh4b)*0.05835;
    if (dsid == 301495) return (hh4b)*0.03368;
    if (dsid == 301496) return (hh4b)*0.02023;
    if (dsid == 301497) return (hh4b)*0.01254;
    if (dsid == 301498) return (hh4b)*0.007979;
    if (dsid == 301499) return (hh4b)*0.005201;
    if (dsid == 301500) return (hh4b)*0.003450;
    if (dsid == 301501) return (hh4b)*0.002336;
    if (dsid == 301502) return (hh4b)*0.001116;
    if (dsid == 301503) return (hh4b)*5.559e-04;
    if (dsid == 301504) return (hh4b)*2.486e-04;
    if (dsid == 301505) return (hh4b)*1.158e-04;
    if (dsid == 301506) return (hh4b)*5.585e-05;
    if (dsid == 301507) return (hh4b)*2.772e-05;

    // RSG hh 4b, c = 2.0
    if (dsid == 301508) return (hh4b)*9.997;
    if (dsid == 301509) return (hh4b)*8.560;
    if (dsid == 301510) return (hh4b)*3.755;
    if (dsid == 301511) return (hh4b)*1.657;
    if (dsid == 301512) return (hh4b)*0.7899;
    if (dsid == 301513) return (hh4b)*0.4043;
    if (dsid == 301514) return (hh4b)*0.2193;
    if (dsid == 301515) return (hh4b)*0.1251;
    if (dsid == 301516) return (hh4b)*0.07419;
    if (dsid == 301517) return (hh4b)*0.04548;
    if (dsid == 301518) return (hh4b)*0.02872;
    if (dsid == 301519) return (hh4b)*0.01855;
    if (dsid == 301520) return (hh4b)*0.01227;
    if (dsid == 301521) return (hh4b)*0.008254;
    if (dsid == 301522) return (hh4b)*0.003913;
    if (dsid == 301523) return (hh4b)*0.001951;
    if (dsid == 301524) return (hh4b)*0.8703e-03;
    if (dsid == 301525) return (hh4b)*0.4070e-03;
    if (dsid == 301526) return (hh4b)*0.1984e-03;
    if (dsid == 301527) return (hh4b)*0.1001e-03;

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


