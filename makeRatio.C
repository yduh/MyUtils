#include "TFile.h"

void makeRatioHisto(){

	TFile * inputFile = new TFile("output/validation.root");
	TH2D * nom = inputFile->Get("QCD_HT_1000ToInf/h_jet_etaphi_BiasedDPhil0p3");
	TH2D * dem = inputFile->Get("QCD_HT_1000ToInf/h_jet_etaphi_BiasedDPhig0p3");

	TH2D * ratio = nom->Clone();
	ratio->Divide(dem);

	ratio->SetStats(0);
	ratio->SetTitle("Ratio with number of biasedDPhi Jets to the number of all jets");
	TCanvas * c1 = new TCanvas();
	ratio->Draw("colz");


	TH1D * ratio1D = new TH1D("ratio1D","1D Ratio",50,0.,1.);
	double temp=0;
	for (unsigned xbin = 0; xbin < ratio->GetNbinsX(); xbin++){
		for (unsigned ybin = 0; ybin < ratio->GetNbinsY(); ybin++){
			ratio1D->Fill(ratio->GetBinContent(xbin,ybin));
		};
	};
	TCanvas * c2 = new TCanvas();
	ratio1D->SetStats(0);
	ratio1D->Draw();


};