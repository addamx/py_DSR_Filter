#coding:utf-8

from csv import reader, writer, QUOTE_NONE, DictReader
from re import sub, compile, search
from collections import namedtuple, OrderedDict, defaultdict
from operator import attrgetter
from tkinter import messagebox
import glob
from os import path
from time import localtime, strftime



def loadfiles(inputpath):
    fileslist = OrderedDict()
    #将voyage和文件名绑定
    files = glob.glob('{}/*.csv'.format(inputpath))
    filesCreate = [path.getctime(f) for f in files]
    for i, ct in zip(files, filesCreate):
        voy = ''
        try: 
            g = open(i, encoding = 'utf-8')
            num = next(g).split(';').index('Vessel/Voyage')
            voy = next(g).split(';')[num]
            g.close()
            lct = localtime(ct)
            if voy in [k.split(' ___ ')[0] for k in fileslist.keys()]:
                messagebox.showerror('Warning', 'Duplicate voyage\'file "{}" in {}.\nPlease clear in disk and press "Refresh" button, or remove one of them to the right list.'.format(voy, inputpath))
            fileslist['{} ___ {}'.format(voy, strftime('%H:%M:%S, %d/%m',lct))]=i
        except StopIteration:
            messagebox.showerror('Warning', '"{}" has no valid data at all.'.format(i))
        
    return fileslist

def loadpath():
    with open('dir', 'r')as f:
        inputpath = next(f)[:-1]
    return inputpath
    
def savepath(inputpath):
    with open('dir', 'w')as f:
        save = inputpath+'\n'
        f.writelines(save)
    
# -----------------------------------                
    
def loadconfig():
    with open('data', 'r') as g:
        loadtemplname = ''
        templs = {}
        try:
            loadtemplname = next(g)[:-1]
        except:
            pass
        try:
            for i in next(g)[:-1].split('@'):
                j, k = i.split(':')
                k = k.split('|')
                templs[j] = k
        except (StopIteration):
            pass
    return loadtemplname, templs

def refreshData(curTemplate, templates):
    with open('data', 'w') as n:
        sl = ''
        sl = curTemplate+'\n'
        for k in templates.keys():
            sl = sl + '{}:{}|{}|{}|{}|{}|{}|{}@'.format(k, *templates[k])
        n.writelines(sl)


# -----------------------------------

    
def runPrintOut(tempname, tempf,filterAgent, filterPOT, filterPOD, HCteu, printAgent, printPOD, printFPOD):

    
    HCteu = float(HCteu)
    vList = [filterAgent, filterPOT, filterPOD, printAgent]
    filterAgent, filterPOT, filterPOD, printAgent = [x.upper().replace(' ','') for x in vList]

    printAgents = printAgent.split(',')  # filter out
    if printPOD == 'N': printPOD = False
    if printFPOD == 'N': printFPOD = False
    bkgAgents = filterAgent.split(',')
    
    text = ''
    
    res = []
    headers_bef = []
    headers = []
    
    
    voyage = [x.split(' ___ ')[0] for x in tempf.keys()]
    def dedupe(items):
        seen = set()
        for item in items:
            if item not in seen:
                yield item
                seen.add(item)
    voyage = list(dedupe(voyage))
    
    POL = []
    NextPOD = []
    DischargePort = []
    
    
    
    match_POT = compile(r'^({})'.format(filterPOT.replace(',', '|')))
    match_POD = compile(r'^({})'.format(filterPOD.replace(',', '|')))
    
    for file in tempf.values():
        with open(file, 'r', encoding='utf-8') as f:
            
            f_csv_r = reader(f, delimiter=';', quoting=QUOTE_NONE)
            if not headers:
                headers_bef = next(f_csv_r)[:-1]
                headers_bef.append('NIL')
                
                for h in headers_bef:
                    headers.append(sub('[^a-zA-Z_]', '_', h))
                rownamed = namedtuple('rownamed', headers)
            
            
            
            def gen_sources(s):
                erroline = 0
                errolineNo = []
                errofile = []
                for (n,i) in enumerate(s, start=2):
                    #yield rownamed._make(i)
                    
                    try:
                        yield rownamed._make(i)
                        
                    except TypeError:
                        pass
                        erroline += 1
                        #errolineNo.append(n)
                        #if not (file in errofile):
                        #    errofile.append(file)
                if erroline != 0:
                    pass
                    #print("出错文件: {}".format(errofile))
                    #print('包括第{}行。\n'.format(errolineNo))
            
            for row in gen_sources(f_csv_r):
                if row.Booking_Agent in bkgAgents:
                    matchPOD = match_POD.search(row.Discharge_Port)
                    matchPOT = match_POT.search(row.Next_POD)

                    if filterPOT == '':
                        matchPOT = False
                    if filterPOD == '':
                        matchPOD = False
                    if matchPOD or matchPOT:
                        continue
                    if row.Transhipment_Port in ('CNSHK', 'CNCWN', 'CNYTN', 'CNNSA', 'HKHKG'):
                        row = row._replace(Receipt=row.Loading_Port, Loading_Port=row.Transhipment_Port)
                    row = row._replace(Loading_Port=row.Current)
                    res.append(row)

            temp = []   #已复制过的单号
            addlist = []    #需要复制的行
            for row in res:
                if not (row.Loading_Port in POL):
                    POL.append(row.Loading_Port)
                if not (row.Next_POD in NextPOD):
                    NextPOD.append(row.Next_POD)
                if not (row.Discharge_Port in DischargePort):
                    DischargePort.append(row.Discharge_Port)
            
                if row.Container == "UNASSIGNED" and row.Qty != "1":
                    if row in temp:
                        continue
                    dupbkg = 0
                    for rowN in res:
                        if row.Booking_Reference == rowN.Booking_Reference and row.Pack == rowN.Pack:
                            dupbkg = dupbkg + 1
                    for i in range(int(row.Qty) - dupbkg):
                        addlist.append(row)
                    temp.append(row)
            res.extend(addlist)
    
    
    res = sorted(res, key=attrgetter('Vessel_Voyage', 'Loading_Port', 'Booking_Reference'))


            
    # Save outcome
    def writeResult():
        k = False   #False means no PermissionError or do not Retry.
        try:
            with open('../result.csv', 'w', newline = '', encoding='utf-8') as fc:
                fc_csv = writer(fc)
                fc_csv.writerow(headers_bef[:-1])
                for row in res:
                    fc_csv.writerow(row)
        except PermissionError:
            k = messagebox.askretrycancel('FAIL TO GENERATE "result.csv"', '"result.csv" has been opened and could not be writed. \nPlease close it and press Retry.')
            return k 
        return k
    w_try = writeResult()
    while (w_try == True):
        w_try = writeResult()
    
    
    # Print outcome with filter
    for i in voyage:
        ttl2 = 0
        ttlup2 = 0
        voyGwt = 0

        for j in POL:
            ttl1 = 0
            ttlup1 = 0
            polGwt = 0

            for k in NextPOD:
                podTeu = 0
                podGwt = 0
                ttlup0 = 0
                

                for m in DischargePort:
                    fpodTeu = 0
                    fpodGwt = 0
                    voyUTeu = 0
                
                
                    for row in res:
                        if row.Booking_Agent in printAgents:
                            if hasattr(row,'Teu'):
                                rowTeu = float(row.Teu) #DSR-Teu
                            else:
                                rowTeu = float(row.Teus)    #BSR-Teus
                            if row.Pack == '40HC':
                                rowTeu = HCteu
                            if hasattr(row, 'Gross_Weight'):
                                rowGwt = int(float(row.Gross_Weight))   #DSR-Gross Weight
                            else:
                                rowGwt = int(float(row.Gross_Wgt))  #BSR-Gross Wgt
                            if row.Vessel_Voyage == i:
                                if row.Loading_Port == j:
                                    if row.Next_POD == k:
                                        if row.Discharge_Port == m:
                                            fpodTeu =fpodTeu + rowTeu
                                            fpodGwt = fpodGwt + rowGwt
                                            if row.Container == "UNASSIGNED":
                                                voyUTeu = voyUTeu + rowTeu
                    
                    if fpodTeu != 0:
                        if printFPOD:
                            text = text + 'FPOD###### {} via {}: {}(Teus), {}(Tons)\n'.format(m, k, round(fpodTeu,1), str(fpodGwt).split('.')[0][:-3])
                        podTeu = podTeu + fpodTeu
                        podGwt = podGwt + fpodGwt
                        ttlup0 = ttlup0 + voyUTeu
                
                
                if podTeu != 0:
                    if printPOD:
                        text = text + 'POD## {}: {}(Teus), {}(Tons)\n\n'.format(k, round(podTeu,1), str(podGwt).split('.')[0][:-3])
                    ttl1 = ttl1 + podTeu
                    ttlup1 = ttlup1 + ttlup0
                    polGwt += podGwt

            if ttl1 != 0:
                text = text + '\n{}: Total: {}\tPick UP: {} --- {}(Tons)\n\n'.format(j, round(ttl1,1), round(ttl1-ttlup1,1), str(polGwt).split('.')[0][:-3])
                ttl2 = ttl2 + ttl1
                ttlup2 = ttlup2 + ttlup1
                voyGwt += polGwt


        #if  ttl2 != 0:
        #无论voyage是否没有想过BKG
        text = text + '{}: TOTAL: {}\tPICK UP: {} --- {}(Tons)\n\n'.format(i, round(ttl2,1), round(ttl2 - ttlup2,1), str(voyGwt).split('.')[0][:-3]) + '--------------------------------------------------------------------------\n\n\n\n'
    
    
    
    # -----CheckPOD for res-------
    d = defaultdict(dict)
    reheaders = []

    try:
        with open('./re/{}.csv'.format(tempname), 'r') as f:
            firstLine = [x.strip() for x in(next(f)[:-1]).split(',')]
            firstFac = firstLine[0]
            reheaders = firstLine[1:]
            
            f.seek(0,0)
            f_csv_r = DictReader(f, delimiter=',', quoting=QUOTE_NONE)
             
            for row in f_csv_r:
                for h in reheaders:
                    d[h][row[firstFac].strip()]= row[h].strip()
        lenVoy=max(len(x) for x in reheaders)
    except:    #FileNotFoundError
        pass
        

    if 'lenVoy' in dir():
        for row in res:
            try:
                if d[(row.Vessel_Voyage)[-lenVoy:]][row.Discharge_Port].find(row.Next_POD) == -1 and firstFac.find(row.Next_POD) == -1:
                    text += '{} mismatch FPOD {} to POD {} on {}.\n'.format(row.Booking_Reference, row.Discharge_Port, row.Next_POD, row.Vessel_Voyage)
            except:
                pass    

    

        
    return text         
