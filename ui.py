#!/usr/bin/env python3
from ast import Return
from asyncio.windows_events import NULL
import os
import sys
import glob
import json
import base64
import shutil
import subprocess
# import tk/tcl
import tkinter as tk 
from tkinter import ttk
from tkinter.filedialog import *
from tkinter import *
from tkinter import scrolledtext
from tkinter.simpledialog import askstring
from ttkbootstrap import Style  # use ttkbootstrap theme
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
# from bs4 import BeautifulSoup
import requests
# using threading in some function
import threading
import time
import webbrowser
# add pyscripts into sys path
sys.path.append(os.path.abspath(os.path.dirname(sys.argv[0])) + "\\pyscripts")
# import functions I modified
import utils
import sn
import verifysn
import ozip_decrypt
import get_miui
import vbpatch
import imgextractor
import sdat2img
import fspatch
import img2sdat


# Flag
DEBUG = False                    # Display debugging information
HIDE_CONSOLE = False            # Hidden console
MENUBAR = True                  # Menu Bar
USEMYLOGO = True                # Use your own logo
TEXTREADONLY = True             # Text box read only
TEXTSHOWBANNER = False           # Show the character painting of the text box
USEMYSTD = False                # Output redirection to Text control
SHOWSHIJU = False               # Show
USESTATUSBAR = True             # Use the status bar (not easy to use)
VERIFYPROG = False              # Program verification (originally planned to rot money)
ALLOWMODIFYCMD = True           # Provide a box that can enter any command
EXECPATH = ".\\bin"             # Temporarily add executable program directory to system variables
LICENSE = "Apache 2.0"          # Program open source protocol

# Check Update
def checkToolUpdate():
    onlineVersion = utils.getOnlineVersion()
    if onlineVersion > VERSION :
        showinfo("For updates available, please go to the GitHub page to view (" + VERSION + " -> " + onlineVersion + ")")
    else :
        showinfo("It is currently the latest version (" + VERSION + ")")

# Verify
if(VERIFYPROG):
    VERIFYCODE = ".\\bin\\VERIFYCODE"
    if(os.access(VERIFYCODE, os.F_OK)):
        vf2code = verifysn.verifycode(sn.get_board_id())
        with open(VERIFYCODE) as vcode:
            vf = vcode.readline()
            f = open(VERIFYCODE, "r")
            vfcode = f.readline()
        if(vf2code == vfcode):
            print("Verify Successfully...")
        else:
            while(verifysn.Verify()==False):
                print("Verify -->")
            print("Save code ...")
            with open(VERIFYCODE,"w") as f:
                f.write(vf2code.encode("utf-8").decode("utf-8"))
    else:
        try:
            print("Verify online -->")
            snurl = "https://gitee.com/affggh/nh4-verify/raw/master/all.json"
            bypass_systemProxy = { "http" : None,
                                   "https" : None}
            fetchv = requests.get(snurl, proxies=bypass_systemProxy)
            fetchvjason = fetchv.json()
            boardid = sn.get_board_id()
            vfcode = fetchvjason[boardid]
            vf2code = verifysn.verifycode(sn.get_board_id())
            if(vfcode == vf2code):
                print("Verify Successfully...")
                print("Save code ...")
                with open(VERIFYCODE,"w") as f:
                    f.write(vfcode.encode("utf-8").decode("utf-8"))
            else:
                print("Verify Failed...")
                print("please input your active code : \n")
                while(verifysn.Verify()==False):
                    print("Verify -->")
        except:
            vf2code = verifysn.verifycode(sn.get_board_id())
            print("Verify Failed...")
            print("please input your active code : \n")
            while(verifysn.Verify()==False):
                print("Verify -->")
            print("Save code ...")
            with open(VERIFYCODE,"w") as f:
                f.write(vf2code.encode("utf-8").decode("utf-8"))

# Var
VERSION = utils.getCurrentVersion()
AUTHOR = "affggh"
WINDOWTITLE = "NH4RomTool " + " [Version: " + VERSION + "] [author: " + AUTHOR + "]"
THEME = "minty"  # 设置默认主题
LOGOICO = ".\\bin\\logo.ico"
BANNER = ".\\bin\\banner"
TEXTFONT = ['Arial', 5]
LOCALDIR = os.path.abspath(os.path.dirname(sys.argv[0]))

# CheckUpdate
threading.Thread(target=checkToolUpdate).start()


# ui config This is for repack tool to detect
if os.access(LOCALDIR+os.sep+"config.json", os.F_OK):
    with open("config.json", encoding='utf-8') as f:
        global UICONFIG
        UICONFIG = json.load(f)
else:
    print("config.json is missing")
    sys.exit()

if(USESTATUSBAR):
    STATUSSTRINGS = ['-', '\\', '|', '/', '-']

if(EXECPATH):
    utils.addExecPath(EXECPATH)

if(HIDE_CONSOLE):  # 隐藏控制台
    utils.hideForegroundWindow

style = Style(theme=THEME)

# Begin of window
root = style.master

width = 1240
height = 480

if(ALLOWMODIFYCMD):
    height += 40
if USESTATUSBAR:
    height += 80

root.geometry("%sx%s" %(width,height))
# root.resizable(0,0) # 设置最大化窗口不可用
root.title(WINDOWTITLE)

# Set images
LOGOIMG = tk.PhotoImage(file=LOCALDIR + ".\\bin\\logo.png")
ALIPAYIMG = tk.PhotoImage(file=LOCALDIR + ".\\bin\\alipay.png")
WECHATIMG = tk.PhotoImage(file=LOCALDIR + ".\\bin\\wechat.png")
ALIREDPACIMG = tk.PhotoImage(file=LOCALDIR + ".\\bin\\zfbhb.png")
DEFAULTSTATUS = tk.PhotoImage(file=LOCALDIR + ".\\bin\\processdone.png")

global WorkDir
WorkDir = False

# Var
filename = tk.StringVar()
directoryname = tk.StringVar()
inputvar = tk.StringVar()
if(ALLOWMODIFYCMD):
    USERCMD = tk.StringVar()

# from https://www.i4k.xyz/article/weixin_49317370/108878373
class myStdout():	# 重定向类
    def __init__(self):
    	# 将其备份
        self.stdoutbak = sys.stdout		
        self.stderrbak = sys.stderr
        # 重定向
        sys.stdout = self
        sys.stderr = self

    def write(self, info):
        # info信息即标准输出sys.stdout和sys.stderr接收到的输出信息
        # text.insert('end', info)	# 在多行文本控件最后一行插入print信息
        # text.update()	# 更新显示的文本，不加这句插入的信息无法显示
        # text.see(tkinter.END)	# 始终显示最后一行，不加这句，当文本溢出控件最后一行时，不会自动显示最后一行
        if(TEXTREADONLY):
            text.configure(state='normal')
        text.insert(END,"[%s]" %(utils.get_time()) + "%s" %(info))
        text.update() # 实时返回信息
        text.yview('end')
        if(TEXTREADONLY):
            text.configure(state='disable')

    def restoreStd(self):
        # 恢复标准输出
        sys.stdout = self.stdoutbak
        sys.stderr = self.stderrbak


class MyThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()
        
        self.func = func
        self.args = args
        
        self.setDaemon(True)
        self.start()    # 在这里开始
        
    def run(self):
        self.func(*self.args)
    


def logo():
    utils.chLocal()
    root.iconbitmap(LOGOICO)

if(USEMYLOGO):
    logo()

def VisitMe():
    webbrowser.open("https://github.com/affggh")

def showinfo(textmsg):
    if(TEXTREADONLY):
        text.configure(state='normal')
    text.insert(END,"[%s]" %(utils.get_time()) + "%s" %(textmsg) + "\n")
    text.update() # 实时返回信息
    text.yview('end')
    if(TEXTREADONLY):
        text.configure(state='disable')

def showontime(textmsg):
    if(TEXTREADONLY):
        text.configure(state='normal')
    # text.delete(1.0, END)
    text.insert(END,"[%s]" %(utils.get_time()) + "%s" %(textmsg) + "\n")
    text.update() # 实时返回信息
    if(TEXTREADONLY):
        text.configure(state='disable')

def runcmd(cmd):
    try:
        ret = subprocess.Popen(cmd,shell=False,
                 stdin=subprocess.PIPE,
                 stdout=subprocess.PIPE,
                 stderr=subprocess.STDOUT)
        for i in iter(ret.stdout.readline,b""):
            showinfo(i.decode("utf-8","ignore").strip())
    except subprocess.CalledProcessError as e:
        for i in iter(e.stdout.readline,b""):
            showinfo(e.decode("utf-8","ignore").strip())

def runontime(cmd):
    try:
        ret = subprocess.Popen(cmd,shell=False,
                 stdin=subprocess.PIPE,
                 stdout=subprocess.PIPE,
                 stderr=subprocess.STDOUT)
        for i in iter(ret.stdout.readline,b""):
            showontime(i.decode("utf-8","ignore").strip())
            time.sleep(1)
    except subprocess.CalledProcessError as e:
        for i in iter(e.stdout.readline,b""):
            showontime(e.decode("utf-8","ignore").strip())
            time.sleep(1)

def returnoutput(cmd):
    try:
        ret = subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)
        return(ret.decode())
    except subprocess.CalledProcessError as e:
        return(e.decode())

def showbanner():
    if(TEXTSHOWBANNER):
        with open(BANNER, "r") as b:
            for i in b.readlines():
                showinfo(i.replace('\n',''))

def cleaninfo():
    if(TEXTREADONLY):
        text.configure(state='normal')
    text.delete(1.0, END)  # 清空text
    # text.image_create(END,image=LOGOIMG)
    # text.insert(END,"\n")
    showbanner()
    if(TEXTREADONLY):
        text.configure(state='disable')

def selectFile():
    filepath = askopenfilename()                   # 选择打开什么文件，返回文件名
    filename.set(filepath.replace('/', '\\'))      # 设置变量filename的值
    showinfo("Select the file to: %s" %(filepath.replace('/', '\\')))

def selectDir():
    dirpath = askdirectory()                   # 选择文件夹
    directoryname.set(dirpath.replace('/', '\\'))
    showinfo("Select folder as a folder: %s" %(dirpath.replace('/', '\\')))

def about():
    root2 = tk.Toplevel()
    curWidth = 300
    curHight = 180
    # 获取屏幕宽度和高度
    scn_w, scn_h = root.maxsize()
    # print(scn_w, scn_h)
    # 计算中心坐标
    cen_x = (scn_w - curWidth) / 2
    cen_y = (scn_h - curHight) / 2
    # print(cen_x, cen_y)

    # 设置窗口初始大小和位置
    size_xy = '%dx%d+%d+%d' % (curWidth, curHight, cen_x, cen_y)
    root2.geometry(size_xy)
    #root2.geometry("300x180")
    root2.resizable(0,0) # 设置最大化窗口不可用
    root2.title("About script and author information")
    aframe1 = Frame(root2, relief=FLAT, borderwidth=1)
    aframe2 = Frame(root2, relief=FLAT, borderwidth=1)
    aframe1.pack(side=BOTTOM, expand=YES, pady=3)
    aframe2.pack(side=BOTTOM, expand=YES, pady=3)
    ttk.Button(aframe1, text='Visit the author homepage', command=VisitMe,style='primiary.Outline.TButton').pack(side=LEFT, expand=YES, padx=5)
    ttk.Button(aframe1, text=' Give the author ', command=VisitMe,style='success.TButton').pack(side=LEFT, expand=YES, padx=5)
    ttk.Label(aframe2, text='沼_Rom工具箱 Version %s\nGUI Written by python tk/tcl\nTheme by ttkbootstrap\n%s Copyright(R) Apache 2.0 LICENSE'%(VERSION,AUTHOR)).pack(side=BOTTOM, expand=NO, pady=3)
    utils.chLocal()
    
    imgLabe2 = ttk.Label(aframe2,image=LOGOIMG)#把图片整合到标签类中
    imgLabe2.pack(side=TOP, expand=YES, pady=3)
    root2.mainloop()

def userInputWindow(title='输入文本'):

    inputWindow = tk.Toplevel()
    curWidth = 400
    curHight = 120
    # 获取屏幕宽度和高度
    scn_w, scn_h = root.maxsize()
    # print(scn_w, scn_h)
    # 计算中心坐标
    cen_x = (scn_w - curWidth) / 2
    cen_y = (scn_h - curHight) / 2
    # print(cen_x, cen_y)

    # 设置窗口初始大小和位置
    size_xy = '%dx%d+%d+%d' % (curWidth, curHight, cen_x, cen_y)
    inputWindow.geometry(size_xy)
    #inputWindow.geometry("300x180")
    inputWindow.resizable(0,0) # 设置最大化窗口不可用
    inputWindow.title(title)
    ent = ttk.Entry(inputWindow,textvariable=inputvar,width=50)
    ent.pack(side=TOP, expand=YES, padx=5)
    ttk.Button(inputWindow, text='确认', command=inputWindow.destroy,style='primiary.Outline.TButton').pack(side=TOP, expand=YES, padx=5)
    inputWindow.wait_window()

def fileChooseWindow(tips):
    chooseWindow = tk.Toplevel()
    curWidth = 500
    curHight = 180
    # 获取屏幕宽度和高度
    scn_w, scn_h = root.maxsize()
    # print(scn_w, scn_h)
    # 计算中心坐标
    cen_x = (scn_w - curWidth) / 2
    cen_y = (scn_h - curHight) / 2
    # print(cen_x, cen_y)

    # 设置窗口初始大小和位置
    size_xy = '%dx%d+%d+%d' % (curWidth, curHight, cen_x, cen_y)
    chooseWindow.geometry(size_xy)
    #chooseWindow.geometry("300x180")
    chooseWindow.resizable(0,0) # 设置最大化窗口不可用
    chooseWindow.title(tips)
    ent = ttk.Entry(chooseWindow,textvariable=filename,width=50)
    ent.pack(side=TOP, expand=NO, padx=0, pady=20)
    ttk.Button(chooseWindow, text='confirm', width=15, command=chooseWindow.destroy,style='primiary.Outline.TButton').pack(side=RIGHT, expand=YES, padx=5, pady=5)
    ttk.Button(chooseWindow, text='Select a document', width=15, command=lambda:[selectFile(),chooseWindow.destroy()],style='primiary.TButton').pack(side=RIGHT, expand=YES, padx=5,  pady=5)
    chooseWindow.wait_window()

def dirChooseWindow(tips):
    chooseWindow = tk.Toplevel()
    curWidth = 400
    curHight = 120
    # 获取屏幕宽度和高度
    scn_w, scn_h = root.maxsize()
    # print(scn_w, scn_h)
    # 计算中心坐标
    cen_x = (scn_w - curWidth) / 2
    cen_y = (scn_h - curHight) / 2
    # print(cen_x, cen_y)

    # 设置窗口初始大小和位置
    size_xy = '%dx%d+%d+%d' % (curWidth, curHight, cen_x, cen_y)
    chooseWindow.geometry(size_xy)
    #chooseWindow.geometry("300x180")
    chooseWindow.resizable(0,0) # 设置最大化窗口不可用
    chooseWindow.title(tips)
    ent = ttk.Entry(chooseWindow,textvariable=directoryname,width=50)
    ent.pack(side=TOP, expand=NO, padx=0, pady=20)
    ttk.Button(chooseWindow, text='confirm', width=15, command=chooseWindow.destroy,style='primiary.Outline.TButton').pack(side=RIGHT, expand=YES, padx=5, pady=5)
    ttk.Button(chooseWindow, text='Select a folder', width=15, command=lambda:[selectDir(),chooseWindow.destroy()],style='primiary.TButton').pack(side=RIGHT, expand=YES, padx=5,  pady=5)
    chooseWindow.wait_window()

def change_theme(var):
    if(DEBUG):
        print("change Theme : " + var)
    showinfo("Set the theme is : " + var)
    style = Style(theme=var)
    style.theme_use()

def getWorkDir():
    x = table.get_children()
    for item in x:
        table.delete(item)
    d = utils.listDirHeader('.\\','NH4_')
    for item in d:
        table.insert('','end',values=item)

def clearWorkDir():
    if not (WorkDir):
        showinfo("No directory is currently selected")
    else:
        showinfo("Will clean up: " + WorkDir)
        try:
            removeDir_EX(os.getcwd() + '\\' + WorkDir)
            # showinfo(os.getcwd() + '\\' + WorkDir)
        except IOError:
            showinfo("Failure to clean up, please check if there is a program that is occupying it ...?")
        else:
            showinfo("The cleanup is successful, and it is refreshing the working catalog")


# removeButSaveCurrentDir  add by azwhikaru 20220329
def removeDir_EX(workDirEX):
    for root, dirs, files in os.walk(workDirEX, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

def statusend():
    if(USESTATUSBAR):
        global STATUSON
        STATUSON = True
        statusthread.join()
        statusbar['image'] = DEFAULTSTATUS
    else:
        pass

def __statusstart():
    while(True):
    #for i in range(len(STATUSSTRINGS)):
        for i in range(33):  # 33是图片帧数
        #statusbar['text'] = STATUSSTRINGS[i]
            photo = PhotoImage(file=LOCALDIR + '\\bin\\processing.gif', format='gif -index %i' %(i))
            statusbar['image'] = photo
            time.sleep(1/18)
            global STATUSON
        if(STATUSON):
            break

def statusstart():
    if(USESTATUSBAR):
        global STATUSON
        STATUSON = False
        global statusthread
        statusthread = threading.Thread(target=__statusstart)
        statusthread.start()
    else:
        pass

def SelectWorkDir():
    item_text = ['']
    for item in table.selection():
        item_text = table.item(item,"values")
    if(item_text[0]!=""):
        global WorkDir
        WorkDir = item_text[0]
        showinfo("Select the working directory as: %s" %(WorkDir))

def ConfirmWorkDir():
    if not (WorkDir):
        showinfo("Warning : Please select a directory")
    else:
        tabControl.select(tab2)

def tableClicked(event):
    SelectWorkDir()

def rmWorkDir():
    if(WorkDir):
        showinfo("Delete directory: %s" %(WorkDir))
        shutil.rmtree(WorkDir)
    else:
        showinfo("Error : The folder to be deleted does not exist")
    getWorkDir()

def mkWorkdir():
    userInputWindow()
    showinfo("User input: %s" %(inputvar.get()))
    utils.mkdir("NH4_" + "%s" %(inputvar.get()))
    getWorkDir()

def detectFileType():
    fileChooseWindow("Test file type")
    if(os.access(filename.get(), os.F_OK)):
        showinfo("The file format is : ")
        runcmd("gettype -i %s" %(filename.get()))
    else:
        showinfo("Error : file does not exist")

def ozipDecrypt():
    fileChooseWindow("解密ozip")
    if(os.access(filename.get(), os.F_OK)):
        ozip_decrypt.main("%s" %(filename.get()))
    else:
        showinfo("Error : file does not exist")

def __ozipEncrypt():
    fileChooseWindow("Encrypted OZIP")
    if(os.access(filename.get(), os.F_OK)):
        statusstart()
        runcmd("zip2ozip "+filename.get())
        statusend()
    else:
        showinfo("Error : file does not exist")

def ozipEncrypt():
    threading.Thread(target=__ozipEncrypt).start()

def getMiuiWindow():
    def __downloadurl(url):
        webbrowser.open(url)

    def downloadurl(url):
        T = threading.Thread(target=__downloadurl(url))
        T.start()

    def downloadMiuiRom():
        getmiuiWindow.destroy()
        url = get_miui.get("%s" %(DEVICE_CODE.get()), 
                           "%s" %(regionselect.get()), 
                           "%s" %(packagetype.get()), 
                           "%s" %(ver.get()))
        utils.thrun(downloadurl(url))

    def showurl():
        url = get_miui.get("%s" %(DEVICE_CODE.get()), "%s" %(regionselect.get()), "%s" %(packagetype.get()), "%s" %(ver.get()))
        showinfo("url : " + url)
    getmiuiWindow = tk.Toplevel()
    curWidth = 260
    curHight = 380
    # 获取屏幕宽度和高度
    scn_w, scn_h = root.maxsize()
    # print(scn_w, scn_h)
    # 计算中心坐标
    cen_x = (scn_w - curWidth) / 2
    cen_y = (scn_h - curHight) / 2
    # print(cen_x, cen_y)

    # 设置窗口初始大小和位置
    size_xy = '%dx%d+%d+%d' % (curWidth, curHight, cen_x, cen_y)
    getmiuiWindow.geometry(size_xy)
    #getmiuiWindow.geometry("300x180")
    getmiuiWindow.resizable(0,0) # 设置最大化窗口不可用
    getmiuiWindow.title("MIUI latest ROM acquisition program")
    DEVICE_CODE = tk.StringVar()
    ttk.Label(getmiuiWindow,text="Device development code").pack(side=TOP, expand=NO, padx=5, pady=10)
    ent = ttk.Entry(getmiuiWindow,textvariable=DEVICE_CODE,width=25)
    ent.pack(side=TOP, expand=NO, padx=5)
    regionselect = tk.StringVar()
    regions = ['CN', 'RU', 'Global', 'ID', 'IN', 'EEA', 'TR', 'TW', 'JP', 'SG']
    ttk.Label(getmiuiWindow,text="area").pack(side=TOP, expand=NO, padx=5, pady=10)
    comboxlist = ttk.Combobox(getmiuiWindow, textvariable=regionselect, width=23)
    comboxlist["values"]=(regions)
    comboxlist.current(0) # 选择第一个
    comboxlist.pack(side=TOP, expand=NO, padx=5)
    
    packagetype = tk.StringVar()
    types = ['recovery', 'fastboot']
    ttk.Label(getmiuiWindow,text="type").pack(side=TOP, expand=NO, padx=5, pady=10)
    comboxlist2 = ttk.Combobox(getmiuiWindow, textvariable=packagetype, width=23)
    comboxlist2["values"]=(types)
    comboxlist2.current(0) # 选择第一个
    comboxlist2.pack(side=TOP, expand=NO, padx=5)
    
    ver = tk.StringVar()
    vers = ['stable', 'beta']
    ttk.Label(getmiuiWindow,text="Stable version/development version").pack(side=TOP, expand=NO, padx=5, pady=10)
    comboxlist3 = ttk.Combobox(getmiuiWindow, textvariable=ver, width=23)
    comboxlist3["values"]=(vers)
    comboxlist3.current(0) # 选择第一个
    comboxlist3.pack(side=TOP, expand=NO, padx=5)
    ttk.Button(getmiuiWindow, text='confirm', width=10, command=lambda:[showurl(),getmiuiWindow.destroy()],style='primiary.Outline.TButton').pack(side=LEFT, expand=YES, padx=10)
    ttk.Button(getmiuiWindow, text='download', width=10, command=downloadMiuiRom,style='primiary.TButton').pack(side=LEFT, expand=YES, padx=10)
    getmiuiWindow.wait_window()

def __unzipfile():
    if(WorkDir):
        fileChooseWindow("Choose a file to decompress")
        if(os.access(filename.get(), os.F_OK)):
            showinfo("Files are being decompressed: " + filename.get())
            statusstart()
            MyThread(utils.unzip_file(filename.get(), WorkDir + "\\rom"))
            statusend()
            showinfo("Decompression complete")
        else:
            showinfo("Error : file does not exist")
    else:
        showinfo("Error : Please select the working directory first")

def unzipfile():
    if(WorkDir):
        if(os.access(WorkDir + "\\rom", os.F_OK)):
            shutil.rmtree(WorkDir + "\\rom")
    threading.Thread(target=__unzipfile).start()

def __zipcompressfile():
    showinfo("Enter the file name generated")
    userInputWindow()
    if(WorkDir):
        showinfo("Being compressed : " + inputvar.get() + ".zip")
        statusstart()
        MyThread(utils.zip_file(inputvar.get()+".zip", WorkDir + "\\rom"))
        statusend()
        showinfo("Compress")
    else:
        showinfo("Error : Please select the working directory first")

def zipcompressfile():
    threading.Thread(target=__zipcompressfile).start()

def __xruncmd(event):
    cmd = USERCMD.get()
    runcmd("busybox ash -c \"%s\"" %(cmd))
    usercmd.delete(0, 'end')

# Parse Payload.bin add by azwhikaru 20220319
def __parsePayload():
    fileChooseWindow("Payload.bin")
    if(os.access(filename.get(), os.F_OK)):
        statusstart()
        data = returnoutput("bin/parsePayload.exe " + filename.get())
        datadict = dict(json.loads(data.replace("\'","\"")))
        showinfo("Payload file resolution results are as follows")
        showinfo("        File hash value : %s" %(utils.bytesToHexString(base64.b64decode(datadict["FILE_HASH"]))))
        showinfo("        File size     : %s" %(datadict["FILE_SIZE"]))
        showinfo("        METADATA HASH: %s" %(utils.bytesToHexString(base64.b64decode(datadict["METADATA_HASH"]))))
        showinfo("        METADATA 大小: %s" %(datadict["METADATA_SIZE"]))
        showinfo("  Note: HAT value type is SHA256")
        statusend()
    else:
        showinfo("Error : file does not exist")

def parsePayload():
    showinfo("Analyze the Payload file")
    threading.Thread(target=__parsePayload, daemon=True).start()   # 开一个子线程防止卡住

def patchvbmeta():
    fileChooseWindow("Select VBMETA file")
    if(os.access(filename.get(), os.F_OK)):
        if(vbpatch.checkMagic(filename.get())):
            flag = vbpatch.readVerifyFlag(filename.get())
            if(flag==0):
                showinfo("The AVB is detected to open the state, and it is closed ...")
                vbpatch.disableAVB(filename.get())
            elif(flag==1):
                showinfo("After detecting only the DM verification, the AVB is being closed...")
                vbpatch.disableAVB(filename.get())
            elif(flag==2):
                showinfo("Test that the AVB verification has been closed and is opening...")
                vbpatch.restore(filename.get())
            else:
                showinfo("unknown mistake")
        else:
            showinfo("The file is not a VBMETA file")
    else:
        showinfo("file does not exist")

def patchfsconfig():
    dirChooseWindow("Choose the directory you want to pack")
    fileChooseWindow("Select fs_config file")
    fspatch.main(directoryname.get(), filename.get())
    showinfo("Renovate")

def xruncmd():
    cmd = USERCMD.get()
    runcmd("busybox ash -c \"%s\"" %(cmd))
    usercmd.delete(0, 'end')

def __smartUnpack():
    fileChooseWindow("Select the file to be intelligently packaged")
    if(WorkDir):
        if(os.access(filename.get(),os.F_OK)):
            filetype = returnoutput("gettype -i " + filename.get()).replace('\r\n', '')  
            # for windows , end of line basicly is \x0a\x0d which is \r\n
            showinfo("Intelligent recognition file type is :  " + filetype)
            unpackdir = os.path.abspath(WorkDir + "/" + filetype)
            if filetype == "ozip":
                showinfo("Decrypting OZIP")
                def __dozip():
                    statusstart()
                    ozip_decrypt.main(filename.get())
                    showinfo("Decrypt")
                    statusend()
                th = threading.Thread(target=__dozip)
                th.start()
            # list of create new folder
            if filetype == "ext" or filetype == "erofs":
                dirname = os.path.basename(filename.get()).split(".")[0]
                def __eext():
                    showinfo("Underplay : " + filename.get())
                    showinfo("Use imgextractor")
                    statusstart()
                    imgextractor.Extractor().main(filename.get(),WorkDir + os.sep + dirname + os.sep + os.path.basename(filename.get()).split('.')[0])
                    statusend()
                def __eerofs():
                    showinfo("Underplay : " + filename.get())
                    showinfo("Use Erofsunpackrust")
                    statusstart()
                    runcmd("erofsUnpackRust.exe " + filename.get() + " " + WorkDir + os.sep + dirname)
                    statusend()
                showinfo("Create an unpacking directory in the working directory : " + dirname)
                if os.path.isdir(os.path.abspath(WorkDir) + "/" + dirname):
                    showinfo("The folder exists and is deleted")
                    shutil.rmtree(os.path.abspath(WorkDir) + "/" + dirname)
                utils.mkdir(os.path.abspath(WorkDir) + "/" + dirname)
                
                if filetype == "ext":
                    th = threading.Thread(target=__eext)
                    th.start()
                if filetype == "erofs":
                    th = threading.Thread(target=__eerofs)
                    th.start()
                    
            else:
                def __dpayload():
                    statusstart()
                    t = threading.Thread(target=runcmd, args=["python .\\bin\\payload_dumper.py %s --out %s\\payload" %(filename.get(),WorkDir)], daemon=True)
                    t.start()
                    t.join()
                    statusend()
                for i in ["super", "dtbo", "boot", "payload"]:
                    if filetype == i:
                        showinfo("Create an unpacking directory in the working directory :  "+ i)
                        if os.path.isdir(unpackdir):
                            showinfo("The folder exists and is deleted")
                            shutil.rmtree(unpackdir)
                        utils.mkdir(unpackdir)
                        if i == "payload":
                            showinfo("Packing Payload")
                            th = threading.Thread(target=__dpayload)
                            th.start()
                        if i == "boot":
                            showinfo("BOOT is being unpacking")
                            os.chdir(unpackdir)
                            runcmd("unpackimg.bat --local %s" %(filename.get()))
                            os.chdir(LOCALDIR)
                        if i == "dtbo":
                            showinfo("Use mkdtboimg packaging")
                            runcmd("mkdtboimg.exe dump " + filename.get() + " -b " + unpackdir + "\\dtb")
                        if i == "super":
                            showinfo("Unlock with LPUNPACK")
                            def __dsuper():
                                statusstart()
                                runcmd("lpunpack " + filename.get() + " " + unpackdir)
                                statusend()
                            th = threading.Thread(target=__dsuper)
                            th.start()
                if filetype == "sparse":
                    showinfo("The file type is Sparse, and converted to RAW DATA using SIMG2IMG to RAW DATA")
                    def __dsimg2img():
                        statusstart()
                        utils.mkdir(WorkDir + "\\rawimg")
                        runcmd("simg2img " + filename.get() + " " +WorkDir+"\\rawimg\\"+ os.path.basename(filename.get()))
                        showinfo("sparse image 转换结束")
                        statusend()
                    th = threading.Thread(target=__dsimg2img)
                    th.start()
                if filetype == "dat":
                    showinfo("Detect DAT, use sdat2img and automatically select the transfer.list file in the directory where the file is located")
                    def __dsdat():
                        pname = os.path.basename(filename.get()).split(".")[0]
                        transferpath = os.path.abspath(os.path.dirname(filename.get()))+os.sep+pname+".transfer.list"
                        if os.access(transferpath, os.F_OK):
                            statusstart()
                            sdat2img.main(transferpath, filename.get(), WorkDir+os.sep+pname+".img")
                            statusend()
                            showinfo("SDAT has been converted to IMG")
                        else:
                            showinfo("Can't find the corresponding transfer.list file in the directory where the DAT file is located")
                    th = threading.Thread(target=__dsdat)
                    th.start()
                if filetype == "br":
                    showinfo("Detect BR format, use brotli to decompress")
                    def __dbr():
                        pname = os.path.basename(filename.get()).replace(".br", "")
                        if os.access(filename.get(), os.F_OK):
                            statusstart()
                            runcmd("brotli -d "+filename.get() +" "+ WorkDir+os.sep+pname)
                            statusend()
                            showinfo("The BR file has been decompressed")
                        else:
                            showinfo("Shocked, how could the file exist?")
                    th = threading.Thread(target=__dbr)
                    th.start()
                if filetype == "vbmeta":
                    showinfo("The VBMTEA is detected. This file does not support the packaging and packaging. Please go to other tools to modify")
                if filetype == "dtb":
                    showinfo("Use Device Tree Compiler to convey the counter -compilation DTB-> DTS")
                    dtname = os.path.basename(filename.get())
                    runcmd("dtc -q -I dtb -O dts " + filename.get() +" -o " + WorkDir + os.sep + dtname+".dts")
                    showinfo("Reverse compile DTB completion")
                if filetype == "zip" or filetype == "7z":
                    showinfo("Please do not use this tool to pack the compressed file, please use 7zip or winrar")
                if filetype == "Unknow":
                    showinfo("File is not supported")
            # os.chdir(unpackdir)
        else:
            showinfo("file does not exist")
    else:
        showinfo("Please select the working directory first")

def smartUnpack():
    T = threading.Thread(target=__smartUnpack, daemon=True)
    T.start()

def repackboot():
    dirChooseWindow("Choose the directory you want to pack Based on Android Image Kitchen")
    if os.path.isdir(directoryname.get()):
        os.chdir(directoryname.get())
        runcmd("repackimg.bat --local")
        os.chdir(LOCALDIR)
    else:
        showinfo("The folder does not exist")

def __repackextimage():
    if (WorkDir):
        dirChooseWindow("Choose the directory you want to pack, for example : .\\NH4_test\\vendor\\vendor")
        # Audo choose fs_config
        showinfo("Automatically search fs_config")
        isFsConfig = findFsConfig(directoryname.get())
        isFileContexts = findFileContexts(directoryname.get())
        if isFsConfig != "0":
            showinfo("Automatically search fs_config to complete:" + isFsConfig)
            fsconfig_path = isFsConfig
        if isFileContexts != "0":
            showinfo("Automatically search File_Contexts to complete" + isFileContexts)
            filecontexts_path = isFileContexts
        else:
            showinfo("Automatically search fs_config failed, please choose manually")
            fileChooseWindow("Select the fs_config file you want to pack the directory")
            fsconfig_path = filename.get()
        if (os.path.isdir(directoryname.get())):
            showinfo("Fix FS_CONFIG files")
            fspatch.main(directoryname.get(), fsconfig_path)
            # Thanks DXY provid info
            cmd = "busybox ash -c \""
            if os.path.basename(directoryname.get()).find("odm")!=-1:
                MUTIIMGSIZE = 1.2
            else:
                MUTIIMGSIZE = 1.07
            if (UICONFIG['AUTOMUTIIMGSIZE']):
                EXTIMGSIZE = int(utils.getdirsize(directoryname.get())*MUTIIMGSIZE)
            else:
                EXTIMGSIZE = UICONFIG['MODIFIEDIMGSIZE']
            cmd += "MKE2FS_CONFIG=bin/mke2fs.conf E2FSPROGS_FAKE_TIME=1230768000 mke2fs.exe "
            cmd += "-O %s " %(UICONFIG['EXTFUEATURE'])
            cmd += "-L %s " %(os.path.basename(directoryname.get()))
            cmd += "-I 256 "
            cmd += "-M /%s -m 0 " %(os.path.basename(directoryname.get()))  # mount point
            cmd += "-t %s " %(UICONFIG['EXTREPACKTYPE'])
            cmd += "-b %s " %(UICONFIG['EXTBLOCKSIZE'])
            cmd += "%s/output/%s.img " %(WorkDir, os.path.basename(directoryname.get()))
            cmd += "%s\"" %(int(EXTIMGSIZE/4096))
            showinfo("Try to create a directory output")
            utils.mkdir(WorkDir + os.sep +"output")
            showinfo("Start packing EXT mirror image")
            statusstart()
            showinfo(cmd)
            runcmd(cmd)
            cmd = "e2fsdroid.exe -e -T 1230768000 -C %s -S %s -f %s -a /%s %s/output/%s.img" %(fsconfig_path, filecontexts_path, directoryname.get(), os.path.basename(directoryname.get()), WorkDir, os.path.basename(directoryname.get()))
            runcmd(cmd)
            statusend()
            showinfo("End")
    else:
        showinfo("Please select the working directory first ")

def findFsConfig(Path):
    parentPath = os.path.dirname(Path)
    currentPath = os.path.basename(parentPath)
    if os.path.exists(parentPath + '\config\\' + currentPath + "_fs_config"):
        return parentPath + '\config\\' + currentPath + "_fs_config"
    else:
        return "0"

def findFileContexts(Path):
    parentPath = os.path.dirname(Path)
    currentPath = os.path.basename(parentPath)
    if os.path.exists(parentPath + '\config\\' + currentPath + "_file_contexts"):
        return parentPath + '\config\\' + currentPath + "_file_contexts"
    else:
        return "0"

def __repackerofsimage():
    if WorkDir:
        dirChooseWindow("Choose the directory you want to pack, for example: .\\NH4_test\\vendor\\vendor")
        # Audo choose fs_config
        showinfo("Automatic search fs_config")
        isFsConfig = findFsConfig(directoryname.get())
        isFileContexts = findFileContexts(directoryname.get())
        if isFsConfig != "0":
            showinfo("Automatically search fs_config to complete: " + isFsConfig)
            fsconfig_path = isFsConfig
        else:
            showinfo("Automatically search fs_config failed, please choose manually")
            fileChooseWindow("Select the fs_config file you want to pack the directory")
            fsconfig_path = filename.get()
        if isFileContexts != "0":
            showinfo("Automatically search File_Contexts to complete" + isFileContexts)
            filecontexts_path = isFileContexts
        statusstart()
        fspatch.main(directoryname.get(), fsconfig_path)
        cmd = "mkfs.erofs.exe %s/output/%s.img %s -z\"%s\" -T\"1230768000\" --mount-point=/%s --fs-config-file=%s --file-contexts=%s" %(WorkDir, os.path.basename(directoryname.get()), directoryname.get().replace("\\","/"), UICONFIG['EROFSCOMPRESSOR'], os.path.basename(directoryname.get()), fsconfig_path, filecontexts_path)
        print(cmd)
        runcmd(cmd)
        statusend()
    else:
        showinfo("Please select the working directory first")

def repackerofsimage():
    th = threading.Thread(target=__repackerofsimage)
    th.start()

def repackextimage():
    th = threading.Thread(target=__repackextimage)
    th.start()

def __repackDTBO():
    if WorkDir:
        dirChooseWindow("Select the DTBO folder")
        if not os.path.isdir(WorkDir+os.sep+"output"):
            utils.mkdir(WorkDir+os.sep+"output")
        cmd = "mkdtboimg.exe create %s\\output\\dtbo.img " %(WorkDir)
        for i in range(len(glob.glob(directoryname.get()+os.sep+"*"))):
            cmd += "%s\\dtb.%s " %(directoryname.get(), i)
        runcmd(cmd)
        showinfo("Package end ")
    else:
        showinfo("Please select the working directory first")

def repackDTBO():
    th = threading.Thread(target=__repackDTBO)
    th.start()

def __repackSparseImage():
    if (WorkDir):
            # 只将 EXT 转为 SIMG 而不是重新打包一次
            fileChooseWindow("Choose IMG files to be converted to SIMG")
            imgFilePath = filename.get()
            if(os.path.exists(imgFilePath) == False):
                showinfo("file does not exist: " + imgFilePath)
            elif returnoutput("gettype -i " + imgFilePath).replace('\r\n', '') != "ext":
                showinfo("The selected file is not an EXT image, please switch first")
                return
            else:
                showinfo("Start conversion")
                statusstart()
                cmd = "%s %s %s/output/%s_sparse.img" %(UICONFIG['SPARSETOOL'], imgFilePath, WorkDir, os.path.basename(directoryname.get()))
                runcmd(cmd)
                statusend()
                showinfo("Convert")
    else:
        showinfo("Please select the working directory first")

def repackSparseImage():
    th = threading.Thread(target=__repackSparseImage)
    th.start()

def compressToBr():
    th = threading.Thread(target=__compressToBr)
    th.start()

def __compressToBr():
    if WorkDir:
        fileChooseWindow("Choose a DAT file to be converted to br")
        imgFilePath = filename.get()
        if(os.path.exists(imgFilePath) == False):
            showinfo("file does not exist: " + imgFilePath)
        elif returnoutput("gettype -i " + imgFilePath).replace('\r\n', '') != "dat":
            showinfo("The selected file is not dat, please switch first")
            return
        else:
            showinfo("Start conversion")
            statusstart()
            th = threading.Thread(target=runcmd("brotli.exe -q 6 " + imgFilePath))
            th.start()
            statusend()
            showinfo("After the conversion is complete, take off to the same folder")
    else:
        showinfo("Please select the working directory first")

def repackDat():
    th = threading.Thread(target=__repackDat)
    th.start()

def __repackDat():
    if WorkDir:
        # TO-DO: 打包后自动定位转换好的 simg   20220331
        # TO-DO: 自动识别Android版本   20220331
        fileChooseWindow("Choose an IMG file to be converted to DAT")
        imgFilePath = filename.get()
        if(os.path.exists(imgFilePath) == False):
            showinfo("file does not exist: " + imgFilePath)
        elif returnoutput("gettype -i " + imgFilePath).replace('\r\n', '') != "sparse":
            showinfo("The selected file is not Sparse, please switch first")
            return
        else:
            showinfo("Warning: Only accept the large version input. For example, 7.1.2 Please enter 7.1 directly!")
            userInputWindow("输入Android版本")
            inputVersion = float(inputvar.get())
            if inputVersion == 5.0: # Android 5
                showinfo("chosen: Android 5.0")
                currentVersion = 1
            elif inputVersion == 5.1: # Android 5.1
                showinfo("chosen: Android 5.1")
                currentVersion = 2
            elif inputVersion >= 6.0 and inputVersion < 7.0: # Android 6.X
                showinfo("chosen: Android 6.X")
                currentVersion = 3
            elif inputVersion >= 7.0: # Android 7.0+
                showinfo("chosen: Android 7.X+")
                currentVersion = 4
            else:
                currentVersion = 0
            # PREFIX
            inputvar.set("")
            showinfo("Tip: Enter the partition name (such as System, Vendor, ODM)")
            userInputWindow("Enter partition name")
            partitionName = inputvar.get()
            if currentVersion == 0:
                showinfo("The Android version input is error, please check the prompt to re -enter!")
                return
            elif partitionName == NULL or partitionName == "":
                showinfo("Input errors in the partition name, please see the prompt to re -enter!")
                return
            # img2sdat <image file> <output dir> <version|1=5.0|2=5.1|3=6.0|4=7.0+> <prefix>
            showinfo("Start conversion")
            statusstart()
            th = threading.Thread(target=img2sdat.main(imgFilePath, WorkDir + "/output/", currentVersion, partitionName))
            th.start()
            statusend()
            showinfo("After the conversion, get rid of the OUTPUT folder in the work directory")
    else:
        showinfo("Please select the working directory first")

def __repackdtb():
    if WorkDir:
        fileChooseWindow("Select DTS file and output to DTB folder")
        if os.access(filename.get(), os.F_OK):
            if not os.path.isdir(WorkDir+os.sep+"dtb"):
                utils.mkdir(WorkDir+os.sep+"dtb")
            statusstart()
            runcmd("dtc -I dts -O dtb %s -o %s\\dtb\\%s.dtb" %(filename.get(), WorkDir, os.path.basename(filename.get()).replace(".dts",".dtb")))
            statusend()
            showinfo("Compiled to DTB to complete")
        else:
            showinfo("file does not exist")
    else:
        showinfo("Please select the working directory first")

def repackdtb():
    th = threading.Thread(target=__repackdtb)
    th.start()

def __repackSuper():
    if WorkDir:
        packtype = tk.StringVar()
        packsize = tk.StringVar()
        packsize.set("9126805504")
        sparse = tk.IntVar()

        def selecttype(type):
            packtype.set(type)
            w.destroy()

        showinfo("Packing Super Mirror")
        w = tk.Toplevel()
        curWidth = 400
        curHight = 180
        # 获取屏幕宽度和高度
        scn_w, scn_h = root.maxsize()
        # 计算中心坐标
        cen_x = (scn_w - curWidth) / 2
        cen_y = (scn_h - curHight) / 2
        # 设置窗口初始大小和位置
        size_xy = '%dx%d+%d+%d' % (curWidth, curHight, cen_x, cen_y)
        w.geometry(size_xy)
        w.resizable(0,0) # 设置最大化窗口不可用
        w.title("Choose the type of your package:")
        l1 = ttk.LabelFrame(w, text="Choose a packing type", labelanchor="nw", relief=GROOVE, borderwidth=1)
        ttk.Button(l1, text='VAB', width=15, command=lambda:selecttype("VAB")).pack(side=LEFT, expand=YES, padx=5)
        ttk.Button(l1, text='AB', width=15, command=lambda:selecttype("AB")).pack(side=LEFT, expand=YES, padx=5)
        ttk.Button(l1, text='A-only', width=15, command=lambda:selecttype("A-only")).pack(side=LEFT, expand=YES, padx=5)
        l1.pack(side=TOP,ipadx=10, ipady=10)
        ttk.Label(w, text="Please enter the SUPER partition size (number of bytes, common 9126805504)").pack(side=TOP)
        ttk.Entry(w, textvariable=packsize,width=50).pack(side=TOP, padx=10, pady=10, expand=YES, fill=BOTH)
        ttk.Checkbutton(w, text = "Sparse", variable = sparse).pack(side=TOP, padx=10, pady=10)
        w.wait_window()
        if packtype.get() == "":
            showinfo("No options")
        else:
            dirChooseWindow("Select the directory of the super partition mirror file")
            superdir = directoryname.get()
            showinfo("SUPER partition mirroring where the directory is located:" + superdir)
            if sparse.get() == True:
                showinfo("Enable sparse parameters")
            cmd = "lpmake "
            showinfo("Pack ： " + packtype.get())
            cmd += "--metadata-size 65536 --super-name super "
            if packtype.get() == 'VAB':
                cmd += "--virtual-ab "
            if sparse.get() == True:
                cmd += "--sparse "
            cmd += "--metadata-slots 2 "
            cmd += "--device super:%s " %(packsize.get())
            showinfo(cmd)

    else:
        showinfo("Please select the working directory first")

def repackSuper():
    th = threading.Thread(target=__repackSuper)
    th.start()

def Test():
    showinfo("Test function")

if __name__ == '__main__':

    if(USEMYSTD):
        mystd = myStdout()
    else:
        # mystd.restoreStd()
        print("Use standard stdout and stderr...")
    #在中心打开主窗口
    screenwidth = root.winfo_screenwidth()  # 屏幕宽度
    screenheight = root.winfo_screenheight()  # 屏幕高度
    x = int((screenwidth - width) / 2)
    y = int((screenheight - height) / 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))  # 大小以及位置

    if(MENUBAR):   # 菜单栏
        menuBar = tk.Menu(root)
        root.config(menu=menuBar)
        menu1 = tk.Menu(menuBar, tearoff=False)
        menuItem = ["About "," Exit"]
        for item in menuItem:
            if(item=="about"):
                menu1.add_command(label=item, command=about)
            if(item=="quit"):
                menu1.add_command(label=item, command=sys.exit)
        menuBar.add_cascade(label="menu", menu=menu1)
        menu2 = tk.Menu(menuBar, tearoff=False)
        menuItem = ["cosmo","flatly","journal","literal","lumen","minty","pulse","sandstone","united","yeti","cyborg","darkly","solar","vapor","superhero"]
        for item in menuItem:
            menu2.add_command(label=item, command=lambda n=item:change_theme(n))
        menuBar.add_cascade(label="theme", menu=menu2)

    # define labels
    frame = ttk.LabelFrame(root, text="NH4 Rom Tool", labelanchor="nw", relief=GROOVE, borderwidth=1)
    frame1 = ttk.LabelFrame(frame, text="Functional area", labelanchor="nw", relief=SUNKEN, borderwidth=1)
    frame2 = ttk.LabelFrame(frame, text="information feedback", labelanchor="nw", relief=SUNKEN, borderwidth=1)

    # Notebook
    tabControl = ttk.Notebook(frame1)
    # tab
    tab1 = ttk.Frame(tabControl)
    tab2 = ttk.Frame(tabControl)
    tab3 = ttk.Frame(tabControl)
    tab33 = ScrolledFrame(tab3, autohide=True, width=220)
    tab4 = ttk.Frame(tabControl)
    # tab44 = ScrolledFrame(tab4, autohide=True, width=220)

    tabControl.add(tab1, text="Work list")
    tabControl.add(tab2, text="Pack")
    tabControl.add(tab3, text="Other tools")
    # tabControl.add(tab4, text="设置")

    tab33.pack(side=LEFT, expand=YES, fill=BOTH)

    # Treeview  use to list work dir
    tab11 = ttk.Frame(tab1)

    columns = ["Workdir"]
    table = ttk.Treeview(
            tab11,  # 父容器
            height=10,  # 表格显示的行数,height行
            columns=columns,  # 显示的列
            show='headings',  # 隐藏首列
            )
    table.column('Workdir', width=100, anchor='center')
    table.heading('Workdir', text='Work list')
    table.pack(side=TOP, fill=BOTH, expand=YES)
    table.bind('<ButtonRelease-1>',tableClicked)
    getWorkDir()

    # 咕咕咕
    def functionNotAvailable() :
        showinfo("When you see this prompt, it means that this function is still not installed, and it may take up to 2147483647 hours to complete it")
    
    # Buttons under Treeview
    tab12 = ttk.Frame(tab1)
    ttk.Button(tab12, text='Confirmation directory', width=10, command=ConfirmWorkDir,style='primiary.Outline.TButton').grid(row=0, column=0, padx='10', pady='8')
    ttk.Button(tab12, text='Delete directory', width=10, command=rmWorkDir,style='primiary.Outline.TButton').grid(row=0, column=1, padx='10', pady='8')
    ttk.Button(tab12, text='New directory', width=10, command=mkWorkdir,style='primiary.Outline.TButton').grid(row=1, column=0, padx='10', pady='8')
    ttk.Button(tab12, text='Refresh directory', width=10, command=getWorkDir,style='primiary.Outline.TButton').grid(row=1, column=1, padx='10', pady='8')
    ttk.Button(tab12, text='Cleaning directory', width=10, command=clearWorkDir,style='primiary.Outline.TButton').grid(row=2, column=0, padx='10', pady='8')


    # Pack Buttons
    tab12.pack(side=BOTTOM, fill=BOTH, expand=YES, anchor=CENTER)
    
    # pack Notebook
    tabControl.pack(fill=BOTH, expand=YES)
    tab11.pack(side=TOP, fill=BOTH, expand=YES)
    
    # tab21 // Unpack
    tab21 = ttk.LabelFrame(tab2, text="Unpack", labelanchor="nw", relief=SUNKEN, borderwidth=1)
    ttk.Button(tab21, text='Decompress', width=10, command=unzipfile,style='primiary.Outline.TButton').grid(row=0, column=0, padx='10', pady='8')
    ttk.Button(tab21, text='Universal dissection', width=10, command=smartUnpack,style='primiary.Outline.TButton').grid(row=0, column=1, padx='10', pady='8')
    
    # tab22 // Repack
    tab22 = ttk.LabelFrame(tab2, text="Pack", labelanchor="nw", relief=SUNKEN, borderwidth=1)
    ttk.Button(tab22, text='compression', width=10, command=zipcompressfile,style='primiary.Outline.TButton').grid(row=0, column=0, padx='10', pady='8')
    ttk.Button(tab22, text='BOOT', width=10, command=repackboot,style='primiary.Outline.TButton').grid(row=0, column=1, padx='10', pady='8')
    ttk.Button(tab22, text='EXT', width=10, command=repackextimage,style='primiary.Outline.TButton').grid(row=1, column=0, padx='10', pady='8')
    ttk.Button(tab22, text='EROFS', width=10, command=repackerofsimage,style='primiary.Outline.TButton').grid(row=1, column=1, padx='10', pady='8')
    ttk.Button(tab22, text='DTS2DTB', width=10, command=repackdtb,style='primiary.Outline.TButton').grid(row=2, column=0, padx='10', pady='8')
    ttk.Button(tab22, text='DTBO', width=10, command=repackDTBO,style='primiary.Outline.TButton').grid(row=2, column=1, padx='10', pady='8')
    ttk.Button(tab22, text='SUPER', width=10, command=repackSuper,style='primiary.Outline.TButton').grid(row=3, column=0, padx='10', pady='8')
    ttk.Button(tab22, text='EXT->SIMG', width=10, command=repackSparseImage,style='primiary.Outline.TButton').grid(row=3, column=1, padx='10', pady='8')
    ttk.Button(tab22, text='IMG->DAT', width=10, command=repackDat,style='primiary.Outline.TButton').grid(row=4, column=0, padx='10', pady='8')
    ttk.Button(tab22, text='DAT->BR', width=10, command=compressToBr,style='primiary.Outline.TButton').grid(row=4, column=1, padx='10', pady='8')
    
    # pack tab2
    tab21.pack(side=TOP, fill=BOTH, expand=NO)
    tab22.pack(side=TOP, fill=BOTH, expand=YES)

    # tab3
    ttk.Button(tab33, text='Detect file format', width=10, command=detectFileType, bootstyle="link").pack(side=TOP, expand=NO, fill=X, padx=8)
    ttk.Separator(tab33).pack(side=TOP, expand=NO, fill=X, padx=8)
    ttk.Button(tab33, text='OZIP Decrypt', width=10, command=ozipDecrypt, bootstyle="link").pack(side=TOP, expand=NO, fill=X, padx=8)
    ttk.Separator(tab33).pack(side=TOP, expand=NO, fill=X, padx=8)
    ttk.Button(tab33, text='OZIP encryption', width=10, command=ozipEncrypt, bootstyle="link").pack(side=TOP, expand=NO, fill=X, padx=8)
    ttk.Separator(tab33).pack(side=TOP, expand=NO, fill=X, padx=8)
    ttk.Button(tab33, text='MIUI Update package acquisition', width=10, command=getMiuiWindow, bootstyle="link").pack(side=TOP, expand=NO, fill=X, padx=8)
    ttk.Separator(tab33).pack(side=TOP, expand=NO, fill=X, padx=8)
    
    s = ttk.Style()
    s.configure('Button.parsePayload', font=('Helvetica', '5'))
    ttk.Button(tab33, text='PAYLOAD.bin Analyze', width=10, command=parsePayload, bootstyle="link").pack(side=TOP, expand=NO, fill=X, padx=8)
    ttk.Separator(tab33).pack(side=TOP, expand=NO, fill=X, padx=8)
    ttk.Button(tab33, text='Close VBMETA verification', width=10, command=patchvbmeta, bootstyle="link").pack(side=TOP, expand=NO, fill=X, padx=8)
    ttk.Separator(tab33).pack(side=TOP, expand=NO, fill=X, padx=8)
    ttk.Button(tab33, text='Fix FS_CONFIG files', width=10, command=patchfsconfig, bootstyle="link").pack(side=TOP, expand=NO, fill=X, padx=8)
    ttk.Separator(tab33).pack(side=TOP, expand=NO, fill=X, padx=8)

    # ScrolledText
    text = scrolledtext.ScrolledText(frame2, width=180, height=18, font=TEXTFONT, relief=SOLID) # 信息展示 文本框
    text.pack(side=TOP, expand=YES, fill=BOTH , padx=4, pady=2)
    # table.bind('<ButtonPress-1>', showinfo("请点击确认目录"))
    if(ALLOWMODIFYCMD):
        frame22 = ttk.LabelFrame(frame2, text="Enter the custom command", labelanchor="nw", relief=SUNKEN, borderwidth=1)
        usercmd = ttk.Entry(frame22,textvariable=USERCMD,width=25)
        usercmd.pack(side=LEFT, expand=YES, fill=X, padx=2, pady=2)
        usercmd.bind('<Return>', __xruncmd)
        ttk.Button(frame22, text='run', command=xruncmd, style='primary.Outline.TButton').pack(side=LEFT, expand=NO, fill=X, padx=2, pady=2)
    # pack frames
    frame.pack(side=TOP, expand=YES, fill=BOTH, padx=2, pady=2)
    frame1.pack(side=LEFT, expand=YES, fill=BOTH, padx=5, pady=2)
    frame2.pack(side=LEFT, expand=YES, fill=BOTH, padx=5, pady=2)
    if(ALLOWMODIFYCMD):
        frame22.pack(side=TOP, expand=NO, fill=BOTH, padx=5, pady=2)

    # bottom labels
    framebotm = ttk.Frame(root, relief=FLAT, borderwidth=0)
    ttk.Button(framebotm, text='Clear information', command=cleaninfo,style='secondary.TButton').pack(side=RIGHT, expand=NO, padx=5,pady=0)
    # Status bar
    if(USESTATUSBAR):
        statusbar = ttk.Label(framebotm, relief='flat', anchor=tk.E, bootstyle="info")
        statusbar.pack(side=RIGHT, fill=tk.X, ipadx=12)
        statusbar['image'] = DEFAULTSTATUS
    # shiju
    if(SHOWSHIJU):
        shiju = utils.getShiju()
        shiju_font = ('Microsoft Yahei',12)
        shijuLable = ttk.Label(framebotm, text="%s —— %s  《%s》" %(shiju['content'],shiju['author'],shiju['origin']), font=shiju_font)
        shijuLable.pack(side=LEFT,padx=8)
    framebotm.pack(side=BOTTOM,expand=NO, fill=X, padx=8, pady=12)

    if(TEXTSHOWBANNER):
        showbanner()

    if(DEBUG):
        showinfo("Debug mode has been opened")
        # showinfo("Board id : " + sn.get_board_id())
        # showinfo(UICONFIG)
    else:
        '''
        showinfo("  Version : %s" %(VERSION))
        showinfo("  Author  : %s" %(AUTHOR))
        showinfo("  LICENSE : %s" %(LICENSE))
        '''

    root.update()
    root.mainloop()
    
    if(USEMYSTD):
        mystd.restoreStd() # 还原标准输出