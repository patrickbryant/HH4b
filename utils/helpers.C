#include "TMath.h"
#include "TLorentzVector.h"

void helpers() {
    cout << "Ran helpers.C" << endl;
}

float dphi(float phi1, float phi2) {
    float PHI = fabs(phi1-phi2);
    if (PHI<=TMath::Pi())
        return PHI;
    else
        return 2*TMath::Pi()-PHI;
}

float dR(float eta1, float phi1, float eta2, float phi2) {
    float deta_ = eta1 - eta2;
    float dphi_ = dphi(phi1, phi2);
    return sqrt(deta_*deta_ + dphi_*dphi_);
}

float dR_vertices(float x1, float y1, float z1, float x2, float y2, float z2){

  double phi1 = TMath::ATan2(y1, x1);
  double theta1 = TMath::ATan2(fabs(y1), z1);
  double eta1 = -TMath::Log(TMath::Tan(theta1/2.0));

  double phi2 = TMath::ATan2(y2, x2);
  double theta2 = TMath::ATan2(fabs(y2), z2);
  double eta2 = -TMath::Log(TMath::Tan(theta2/2.0));

  return dR(eta1, phi1, eta2, phi2);
}

float inv_mass(float pt1, float eta1, float phi1, float m1, float pt2, float eta2, float phi2, float m2){
  TLorentzVector v1;
  TLorentzVector v2;
  TLorentzVector sum;
  
  v1.SetPtEtaPhiM(pt1, eta1, phi1, m1);
  v2.SetPtEtaPhiM(pt2, eta2, phi2, m2);

  sum = v1+v2;

  return sum.M();

}

int pass_btag(float mv2_score, float threshold){
  return (int)(mv2_score > threshold);
}

int num_pass_btag(float mv2_1, float mv2_2, float mv2_3, float mv2_4, float threshold){
  return pass_btag(mv2_1, threshold) + pass_btag(mv2_2, threshold) + pass_btag(mv2_3, threshold)  + pass_btag(mv2_4, threshold);
}

