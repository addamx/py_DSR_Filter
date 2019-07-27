#!/usr/bin/env python
#coding=utf-8

from GUI import *
from function import *
from tkinter import *
from tkinter import simpledialog, messagebox, filedialog
from re import search
from os import remove, walk, path, system
from threading import Thread

# 1. Create GUI ------------------------------




root = Tk()
root.title('DSR Filter 1.31') 
menu = MenuEx(root)
resource = Resource(root)
filterex = Filter(root)
printout = PrintOut(root)
## 1.1 Grid GUI components 
resource.grid(row = 0, column = 0, sticky=N+S+E+W)
filterex.grid(row = 1, column = 0, sticky=N+S+E+W)
printout.grid(row = 0, column = 1, rowspan = 2, sticky=N+S+E+W)

root.columnconfigure(0, weight = 1)
root.columnconfigure(1, weight = 6)
root.rowconfigure(0, weight = 1)
root.rowconfigure(1, weight = 1)
# 2. Create Variable




vPick = StringVar()
vDel = StringVar()

filterex.lbTemplname.config(textvariable = vPick)   #filterex.lbTemplname and templmenu share same textvariable.

vLPath = StringVar()
vSPath = StringVar()

componentlist = [
    filterex.vFiltAgent,
    filterex.vFiltPOT,
    filterex.vFiltPOD,
    filterex.vHCteu,
    filterex.vByAgent,
    filterex.vPrintPOD,
    filterex.vPrintFPOD,
    ]

componentlist_get = lambda x:x.get()
initset = ['', '', '', '2', '', 'N', 'N']
for n,v in zip(componentlist, initset):
    n.set(v)

    
inputpath = ''
tempf = {}
 
# 3. Create Functions ------------------------------

def ConfigGUI(vloadtempl_name, vloadtempl_list):
    if vloadtempl_name == 0:
        vloadtempl_name = vPick.get()
    for x in vloadtempl_list.keys():
        if vloadtempl_name == x:         # when loadtempl_name was found in loadtempl_list)
            for v,cp in zip(vloadtempl_list[x], componentlist):
                cp.set(v)
def cmddeltempl():
    v = vDel.get()
    print('delete Template:',v)
    menu.deltemplmenu.delete(v)
    menu.templmenu.delete(v)
    del loadtempl_list[v]       #update[delete] template list
    if v == vPick.get():    #if delete current selected template, update GUI too.
        vPick.set('')
def cmdaddtempl(name):
    menu.templmenu.insert_radiobutton(2, label = name, variable = vPick, command = lambda : ConfigGUI(0, loadtempl_list))
    menu.deltemplmenu.insert_radiobutton(0, label = name, variable = vDel, command = cmddeltempl)
    
def cmdSavetempl():
    newtempl = simpledialog.askstring('Save Settings as Template', 'Define name of Template: ("a~z"/"A~Z"/"."/"_"/"-")')  
    if newtempl:
        if newtempl in loadtempl_list:
            k = messagebox.askokcancel('Overwrite Message', 'The name already exists. Please confirm if overwrite "{}"'.format(newtempl))
            if k:
                loadtempl_list[newtempl] = [componentlist_get(x) for x in componentlist]
                print('overwrite "{}"'.format(newtempl))
                vPick.set(newtempl)
        elif search(r'[^a-zA-Z0-9_.-]', newtempl):
            messagebox.showerror('Save Failed', 'Only allows to input "a~z"/"A~Z"/"."/"_"/"-", please try again.')
        else:
            loadtempl_list[newtempl] = [componentlist_get(x) for x in componentlist]    #update[add] template list
            cmdaddtempl(newtempl)   #update template's menu 
            vPick.set(newtempl)     #select when save as template
            print('add template "{}"'.format(newtempl))

# 4. Initiating Setup of GUI ------------------------------

inputpath = loadpath()
resource.vPathname.set(inputpath)
loadtempl_name = 0  # record current template name
loadtempl_list = 0
loadtempl_name, loadtempl_list = loadconfig()
if loadtempl_list:      # when loadtempl_list is not empty (data has 2 lines)
    ConfigGUI(loadtempl_name, loadtempl_list)
    for x in loadtempl_list:    ##load template into menu
        cmdaddtempl(x)      ## and create vPick fo show menu&label's name
    vPick.set(loadtempl_name)    #After creating menu, vPick.set() replace loadtempl_name to show value in listbox(rslist)


        
# 4. Bind function and GUI's other component ------------------------------


def cmdRefresh(inputpath):
    global tempf
    global fileslist
    tempf = {}
    fileslist = {}
    fileslist = loadfiles(inputpath)       #开始时的fileslist{'voyage':'path'}
    resource.vRslist.set('')
    resource.vRmlist.set('')
    printout.txPrint.delete(1.0, END)
    if fileslist:
        resource.vRslist.set([v for v in fileslist])
        items = [v for v in fileslist]
        tempf = fileslist.copy()    # Deep copy fileslist not just point to original variable
        
    
def cmdRemove(tempf):
    i = [k for k in resource.rslist.curselection()]
    for voy in [resource.rslist.get(x) for x in i]:
        resource.rmlist.insert(END, voy)
        del tempf[voy]
    resource.vRslist.set([v for v in tempf])
        
def cmdadd(tempf):
    i = [k for k in resource.rmlist.curselection()] #convert to list for reverse
    for voy in [resource.rmlist.get(x) for x in i]:
        tempf[voy] = fileslist[voy]
    resource.vRslist.set([v for v in tempf])
    i.reverse()
    for y in i:
        resource.rmlist.delete(y)

def cmdDelete():
    k = messagebox.askokcancel('Delete all in disk', 'If contine to delete all these voyage\'s CSV files in {}?'.format(inputpath))
    if k:
        for f in fileslist.values():
            remove(f)
    cmdRefresh(inputpath)

def cmdDelone():
    cursel = resource.rslist.curselection()
    cursel = [resource.rslist.get(x) for x in cursel]
    k = messagebox.askokcancel('Delete selected ".CSV" files in disk', 'If contine to delete selected voyage\'s "CSV" files in {}?'.format(inputpath))
    if k:
        for f in cursel:
            remove(fileslist[f])
    cmdRefresh(inputpath)
    
def cmdUp():
    i = resource.rslist.curselection()
    if i != ():
        if i[0] != 0:
            tempfv = [x for x in tempf.keys()] #ordict.keys not support index, must convert to list
            for d, voy in zip(i ,[resource.rslist.get(x) for x in i]): 
                tk = d-1
                tv = tempfv[tk]
                tempfv[tk] = voy
                tempfv[d] = tv
            # sorted tempf according to tempfv
            templist = tempf.copy()
            tempf.clear()
            for v in tempfv:
                item = templist[v]
                tempf[v] = item
            resource.vRslist.set(tempfv)
            resource.rslist.selection_clear(0,END)
            for x in i:
                resource.rslist.selection_set(x-1)
    
def cmdDown():
    i = list(resource.rslist.curselection())# convert list for reserve
    i.reverse()     # reverse before put back
    if i != []:
        if i[0] != len(tempf)-1:
            tempfv = [x for x in tempf.keys()]
            for d, voy in zip(i ,[resource.rslist.get(x) for x in i]): 
                tk = d+1
                tv = tempfv[tk]
                tempfv[tk] = voy
                tempfv[d] = tv
            templist = tempf.copy()
            tempf.clear()
            for v in tempfv:
                item = templist[v]
                tempf[v] = item
            resource.vRslist.set(tempfv)
            resource.rslist.selection_clear(0,END)
            for x in i:
                resource.rslist.selection_set(x+1)
    
def cmdrunPrintOut():
    def getText():
        printout.pbRun.start()
        printout.btRun.config(state='disabled')
        printout.btRun.config(text='Runing...')
        printout.btOpRes.config(state='disabled')
        ttext = runPrintOut(vPick.get(), tempf, *[componentlist_get(x) for x in componentlist])
        printout.txPrint.delete(1.0, END)
        printout.txPrint.insert(1.0, ttext)
        ttext = ''
        printout.pbRun.stop()
        printout.btRun.config(state='active')
        printout.btRun.config(text='RUN')
        printout.btOpRes.config(state='active')
    threadBar = Thread(target = getText)
    threadBar.start()

def cmdOpenRes():
    def OpenRes():
        system("start " + '../result.csv')
    threadOpenRes = Thread(target = OpenRes)
    threadOpenRes.start()
    
def cmdLoadpath():
    global inputpath
    k = filedialog.askdirectory()
    if k:
        inputpath = k
    cmdRefresh(inputpath)
    resource.vPathname.set(inputpath)

def cmdOpenhelp():
    system('start ' + '../doc/help.pdf')
    
    
        
## 4.2 function_source
menu.filemenu.entryconfigure(0, command = cmdLoadpath)
menu.templmenu.entryconfigure(0, command = cmdSavetempl)
menu.info.entryconfigure(0, command = cmdOpenhelp)

fileslist = loadfiles(inputpath)    # initiating filelist
cmdRefresh(inputpath)       # initiating fileListBox and labelanme

resource.btrefresh.config(command = lambda : cmdRefresh(inputpath))
resource.btremove.config(command = lambda : cmdRemove(tempf))
resource.btadd.config(command = lambda : cmdadd(tempf))
resource.btdelete.config(command = cmdDelete)
resource.btdelone.config(command = cmdDelone)
resource.btUp.config(command = cmdUp)
resource.btDown.config(command = cmdDown)

printout.btRun.config(command = cmdrunPrintOut)
printout.btOpRes.config(command = cmdOpenRes)






# ====================================================

root.mainloop()


#print(vPick.get(), loadtempl_list)
refreshData(vPick.get(), loadtempl_list)
savepath(inputpath)
