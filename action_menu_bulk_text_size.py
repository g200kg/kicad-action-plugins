# file : action_bulk_format_text.py
#
# Copyright (C) 2018 g200kg
#   Released under under MIT License
#

import pcbnew
from pcbnew import *
import wx
import os
import zipfile

size_ref_height = 1
size_ref_width = 1
size_ref_thickness = 0.1
size_val_height = 1
size_val_width = 1
size_val_thickness = 0.1
size_other_height = 1
size_other_width = 1
size_other_thickness = 0.1

modules = None

class BulkTextSize( pcbnew.ActionPlugin ):
    '''
    Bulk Text Size
    '''

    def defaults( self ):
        self.name = "Bulk Text Size"
        self.category = "Edit "
        self.description = "Bulk Text Size"
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'bulk_text_size.png')


    def Run( self ):

        class Dialog(wx.Dialog):
            def __init__(self, parent):
                wx.Dialog.__init__(self, parent, id=-1, title='Bulk Text Size', size=(500,250))
                self.panel = wx.Panel(self)
                icon=wx.EmptyIcon()
                icon_source=wx.Image(os.path.join(os.path.dirname(__file__),'bulk_text_size.png'),wx.BITMAP_TYPE_PNG)
                icon.CopyFromBitmap(icon_source.ConvertToBitmap())
                self.SetIcon(icon)
                rh={}
                rw={}
                rt={}
                vh={}
                vw={}
                vt={}
                for m in modules:
                    ref = m.Reference()
                    h=ref.GetTextHeight()
                    if not h in rh.keys():
                        rh[h] = 0
                    rh[h] = rh[h] + 1
                    w=ref.GetTextWidth()
                    if not w in rw.keys():
                        rw[w] = 0
                    rw[w] += 1
                    t=ref.GetThickness()
                    if not t in rt.keys():
                        rt[t] = 0
                    rt[t] += 1
                    val = m.Value()
                    h=val.GetTextHeight()
                    if not h in vh.keys():
                        vh[h] = 0
                    vh[h] += 1
                    w=val.GetTextWidth()
                    if not w in vw.keys():
                        vw[w] = 0
                    vw[w] += 1
                    t=val.GetThickness()
                    if not t in vt.keys():
                        vt[t] = 0
                    vt[t] += 1
                size_ref_height = max(rh, key=rh.get)/1000000.0
                size_ref_width = max(rw, key=rw.get)/1000000.0
                size_ref_thickness = max(rt, key=rt.get)/1000000.0
                size_val_height = max(vh, key=vh.get)/1000000.0
                size_val_width = max(vw, key=vw.get)/1000000.0
                size_val_thickness = max(vt, key=vt.get)/1000000.0
                self.clsbtn = wx.Button(self.panel, wx.ID_ANY, 'Close', pos=(150,170))
                self.applybtn = wx.Button(self.panel, wx.ID_ANY, 'apply', pos=(30,170))
                self.labelRef = wx.StaticText(self.panel, wx.ID_ANY, 'Reference (mm)', pos=(100,10))
                self.labelVal = wx.StaticText(self.panel, wx.ID_ANY, 'Value (mm)', pos=(220,10))
                self.labelOther = wx.StaticText(self.panel, wx.ID_ANY, 'Other (mm)', pos=(340,10))
                self.labelModify = wx.StaticText(self.panel, wx.ID_ANY, 'Modify', pos=(30,35))
                self.labelHeight = wx.StaticText(self.panel, wx.ID_ANY, 'Height', pos=(30,60))
                self.labelWidth = wx.StaticText(self.panel, wx.ID_ANY, 'Width', pos=(30,85))
                self.labelThickness = wx.StaticText(self.panel, wx.ID_ANY, 'Thickness', pos=(30,110))
                self.textRefMod = wx.CheckBox(self.panel, wx.ID_ANY, '', pos=(150,35))
                self.textRefMod.SetValue(True)
                self.textRefHeight = wx.TextCtrl(self.panel, wx.ID_ANY, str(size_ref_height), pos=(100,60), style=wx.TE_CENTER)
                self.textRefWidth = wx.TextCtrl(self.panel, wx.ID_ANY, str(size_ref_width), pos=(100,85), style=wx.TE_CENTER)
                self.textRefThickness = wx.TextCtrl(self.panel, wx.ID_ANY, str(size_ref_thickness), pos=(100,110), style=wx.TE_CENTER)
                self.textValMod = wx.CheckBox(self.panel, wx.ID_ANY, '', pos=(270,35))
                self.textValMod.SetValue(True)
                self.textValHeight = wx.TextCtrl(self.panel, wx.ID_ANY, str(size_val_height), pos=(220,60), style=wx.TE_CENTER)
                self.textValWidth = wx.TextCtrl(self.panel, wx.ID_ANY, str(size_val_width), pos=(220,85), style=wx.TE_CENTER)
                self.textValThickness = wx.TextCtrl(self.panel, wx.ID_ANY, str(size_val_thickness), pos=(220,110), style=wx.TE_CENTER)
                self.textOtherMod = wx.CheckBox(self.panel, wx.ID_ANY, '', pos=(390,35))
                self.textOtherMod.SetValue(False)
                self.textOtherHeight = wx.TextCtrl(self.panel, wx.ID_ANY, str(size_other_height), pos=(340,60), style=wx.TE_CENTER)
                self.textOtherWidth = wx.TextCtrl(self.panel, wx.ID_ANY, str(size_other_width), pos=(340,85), style=wx.TE_CENTER)
                self.textOtherThickness = wx.TextCtrl(self.panel, wx.ID_ANY, str(size_other_thickness), pos=(340,110), style=wx.TE_CENTER)
                self.clsbtn.Bind(wx.EVT_BUTTON, self.OnClose)
                self.applybtn.Bind(wx.EVT_BUTTON, self.OnApply)
                self.Bind(wx.EVT_CLOSE,self.OnClose)
                self.applybtn.SetFocus()
            def OnClose(self,e):
                e.Skip()
                self.Close()
            def OnApply(self,e):
                size_ref_height = float(self.textRefHeight.GetValue())
                size_ref_width = float(self.textRefWidth.GetValue())
                size_ref_thickness = float(self.textRefThickness.GetValue())
                size_val_height = float(self.textValHeight.GetValue())
                size_val_width = float(self.textValWidth.GetValue())
                size_val_thickness = float(self.textValThickness.GetValue())
                for m in modules:
                    ref = m.Reference()
                    val = m.Value()
                    if self.textRefMod.GetValue():
                        ref.SetTextHeight(int(size_ref_height *10**6))
                        ref.SetTextWidth(int(size_ref_width *10**6))
                        ref.SetThickness(int(size_ref_thickness *10**6))
                    if self.textValMod.GetValue():
                        val.SetTextHeight(int(size_val_height *10**6))
                        val.SetTextWidth(int(size_val_width *10**6))
                        val.SetThickness(int(size_val_thickness *10**6))
                    items = m.GraphicalItems()
                    if self.textOtherMod.GetValue():
                        for item in items:
                            if item != ref and item != val:
                                cl = item.GetClass()
                                if cl == 'MTEXT':
                                    item.SetTextHeight(int(size_other_height *10**6))
                                    item.SetTextWidth(int(size_other_width *10**6))
                                    item.SetThickness(int(size_other_thickness *10**6))
                pcbnew.Refresh()
                e.Skip()

        board = pcbnew.GetBoard()
        modules = board.GetModules()
        dialog = Dialog(None)
        dialog.Center()
        dialog.ShowModal()
        dialog.Destroy()
        

BulkTextSize().register()
