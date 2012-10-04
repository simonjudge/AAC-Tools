import wx
# Import rewriting libs
import pdb
import os.path, errno, re
from lxml import etree

########################################################################
class MyFileDropTarget(wx.FileDropTarget):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, window):
        """Constructor"""
        wx.FileDropTarget.__init__(self)
        self.window = window
        
    #----------------------------------------------------------------------
    def OnDropFiles(self, x, y, filenames):
        """
        When files are dropped, write where they were dropped and then
        the file paths themselves
        """
        dowrite= False
        doshow= True
        found= False
        self.window.SetInsertionPointEnd()
        for filepath in filenames:
            if os.path.isdir(filepath):
                self.window.updateText( "\nCurrently searching "+ filepath )
                for r,d,f in os.walk(filepath):                                  # Parse any directory, only picking up on grid.xml files.
                    page = os.path.split(r)[1]
                    for files in f:
                        if files.endswith("grid.xml"):
                            pth = os.path.join(r,files)                    
                            tree = etree.parse(pth)                         # Parse the file
                            if(tree.xpath(".//licencekey") != []):
                                found = True
                                self.window.updateText( "\n\nLicence found in " + page)     
                                for bad in tree.xpath("//protectedpicture"):
                                    # Can we get the caption text ?  this is for alerting the user where the problem is
                                    theText = bad.getparent().xpath("(./caption)/text()") 
                                    if (len(theText)!=0):
                                          self.window.updateText("\n\tCheck: " + theText[0])
            if found == False:
                self.window.updateText( "\n\nSorry.\n\n That doesnt look like it was either a Grid 2 User folder\n or there were licenced files in it")



########################################################################
class DnDPanel(wx.Panel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)
        cb = wx.CheckBox(self, label='Remove Licence', pos=(20, 40))
        cb.SetValue(False)
        cb.Bind(wx.EVT_CHECKBOX, self.ShowOrHideTitle)
    
        file_drop_target = MyFileDropTarget(self)
        lbl = wx.StaticText(self, label="Drag your Grid 2 user folder \n in the below window to check for licenced components:")
        self.fileTextCtrl = wx.TextCtrl(self,
                                        style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_READONLY)
        self.fileTextCtrl.SetDropTarget(file_drop_target)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(lbl, 0, wx.ALL, 5)
        sizer.Add(self.fileTextCtrl, 4, wx.EXPAND|wx.ALL, 5)
        sizer.Add(cb, 0, wx.ALIGN_CENTER_HORIZONTAL,0)
        self.SetSizer(sizer)
        
    #----------------------------------------------------------------------
    def SetInsertionPointEnd(self):
        """
        Put insertion point at end of text control to prevent overwriting
        """
        self.fileTextCtrl.SetInsertionPointEnd()
        
    #----------------------------------------------------------------------
    def updateText(self, text):
        """
        Write text to the text control
        """
        self.fileTextCtrl.WriteText(text)
    
    def ShowOrHideTitle(self, e):
        
        sender = e.GetEventObject()
        isChecked = sender.GetValue()
        
        if isChecked:
            return          
        else: 
            return  
    
########################################################################
class DnDFrame(wx.Frame):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, parent=None, title="Grid 2 User Licence Checker",pos=(150,150), size=(450,450))
        self.statusbar = self.CreateStatusBar()
        panel = DnDPanel(self)
        self.Show()

#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = DnDFrame()
    app.MainLoop()