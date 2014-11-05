import re
import root_style
import sys
import os
from array import *
import ROOT
import argparse
ROOT.gROOT.SetBatch()
parser = argparse.ArgumentParser(description='Process pad_run.')
parser.add_argument('filename',type = str, help='filename')

args = parser.parse_args()
print args
print type(args.filename),str(args.filename)
filename = args.filename
runno = re.findall(r'\d+',str(filename))[-1]
args.runno = int(runno)

root_style.set_style(1000,1000,1)

#filename = 'run_bt2014_10r{runno:06d}.root'.format(runno=args.runno)
f = ROOT.TFile.Open(str(filename))
if not f:
    raise Exception('Cannot open file')
tree = f.Get('rec')
if not tree:
    raise Exception('Cannot open tree')
histos = {}
t_min = (int(tree.GetMinimum('timestamp')/1000)*1000)
t_max = ((int(tree.GetMaximum('timestamp')/1000)+1)*1000)
print t_min,t_max
t_bins = int((t_max - t_min)/1000)
s_min = -30.
s_max = 30.
s_bins = int((s_max - s_min))*8

def set_time_fmt(histo):
    histo.GetXaxis().SetTimeDisplay(1)
    histo.GetXaxis().SetTimeFormat('%H:%M')
    histo.GetXaxis().SetNdivisions(1005)

name = 'h_timing'
t_bins = int(t_bins)
t_min = float(t_min)
t_max = float(t_max)
if t_bins > 1000:
    t_bins = 1000
histo = ROOT.TH1F(name,name,int(t_bins*100),float(t_min),float(t_max) )
set_time_fmt(histo)
histos[name] = {'h':histo, 'y':'number of entries', 'x':'time stamp','o':'colz'}
tree.Draw('timestamp>>%s'%name,'!calibflag','goff')
entries_per_bin = 1000
n = entries_per_bin
x = []
y = []
for i in range(1,histo.GetNbinsX()+1):
    if n >= entries_per_bin:
        x.append(histo.GetXaxis().GetBinLowEdge(i))
        y.append(n)
        n = 0
    n += histo.GetBinContent(i)
x.append(histo.GetXaxis().GetBinLowEdge(histo.GetNbinsX()+1))
y.append(n)
print len(x),len(y)
print x
print y
t_array = array('d',x)

name = 'h_timing_calib'
histo = ROOT.TH1F(name,name,t_bins*100,float(t_min),float(t_max))
set_time_fmt(histo)
histos[name] = {'h':histo, 'y':'number of entries', 'x':'time stamp','o':'','xx':'time'}
set_time_fmt(histos[name]['h'])
tree.Draw('timestamp>>%s'%name,'calibflag','goff')
# Channel 1
def noise_plots(channel):
    print '\nplotting noise for channel',channel

    name = 'h_baseline_time_chn%d'%channel
    histos[name] = {'h': ROOT.TH2F(name, name, len(t_array)-1, t_array, s_bins, s_min, s_max), 'x':'time stamp', 'y':'baseline_{chn%d}'%channel,'o':'colz','xx':'time'}
    set_time_fmt(histos[name]['h'])
    cmd = "avrg_first_chn%d:timestamp>>%s"%(channel, name)
    print '\t', name, cmd
    tree.Draw(cmd,"!calibflag","goff")

    name = 'h_baseline_chn%d'%channel
    histos[name] = {'h': ROOT.TH1F(name,name,s_bins,s_min,s_max), 'y':'number of entries', 'x':'baseline_{chn%d}'%channel,'o':'colz'}
    cmd = "avrg_first_chn%d>>%s"%(channel,name)
    print '\t', name,cmd
    tree.Draw(cmd,"!calibflag","goff")

    name = 'h_baseline_time_calib_chn%d'%channel
    histos[name] = {'h': ROOT.TH2F(name, name, t_bins, t_min, t_max, s_bins, s_min, s_max), 'x':'time stamp', 'y':'baseline_{chn%d}'%channel,'o':'colz','xx':'time'}
    set_time_fmt(histos[name]['h'])
    cmd = "avrg_first_chn%d:timestamp>>%s"%(channel, name)
    print '\t', name, cmd
    tree.Draw(cmd,"calibflag","goff")

    name = 'h_baseline_calib_chn%d'%channel
    histos[name] = {'h': ROOT.TH1F(name,name,s_bins,s_min,s_max), 'y':'number fo entries', 'x':'baseline_{chn%d}'%channel,'o':''}
    cmd = "avrg_first_chn%d>>%s"%(channel,name)
    print '\t', name, cmd
    tree.Draw(cmd,"calibflag","goff")

def signal_plots():
    s_max = tree.GetMaximum('Integral50')
    s_min = tree.GetMinimum('Integral50')
    s_bin = int(s_max-s_min)*2

    name = 'h_signal_time'
    histos[name] = {'h': ROOT.TH2F(name, name, len(t_array)-1, t_array, s_bins, s_min, s_max), 'x':'time stamp', 'y':'signal','o':'colz','xx':'time'}
    set_time_fmt(histos[name]['h'])
    cmd = "Integral50:timestamp>>%s"%( name)
    print '\t', name, cmd
    tree.Draw(cmd,"!calibflag","goff")
    name = 'h_signal_cm_corrected_time'
    histos[name] = {'h': ROOT.TH2F(name, name, len(t_array)-1, t_array, s_bins, s_min, s_max), 'x':'time stamp', 'y':'signal','o':'colz','xx':'time'}
    set_time_fmt(histos[name]['h'])
    cmd = "Integral50-avrg_first_chn1:timestamp>>%s"%( name)
    print '\t', name, cmd
    tree.Draw(cmd,"!calibflag","goff")

    pass
for i in range(1,5):
    noise_plots(i)
signal_plots()

c1 = ROOT.TCanvas()
folder = './results/%06d'%args.runno
def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

def save_histo(histo,option=''):
    c1.cd()
    histo.Draw(option)
    pt = ROOT.TPaveText(.02,.02,.1,.1,'NDC');
    pt.SetTextFont(42)
    pt.SetTextSize(0.04)

    pt.AddText('Run %d'%args.runno)
    pt.SetFillColor(0)
    pt.SetFillStyle(0)
    pt.SetShadowColor(0)
    pt.SetBorderSize(0)
    pt.Draw()
    name = histo.GetName()
    fname = '{folder}/{name}.png'.format(folder=folder,name=name)
    print fname
    ensure_dir(fname)
    c1.Update()
    c1.SaveAs(fname)


for name in histos:
    print name, histos[name]
    entry = histos[name]
    histo = entry.get('h',None)
    if not histo:
        continue

    histo.GetXaxis().SetTitle(entry.get('x',''))
    histo.GetYaxis().SetTitle(entry.get('y',''))
    if 'time' in entry.get('xx',''):
        set_time_fmt(histo)
    save_histo(histo,entry.get('o',''))
    if 'TH2F' in histo.ClassName():
        htemp = histo.ProfileX()
        htemp.GetXaxis().SetTitle(entry.get('x',''))
        htemp.GetYaxis().SetTitle('avrg '+entry.get('y',''))
        if 'time' in entry.get('xx',''):
            set_time_fmt(htemp)
        save_histo(htemp,'')
        #htemp.GetXaxis().SetTimeDisplay(1)
    else:
        pass






