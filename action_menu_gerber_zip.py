# coding: utf-8
# file : action_menu_gerber_zip.py
#
# Copyright (C) 2018 g200kg
#   Released under MIT License
#

import pcbnew
from pcbnew import *
import wx
import os
import locale
import zipfile

gerber_subdir = "Gerber"
merge_npth = False
use_aux_origin = True
excellon_format = EXCELLON_WRITER.DECIMAL_FORMAT # EXCELLON_WRITER.SUPPRESS_LEADING
zip_fname = ""

layers = [
    [ F_Cu,     'GTL', None ],
    [ B_Cu,     'GBL', None ],
    [ F_SilkS,  'GTO', None ],
    [ B_SilkS,  'GBO', None ],
    [ F_Mask,   'GTS', None ],
    [ B_Mask,   'GBS', None ],
    [ Edge_Cuts,'GML', None ],
    [ In1_Cu,   'GL2', None ],
    [ In2_Cu,   'GL3', None ],
    [ In3_Cu,   'GL4', None ],
    [ In4_Cu,   'GL5', None ],
]

strtab = {
    'default':{
        'DESC':'Make Gerber-files and ZIP for Elecrow / FusionPCB.',
        'MERGE':'Merge NPTH in single file (CHECK Recommended for FusionPCB)',
        'AUXORIG':'Use Aux Origin',
        'ZEROS':'Drillfile - Zeros',
        'DECIMAL':'Decimal format',
        'SUPPRESS':'Suppress leading zeros',
        'CLOSE':'Close',
        'EXEC':'Plot and make zip',
        'COMPLETE':'GerberZip Complete. \n\n OUtput file : %s',
    },
    'ja_JP':{
        'DESC':u'Elecrow / FusionPCB 向けのガーバーを作成し ZIP ファイルにまとめます。',
        'MERGE':u'NPTH を 1 つのファイルにマージ (FusionPCB ではチェック推奨)',
        'AUXORIG':u'補助座標の使用',
        'ZEROS':u'ドリルファイル - ゼロの扱い',
        'DECIMAL':u'小数点フォーマット',
        'SUPPRESS':u'サプレスリーディングゼロ',
        'CLOSE':u'閉じる',
        'EXEC':u'プロットと Zip の作成',
        'COMPLETE':u'GerberZip 完了。 \n\n 出力ファイル : %s',
    },
}

def getstr(s,lang):
    if(lang not in s):
        tab =strtab['default']
    else:
        tab =strtab[lang]
    return tab[s]

def forcedel(fname):
    if os.path.exists(fname):
        os.remove(fname)

def forceren(src, dst):
    forcedel(dst)
    os.rename(src, dst)

def refill(board):
    filler = pcbnew.ZONE_FILLER(board)
    zones = board.Zones()
    filler.Fill(zones)

def Exec():
    global zip_fname
    board = pcbnew.GetBoard()
    board_fname = board.GetFileName()
    board_dir = os.path.dirname(board_fname)
    board_basename = (os.path.splitext(os.path.basename(board_fname)))[0]
    gerber_dir = '%s/%s' % (board_dir, gerber_subdir)
    drill_fname = '%s/%s.TXT' % (gerber_dir, board_basename)
    npth_fname = '%s/%s-NPTH.TXT' % (gerber_dir, board_basename)
    zip_fname = '%s/%s.zip' % (gerber_dir, board_basename)
    if not os.path.exists(gerber_dir):
        os.mkdir(gerber_dir)
    max_layer = board.GetCopperLayerCount() + 5

    refill(board)

# PLOT
    pc = pcbnew.PLOT_CONTROLLER(board)
    po = pc.GetPlotOptions()

    po.SetOutputDirectory(gerber_dir)
    po.SetPlotValue(True)
    po.SetPlotReference(True)
    po.SetExcludeEdgeLayer(False)
    po.SetLineWidth(FromMM(0.1))
    po.SetSubtractMaskFromSilk(True)
    po.SetUseAuxOrigin(use_aux_origin)

    for layer in layers:
        targetname = '%s/%s.%s' % (gerber_dir, board_basename, layer[1])
        forcedel(targetname)
    forcedel(drill_fname)
    forcedel(npth_fname)
    forcedel(zip_fname)

    for i in range(max_layer):
        layer = layers[i]
        pc.SetLayer(layer[0])
        pc.OpenPlotfile(layer[1],PLOT_FORMAT_GERBER,layer[1])
        pc.PlotLayer()
        layer[2] = pc.GetPlotFileName()
    pc.ClosePlot()

    for i in range(max_layer):
        layer = layers[i]
        targetname = '%s/%s.%s' % (gerber_dir, board_basename, layer[1])
        forceren(layer[2],targetname)
# DRILL
    ew = EXCELLON_WRITER(board)
    ew.SetFormat(True, excellon_format, 3, 3)
    offset = wxPoint(0,0)
    if(use_aux_origin):
        offset = board.GetAuxOrigin()
    ew.SetOptions(False, False, offset, merge_npth)
    ew.CreateDrillandMapFilesSet(gerber_dir,True,False)
    if merge_npth:
        forceren('%s/%s.drl' % (gerber_dir, board_basename), drill_fname)
    else:
        forceren('%s/%s-PTH.drl' % (gerber_dir, board_basename), drill_fname)
        forceren('%s/%s-NPTH.drl' % (gerber_dir, board_basename), npth_fname)
# ZIP
    with zipfile.ZipFile(zip_fname,'w') as f:
        for i in range(max_layer):
            layer = layers[i]
            targetname = '%s/%s.%s' % (gerber_dir, board_basename, layer[1])
            f.write(targetname, os.path.basename(targetname))
        f.write(drill_fname, os.path.basename(drill_fname))
        if not merge_npth:
            f.write(npth_fname, os.path.basename(npth_fname))


class GerberZip( pcbnew.ActionPlugin ):

    max_layer = 7

    def defaults( self ):
        self.name = "Make Gerber-Zip (Elecrow / FusionPCB style)"
        self.category = "Plot"
        self.description = "Make Gerber-Zip-file for Elecrow / FusionPCB"
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'action_menu_gerber_zip.png')

    def Run(self):
        class Dialog(wx.Dialog):
            def __init__(self, parent):
                lang = wx.Locale.GetCanonicalName(wx.GetLocale())
                wx.Dialog.__init__(self, parent, id=-1, title='Gerber-Zip')
                self.panel = wx.Panel(self)
                self.description = wx.StaticText(self.panel, wx.ID_ANY, getstr('DESC',lang), pos=(20,10))
                self.mergeNpth = wx.CheckBox(self.panel, wx.ID_ANY, getstr('MERGE',lang), pos=(30,40))
                self.useAuxOrigin = wx.CheckBox(self.panel, wx.ID_ANY, getstr('AUXORIG',lang), pos=(30,60))
                self.zeros = wx.RadioBox(self.panel,wx.ID_ANY, getstr('ZEROS',lang), pos=(30,90), choices=[getstr('DECIMAL',lang), getstr('SUPPRESS',lang)], style=wx.RA_HORIZONTAL)
                self.execbtn = wx.Button(self.panel, wx.ID_ANY, getstr('EXEC',lang), pos=(30,150))
                self.clsbtn = wx.Button(self.panel, wx.ID_ANY, getstr('CLOSE',lang), pos=(170,150))
                self.mergeNpth.SetValue(merge_npth)
                self.useAuxOrigin.SetValue(use_aux_origin)
                self.clsbtn.Bind(wx.EVT_BUTTON, self.OnClose)
                self.execbtn.Bind(wx.EVT_BUTTON, self.OnExec)
            def OnClose(self,e):
                e.Skip()
                self.Close()
            def OnExec(self,e):
                lang = wx.Locale.GetCanonicalName(wx.GetLocale())
                merge_npth = True if self.mergeNpth.GetValue() else False
                use_aux_origin = True if self.useAuxOrigin.GetValue() else False
                excellon_format = (EXCELLON_WRITER.DECIMAL_FORMAT, EXCELLON_WRITER.SUPPRESS_LEADING)[self.zeros.GetSelection()]
                Exec()
                wx.MessageBox(getstr('COMPLETE',lang)%zip_fname, 'Gerber Zip', wx.OK|wx.ICON_INFORMATION)
                e.Skip()
        dialog = Dialog(None)
        dialog.Center()
        dialog.ShowModal()
        dialog.Destroy()

GerberZip().register()
