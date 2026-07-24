# Windows List
# Copyright (C) 2026 Hoàng Lon

from scriptHandler import script
from logHandler import log
import wx
import ui
import gui
import api
import controlTypes
import globalPluginHandler
import addonHandler
import globalVars

# For translation
addonHandler.initTranslation()

def disableOnSecureScreen(plugin):
	if globalVars.appArgs.secure:
		return globalPluginHandler.GlobalPlugin
	return plugin

def showModal(factory, *args, **kwargs):
	def run():
		dlg = None
		gui.mainFrame.prePopup()
		try:
			dlg = factory(*args, **kwargs)
			if isinstance(dlg, wx.Dialog):
				dlg.ShowModal()
		finally:
			if isinstance(dlg, wx.Dialog):
				dlg.Destroy()
			gui.mainFrame.postPopup()
	wx.CallAfter(run)

def getWindowsList():
	windows = []
	for obj in api.getDesktopObject().children:
		try:
			name = (obj.name or _("No title")).strip()
			if name and obj.isFocusable and obj.role == controlTypes.Role.WINDOW:
				windows.append((name, obj))
		except Exception:
			log.exception(f"Failed to enumerate window: {obj.name or 'No title'}")
	if not windows:
		ui.message(_("No windows found"))
	return windows

def showWindowsListDialog():
	windows = getWindowsList()
	if windows:
		showModal(WindowsListDialog, windows)

class WindowsListDialog(wx.Dialog):
	def __init__(self, windows):
		self.windows = windows
		super().__init__(gui.mainFrame, title=_("Windows List"))
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.listBox = wx.ListBox(self, choices=[name for name, obj in self.windows])
		if self.windows:
			self.listBox.SetSelection(0)
		sizer.Add(self.listBox, proportion=1, flag=wx.EXPAND | wx.ALL, border=8)
		btns = self.CreateButtonSizer(wx.OK | wx.CANCEL)
		sizer.Add(btns, flag=wx.ALIGN_RIGHT | wx.ALL, border=8)
		self.SetSizerAndFit(sizer)
		self.listBox.Bind(wx.EVT_LISTBOX_DCLICK, self.onActivate)
		self.Bind(wx.EVT_BUTTON, self.onActivate, id=wx.ID_OK)
		self.CentreOnScreen()

	def onActivate(self, evt):
		index = self.listBox.GetSelection()
		self.EndModal(wx.ID_OK)
		if index != wx.NOT_FOUND:
			obj = self.windows[index][1]
			try:
				obj.setFocus()
			except Exception:
				window = self.windows[index][0]
				ui.message(_("Could not switch to {window}").format(window=window))

@disableOnSecureScreen
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	# Input gestures category
	SCRIPT_CATEGORY = _("Windows List")

	@script(description=_("Show windows list dialog"), category=SCRIPT_CATEGORY)
	def script_windowsList(self, gesture):
		showWindowsListDialog()