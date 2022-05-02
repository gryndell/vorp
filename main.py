#!/usr/bin/env python3

import collections
import tkinter as tk
from tkinter.constants import HORIZONTAL
import tkinter.font as tkFont
from tkinter import StringVar, Toplevel, messagebox, ttk
import vorpdb

root = tk.Tk()
# root.geometry("1366x768")
root.resizable(False, False)
root.title('VORP')
# root.attributes("-fullscreen", 1)

# Global variables
msgStatus = StringVar()
orderId = StringVar()
orderNr = StringVar()
compCode = StringVar()
langCode = StringVar()
langCode.set(vorpdb.run_query("SELECT Language FROM Control", ())[0][0])
workstation = StringVar()
myId = StringVar()
myOp = 0

# Get configuration data from Control record
langCode.set(vorpdb.run_query("SELECT Language FROM Control",
                              ())[0][0])
workstation.set(vorpdb.run_query("SELECT Workstation FROM Control",
                                 ())[0][0])
urlInput = StringVar()
urlInput.set(vorpdb.run_query("SELECT url_input FROM Control",
                              ())[0][0])
urlOutput = StringVar()
urlOutput.set(vorpdb.run_query("SELECT url_output FROM Control",
                               ())[0][0])

# Establish ttk.Style
fontTrv = tkFont.Font(root, font="LiberationMono", size=12)
fontFrm = tkFont.Font(root, font="Cantarell", size=18)
fontEnt = tkFont.Font(root, font="LiberationMono", size=18)
myStyle = ttk.Style()
myStyle.theme_use('default')   # One of clam, alt, default or classic
myStyle.configure("TFrame", font="Cantarell 18")
myStyle.configure("TLabel", font="Cantarell 18")
myStyle.configure("TEntry", font="LiberationMono 18")
myStyle.configure("TButton", font="Cantarell 18")
myStyle.configure(
    "Treeview",
    font=fontTrv,
    rowheight=30, sticky='nsew'
)
myStyle.configure("Treeview.Heading",
                  font=fontTrv, padding=5, sticky='nsew')
myStyle.configure(
    "Treeview.Row",
    padding=1,
    font=fontTrv,
    sticky='ew'
)
myStyle.configure(
    "Treeview.Cell",
    padding=1,
    font=fontTrv,
    sticky='ew'
)
myStyle.configure("TLabelframe.Label", padding=5, font="Cantarell 18")

# Get width of characters
charWidthTrv = fontTrv.measure("W")
charWidthFrm = fontFrm.measure("W")
charWidthEnt = fontEnt.measure("W")


# Get a Label, given language and Term
def getLabel(iLang, iTerm):
    myResult = vorpdb.run_query(
        "SELECT Label FROM Labels WHERE Language = ? AND Term = ?",
        (iLang, iTerm)
    )
    if len(myResult) == 0:
        return iTerm
    else:
        return myResult[0][0]


# Create and grid the frames
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
frmMain = ttk.Frame(root, padding=(5, 5, 5, 5))
frmMain.grid(column=0, row=0, sticky='nsew')
frmOrders = ttk.Labelframe(
    frmMain,
    text=(' ' + getLabel(langCode.get(), 'Orders') + ' '),
    labelanchor='nw',
    padding=10
)
frmCompList = ttk.Labelframe(
    frmMain,
    text=(' ' + getLabel(langCode.get(), 'Components') + ' '),
    labelanchor='nw',
    padding=10
)
frmOrders.focus_set()


# Close the app
def closeApp():
    vorpdb.logEvent("Session End")
    root.destroy()


# configure the work station
def wkstnConfigure():
    # Verify password
    def verifyPw(iPass):
        # If password is verified, open up the configuration frame
        if vorpdb.pw_verify(iPass):
            entLanguage.state(['!disabled'])
            entWorkstation.state(['!disabled'])
            entInput.state(['!disabled'])
            entOutput.state(['!disabled'])
            entLanguage.icursor(tk.END)
            entLanguage.focus_set()
        # Otherwise close the configuration
        else:
            frmConfig.destroy()
            frmMain.focus_set()

    def setLang(iLang):
        vorpdb.run_query("UPDATE Control SET Language = ?", (iLang,))
        entWorkstation.icursor(tk.END)
        entWorkstation.focus_set()

    def setName(iName):
        vorpdb.run_query("UPDATE Control SET Workstation = ?", (iName,))
        entInput.icursor(tk.END)
        entInput.focus_set()

    def setInput(iInput):
        vorpdb.run_query("UPDATE Control SET url_input = ?", (iInput,))
        entOutput.icursor(tk.END)
        entOutput.focus_set()

    def setOutput(iOutput):
        vorpdb.run_query("UPDATE Control SET url_output = ?", (iOutput,))
        frmConfig.destroy()
        frmMain.focus_set()

    def closeConfig():
        frmConfig.destroy()
        frmMain.focus_set()

    frmConfig = Toplevel(frmMain)
    password = StringVar()
    lblPassword = ttk.Label(
        frmConfig,
        text='Password:',
        anchor='e'
    )
    entPassword = ttk.Entry(
        frmConfig,
        textvariable=password,
        show="*",
        width=18
    )
    entPassword.configure(font="LiberationMono 18")
    lblLanguage = ttk.Label(
        frmConfig,
        text='Language:',
        anchor='e'
    )
    entLanguage = ttk.Entry(
        frmConfig,
        textvariable=langCode,
        width=2
    )
    entLanguage.state(['disabled'])
    entLanguage.configure(font="LiberationMono 18")
    lblWorkStation = ttk.Label(
        frmConfig,
        text="Workstation:"
    )
    entWorkstation = ttk.Entry(
        frmConfig,
        textvariable=workstation,
        width=8
    )
    entWorkstation.state(['disabled'])
    entWorkstation.configure(font="LiberationMono 18")
    lblInput = ttk.Label(
        frmConfig,
        text='URL Input:',
        anchor='e'
    )
    entInput = ttk.Entry(
        frmConfig,
        textvariable=urlInput,
        width=80
    )
    entInput.state(['disabled'])
    entInput.configure(font="LiberationMono 18")
    lblOutput = ttk.Label(
        frmConfig,
        text='URL Output:',
        anchor='e'
    )
    entOutput = ttk.Entry(
        frmConfig,
        textvariable=urlOutput,
        width=80
    )
    entOutput.state(['disabled'])
    entOutput.configure(font="LiberationMono 18")

    # Set up the configuration dialog
    lblPassword.grid(column=0, row=0, sticky='e')
    entPassword.grid(column=1, row=0, sticky='w')
    entPassword.bind('<Return>', lambda l: verifyPw(password.get()))
    entPassword.bind('<Tab>', lambda l: verifyPw(password.get()))
    lblLanguage.grid(column=0, row=1, sticky='e')
    entLanguage.grid(column=1, row=1, sticky='w')
    entLanguage.bind('<Return>', lambda l: setLang(langCode.get()))
    entLanguage.bind('<Tab>', lambda l: setLang(langCode.get()))
    lblWorkStation.grid(column=0, row=2, sticky='e')
    entWorkstation.grid(column=1, row=2, sticky='w')
    entWorkstation.bind('<Return>', lambda l: setName(workstation.get()))
    entWorkstation.bind('<Tab>', lambda l: setName(workstation.get()))
    lblInput.grid(column=0, row=3, sticky='e')
    entInput.grid(column=1, row=3, sticky='w')
    entInput.bind('<Return>', lambda l: setInput(urlInput.get()))
    entInput.bind('<Tab>', lambda l: setInput(urlInput.get()))
    lblOutput.grid(column=0, row=4, sticky='e')
    entOutput.grid(column=1, row=4, sticky='w')
    entOutput.bind('<Return>', lambda l: setOutput(urlOutput.get()))
    entOutput.bind('<Tab>', lambda l: verifyPw(password.get()))
    frmConfig.bind('<Escape>', lambda l: closeConfig())
    entPassword.focus_set()


# Button to Configure
btnConfigure = ttk.Button(
    frmMain,
    text="",
    command=wkstnConfigure
)

# Button to Exit
btnExit = ttk.Button(
    frmMain,
    text=getLabel(langCode.get(), 'Exit'),
    command=closeApp
)

# Treeview for the Orders
trvOrderList = ttk.Treeview(
    frmOrders,
    columns=(
        'Order Nbr',
        'ID',
        'Item Code',
        'Op',
        'Qty Open',
        'Receipt',
    ),
    height=18,
    show='headings',
    selectmode='browse',
    takefocus=1
)
trvOrderList.column('#1', anchor="sw", stretch=True, width=(charWidthTrv * 20))
trvOrderList.heading('#1', text=getLabel(langCode.get(), 'Order Nbr'))
trvOrderList.column('#2', anchor="sw", stretch=True, width=(charWidthTrv * 10))
trvOrderList.heading('#2', text=getLabel(langCode.get(), 'Order ID'))
trvOrderList.column('#3', anchor="sw", stretch=True, width=(charWidthTrv * 20))
trvOrderList.heading('#3', text=getLabel(langCode.get(), 'Item Code'))
trvOrderList.column('#4', anchor="se", stretch=True, width=(charWidthTrv * 3))
trvOrderList.heading('#4', text=getLabel(langCode.get(), 'Op'))
trvOrderList.column('#5', anchor="se", stretch=True, width=(charWidthTrv * 10))
trvOrderList.heading('#5', text=getLabel(langCode.get(), 'Qty Open'))
trvOrderList.column('#6', anchor="sw", stretch=True, width=(charWidthTrv * 10))
trvOrderList.heading('#6', text=getLabel(langCode.get(), 'Receipt'))

# Treeview for the Components
trvCompList = ttk.Treeview(
    frmCompList,
    columns=(
        'Op',
        'Component',
        'Action',
        'Qty Open'
    ),
    height=18,
    show='headings',
    selectmode='browse',
    takefocus=1
)
trvCompList.column('#1', anchor='e', stretch=True, width=(charWidthTrv * 4))
trvCompList.heading('#1', text=getLabel(langCode.get(), 'Op'))
trvCompList.column('#2', anchor='w', stretch=True, width=(charWidthTrv * 20))
trvCompList.heading('#2', text=getLabel(langCode.get(), 'Component'))
trvCompList.column('#3', anchor='w', stretch=True, width=(charWidthTrv * 10))
trvCompList.heading('#3', text=getLabel(langCode.get(), 'Action'))
trvCompList.column('#4', anchor='e', stretch=True, width=(charWidthTrv * 10))
trvCompList.heading('#4', text=getLabel(langCode.get(), 'Qty Open'))


# Get a list of components for the current order
def getComponents():
    # Clear the list
    for i in trvCompList.get_children():
        trvCompList.delete(i)

    selected = trvOrderList.focus()
    orderRow = trvOrderList.item(selected, 'values')

    if orderRow != () and orderRow != '':
        orderId = orderRow[1]
        orderOp = orderRow[3]
        try:
            queryDtl = """
                SELECT * FROM operationDtl WHERE id = ? AND op = ?
                """
            argsDtl = (orderId, orderOp)
            resultDtl = vorpdb.run_query(queryDtl, argsDtl)
            # Turn results into a list of ordered dictionaries
            listDtl = []
            if len(resultDtl) != 0:
                for row in resultDtl:
                    myDict = collections.OrderedDict()
                    myDict["id"] = row[0]
                    myDict["op"] = row[1]
                    myDict["component"] = row[2]
                    myDict["componentDesc"] = row[3]
                    myDict["qty"] = row[4]
                    myDict["task"] = row[5]
                    myDict["qty_done"] = row[6]
                    listDtl.append(myDict)
            # Put values into treeview
            for i in range(0, len(listDtl)):
                trvCompList.insert(
                    '',
                    'end',
                    text="1",
                    values=(
                        listDtl[i]["op"],
                        listDtl[i]["component"],
                        listDtl[i]["task"],
                        listDtl[i]["qty"]
                    )
                )
        except Exception as eDtl:
            vorpdb.logEvent("Error in getComponents: {}".format(str(eDtl)))
            messagebox.showerror(
                message="Error: {}".format(str(eDtl))
            )
        set_focus('entCompCode')
        return 'break'
    # end of getComponents


# Label for Component Entry Box
labelComponent = getLabel(langCode.get(), 'Component') + ':'
lblCompCode = ttk.Label(
    frmCompList,
    text=labelComponent,
    anchor="w"
)

# Component Entry Box
entCompCode = ttk.Entry(
    frmCompList,
    width=18,
    textvariable=compCode,
    takefocus=1
)
entCompCode.configure(font=fontEnt)
compCode.set('')

# Label to show status messages
lblStatus = ttk.Label(
    frmMain,
    textvariable=msgStatus,
    anchor="w"
)

# Grid the widgets
btnConfigure.grid(row=0, column=0, sticky='nsw')
btnExit.grid(row=0, column=1, sticky='nsw')
frmOrders.grid(row=1, column=0, sticky='nsew')
frmCompList.grid(row=1, column=1, sticky='nsew')
trvOrderList.grid(row=2, column=0, sticky='nsew')
trvCompList.grid(row=2, column=0, columnspan=2, sticky='nsew')
lblCompCode.grid(row=3, column=0, sticky='se')
entCompCode.grid(row=3, column=1, sticky='nsew')
sepStatus = ttk.Separator(frmMain, orient=HORIZONTAL)
sepStatus.grid(row=4, column=0, columnspan=2, sticky='ew')
lblStatus.grid(row=5, column=0, columnspan=2, sticky='nsew')

# Initialize focus at Order List
trvOrderList.focus_set()


# function to set focus when <Tab> is overridden
def set_focus(iWidget):
    if iWidget == 'entCompCode':
        entCompCode.focus_set()
    if iWidget == 'trvOrderList':
        orderListChildren = trvOrderList.get_children()
        if len(orderListChildren) > 0:
            trvOrderList.focus_set()
            trvOrderList.focus(orderListChildren[0])
            trvOrderList.selection_set(orderListChildren[0])
    if iWidget == 'trvCompList':
        compListChildren = trvCompList.get_children()
        if len(compListChildren) > 0:
            trvCompList.focus_set()
            trvCompList.focus(compListChildren[0])
            trvCompList.selection_set(compListChildren[0])


# Bind events
btnConfigure.bind('<Tab>', lambda l: set_focus('btnExit'))
btnConfigure.bind('<Return>', lambda l: wkstnConfigure())
btnExit.bind('<Tab>', lambda l: set_focus('trvOrderList'))
btnExit.bind('<Return>', lambda l: closeApp())
trvOrderList.bind('<Tab>', lambda l: getComponents())
trvOrderList.bind('<Return>', lambda l: getComponents())
trvOrderList.bind('<1>', lambda l: getComponents())
trvCompList.bind('<Tab>', lambda l: set_focus('entCompCode'))
trvCompList.bind('<Return>', lambda l: set_focus('entCompCode'))

# Fetch jobs
records = vorpdb.fetchData()
msgStatus.set("Fetched {} records".format(records))

try:
    # Load operationHdr records into trvOrderList
    for i in trvOrderList.get_children():
        trvOrderList.delete(i)
    queryHdr = """
        SELECT * FROM operationHdr WHERE toStation = ?
        """
    argsHdr = (workstation.get(),)
    resultHdr = vorpdb.run_query(queryHdr, argsHdr)
    listHdr = []
    if len(resultHdr) != 0:
        for row in resultHdr:
            myDict = collections.OrderedDict()
            myDict["toStation"] = row[0]
            myDict["id"] = row[1]
            myDict["nr"] = row[2]
            myDict["op"] = row[3]
            myDict["product"] = row[4]
            myDict["productDesc"] = row[5]
            myDict["orderType"] = row[6]
            myDict["qty"] = row[7]
            myDict["receipt"] = row[8]
            myDict["backflush"] = row[9]
            myDict["qty_comp"] = row[10]
            myDict["qty_rjct"] = row[11]
            listHdr.append(myDict)
    for i in range(0, len(listHdr)):
        myId.set(listHdr[i]["id"])
        myOp = listHdr[i]["op"]
        trvOrderList.insert(
            '',
            'end',
            text="1",
            values=(
                listHdr[i]["nr"],
                listHdr[i]["id"],
                listHdr[i]["product"],
                listHdr[i]["op"],
                listHdr[i]["qty"],
                listHdr[i]["receipt"]
            )
        )
    trvOrderList.focus()
except Exception as eHdr:
    vorpdb.logEvent("Error in getting Job List: {}".format(str(eHdr)))
    messagebox.showerror(message="Error: {}".format(str(eHdr)))
    # # Debug
    # print("Job List Error: {}".format(str(eHdr)))

# Start logging
vorpdb.logEvent("Session Begin")

root.mainloop()
