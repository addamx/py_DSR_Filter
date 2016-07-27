Set ws = CreateObject("Wscript.Shell")
ws.CurrentDirectory = ".\source"
ws.run "python DSR_Filter.py",vbhide