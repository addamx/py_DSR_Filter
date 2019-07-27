#!/usr/bin/python
#-*- coding:UTF-8 -*-

from tkinter import *
from tkinter import filedialog,ttk

class MenuEx(ttk.Frame):
    
    def __init__(self, parent=None):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        
        self.initUI()
        
    def initUI(self):
        menubar = Menu(self.parent)
        self.parent.config(menu = menubar)
        self.filemenu = Menu(menubar, tearoff = 0)
        self.templmenu = Menu(menubar, tearoff = 0)
        self.info = Menu(menubar, tearoff = 0)
        
        
        # 2nd menu
        self.filemenu.add_command(label = 'Select Load Path')
        self.templmenu.add_command(label = 'Save Setting')
        self.templmenu.add_separator()
        self.templmenu.add_separator()
        self.info.add_command(label = 'help doc')
        #self.help.add_command(label = 'About')
        
        
        # 3rd menu
        self.deltemplmenu = Menu(self.templmenu, tearoff =0)
        
        # link menus
        menubar.add_cascade(label = 'File', menu = self.filemenu)
        menubar.add_cascade(label = 'Template', menu = self.templmenu)
        menubar.add_cascade(label = '(?)', menu = self.info)

        self.templmenu.add_cascade(label = 'Delete Setting', menu = self.deltemplmenu)
        
        
    
class Resource(ttk.LabelFrame):
    
    def __init__(self, parent=None):
        ttk.LabelFrame.__init__(self, parent)
        self.parent = parent
        self.config(text = 'SOURCE')
        
        self.vPathname = StringVar()
        self.vRslist = StringVar()
        self.vRmlist = StringVar()
        ## Create components
        

        # 1.file list of resoures, only show voyages
        self.pathname = Label(self, textvariable = self.vPathname, width = 40, justify = LEFT)
        self.rslist = Listbox(self, selectmode = EXTENDED, width = 22, listvariable = self.vRslist, activestyle = 'none', height = 12)
        self.rsslb = ttk.Scrollbar(self)
        self.rslist['yscrollcommand'] = self.rsslb.set
        self.rsslb['command'] = self.rslist.yview
        
        # 2. removing list
        self.rmlist = Listbox(self, selectmode = EXTENDED, width = 20, bg = 'gray', listvariable = self.vRmlist, activestyle = 'none', height = 12)
        self.rmslb = ttk.Scrollbar(self)
        self.rmlist['yscrollcommand'] = self.rmslb.set
        self.rmslb['command'] = self.rmlist.yview
        
        # 3. add buttons
        self.btremove = ttk.Button(self, text = '>>', width = 5)
        self.btadd = ttk.Button(self, text = '<<', width = 5)
        self.btrefresh = ttk.Button(self, text = 'Refresh')
        self.btdelete = ttk.Button(self, text = 'Del All', width = 7)
        self.btdelone = ttk.Button(self, text = 'Del Select', width = 9)
        self.btUp = ttk.Button(self, text = ' UP ', width = 5)
        self.btDown = ttk.Button(self, text = 'Down', width = 5)
        
        self.initUI()
        
    def initUI(self):
        self.pathname.grid(row = 0, column = 0, columnspan = 4, sticky= W)
        
        self.btUp.grid(row = 2, column = 0, sticky = S)
        self.btDown.grid(row = 4, column = 0, sticky = N)
        

        self.rslist.grid(row = 1, column = 1, rowspan = 5, sticky=W+E+N+S, pady = 20)
        self.rsslb.grid(row = 1, column = 2, rowspan = 5, sticky=W+E+N+S, pady = 20)
        self.btremove.grid(row = 2, column = 3, sticky = S)
        self.btadd.grid(row = 4, column = 3, sticky = N)
        self.rmlist.grid(row = 1, column = 4, rowspan = 5, sticky=W+E+N+S, pady = 20)
        self.rmslb.grid(row = 1, column = 5, rowspan = 5, sticky=W+E+N+S, pady = 20)
        self.btdelete.grid(row = 9, column = 0, sticky = E+S, pady = 10)
        self.btdelone.grid(row = 9, column = 1, sticky = W+S, pady = 10)
        self.btrefresh.grid(row = 9, column = 3, pady = 10)
        
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(4, weight = 1)
        self.rowconfigure(1, weight = 1)
        self.rowconfigure(3, weight = 1)
        self.rowconfigure(5, weight = 1)

class Filter(ttk.LabelFrame):
    
    def __init__(self, parent=None):
        ttk.LabelFrame.__init__(self, parent)
        self.parent = parent
        self.config(text = 'FILTER/PRINT')
        
        self.vFiltAgent = StringVar()
        self.vFiltPOT = StringVar()
        self.vFiltPOD = StringVar()
        self.vHCteu = StringVar()
        self.vHCteu.set('2')
        
        
        self.lbTemplname = Label(self, width = 40, justify = LEFT, font=('Verdana','10', 'bold'))
        
        self.etFiltAgent = ttk.Entry(self, textvariable = self.vFiltAgent)
        self.etFiltPOT = ttk.Entry(self, textvariable = self.vFiltPOT)
        self.etFiltPOD = ttk.Entry(self, textvariable = self.vFiltPOD)
        
        self.opHCteu = ttk.Combobox(self, textvariable=self.vHCteu, value=['2', '2.25', '2.3', '2.5', '3'], width=3)
        
        
        
        self.vByAgent = StringVar()
        self.vPrintPOD = StringVar()
        self.vPrintFPOD = StringVar()
        
        self.etByAgent = ttk.Entry(self, textvariable = self.vByAgent)
        self.ckPrintPOD = ttk.Checkbutton(self, variable = self.vPrintPOD, onvalue = 'Y', offvalue = 'N', text = 'Print POD')
        self.ckPrintFPOD = ttk.Checkbutton(self, variable = self.vPrintFPOD, onvalue = 'Y', offvalue = 'N', text = 'Print FPOD')
        
        
        self.initUI()
        
    def initUI(self):
    
        self.lbTemplname.grid(row = 0, column = 0, columnspan = 7)
        
        Label(self, text = 'Set Filter in/out').grid(row = 1, column = 0, columnspan = 3)
        Label(self, text = '(In)BkgAgent: ').grid(row = 2, column = 0, sticky = W)
        self.etFiltAgent.grid(row = 2, column = 1)
        Label(self, text = '(Out)POT: ').grid(row = 3, column = 0, sticky = W)
        self.etFiltPOT.grid(row = 3, column = 1)
        Label(self, text = '(Out)POD: ').grid(row = 4, column = 0, sticky = W)
        self.etFiltPOD.grid(row = 4, column = 1)
        Label(self, text = "40HC's teu: ").grid(row = 5, column = 5, sticky = W)

        Label(self, text = '        ').grid(row = 1, column = 4, rowspan = 6)
        
        Label(self, text = 'Set Print result').grid(row = 1, column = 5, columnspan = 2)
        Label(self, text = 'BkgAgent:', width = 8).grid(row = 2, column = 5, sticky = W)
        self.etByAgent.grid(row = 2, column = 6, sticky = W)
        self.ckPrintPOD.grid(row = 3, column = 5, sticky = W)
        self.ckPrintFPOD.grid(row = 4, column = 5, sticky = W)
        self.opHCteu.grid(row = 5, column = 6, sticky = W)
        

        
class PrintOut(ttk.Frame):
    
    def __init__(self, parent=None):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        
        self.txPrint = Text(self, width = '65', font=('Verdana','10', NORMAL))
        self.txScrollbar = ttk.Scrollbar(self)
        self.txPrint['yscrollcommand'] = self.txScrollbar.set
        self.txScrollbar['command'] = self.txPrint.yview
        
        self.btRun = ttk.Button(self, text = '  RUN  ')
        self.btOpRes = ttk.Button(self, text = 'Open')
        self.pbRun = ttk.Progressbar(self, orient='horizontal', mode='indeterminate')
        
        self.initUI()
        
    def initUI(self):
        self.txPrint.grid(row = 0, column = 0, columnspan = 5, sticky=N+S+E+W)
        self.txScrollbar.grid(row = 0, column = 5, sticky=N+S+E+W)
        self.btRun.grid(row = 3, column = 0, sticky=W, padx = 10, pady = 10)
        self.btOpRes.grid(row = 3, column = 1, sticky=E, padx = 10, pady = 10)
        self.pbRun.grid(row = 3, column = 2, sticky=W, padx = 10, pady = 10)
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0,weight=1)


        
if __name__ == '__main__':
    root = Tk()
    pass
    root.mainloop()