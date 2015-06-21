import os
import ROOT as r

#Get the names of all files under a directory
def getfilelist(dir=""):
	filelist=[]
	for file in [f for f in os.listdir(dir)]:
		filelist.append(file)
	return filelist

#Get the names of all files under a directory with extension
def getfilelistwithext(dir="",ext=""):
	filelist=[]
	for file in [f for f in os.listdir(dir) if f.endswith(ext)]:
		filelist.append(dir+file)
	return filelist

def plothist(filename="",outdir="", withtext=False):
	hfile = r.TFile(filename,'READ')
	names = [k.GetName() for k in hfile.GetListOfKeys()]
	for name in names:
		h = hfile.Get(name)
		c1 = r.TCanvas("c","c",1500,1200)
		h.SetStats(False)
		if withtext:
			h.Draw("colztext")
		else:
			h.Draw("colz")
		c1.Print(outdir+name+".pdf")
	hfile.Close()

#List key in a root file
def listkey(filename=""):
	hfile = r.TFile(filename,'READ')
	names = [k.GetName() for k in hfile.GetListOfKeys()]
	return names

#return all histograms in a dictionary in a file, with key as their histogram names
def gethist(filename=""):
	hfile = r.TFile(filename,'READ')
	names = [k.GetName() for k in hfile.GetListOfKeys()]
	hists = []
	for name in names:
		element = []
		element.append(name)
		h = hfile.Get(name)
		element.append(h)
		print h
		print element
		h.SetStats(False)
		hists.append(element)
	hfile.Close()
	return hists

#overlay histograms with same names in two rootfiles and produce the graphs in pdf
def overlay(filename1,filename2,outdir,name1="h1",name2="h2",color1=4,color2=2,setlog=True):
	f1 = r.TFile(filename1,'READ')
	f2 = r.TFile(filename2,'READ')
	key1 = listkey(filename1)
	key2 = listkey(filename2)
	commonkey = []
	for key in key1:
		if key in key2:
			commonkey.append(key)
	for key in commonkey:
		##Read histos
		h1 = f1.Get(key)
		h2 = f2.Get(key)

		##configure graphics
		c1 = r.TCanvas("c","c",1500,1200)
		h1.SetStats(False)
		h2.SetStats(False)
		h1.SetLineColor(color1)
		h2.SetLineColor(color2)
		leg = r.TLegend(0.75,0.70,0.98,0.85)
		leg.AddEntry(h1,name1)
		leg.AddEntry(h2,name2)
		if setlog:
			c1.SetLogy()

		##Draw histograms
		h1.Draw()
		h2.Draw("SAME")
		leg.Draw("SAME")
		c1.Print(outdir+key+".pdf")

		












