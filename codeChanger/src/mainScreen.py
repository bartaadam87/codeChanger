'''
Created on 20 Feb 2014

@author: rr162938
'''

import sys
from threading import Timer
import time

from PyQt4 import QtGui, QtCore
import pyodbc
import serial

import codeChanger


def timeR(time):
    timerR = Timer(time, delText)
    timerR.start()

def timeC(time):
    openPort()
    timerR = Timer(time, cyc)
    timerR.start()

def delText():
    codeChangerGui.lineEdit.clear()

def setText(text):
    codeChangerGui.lineEdit.setText(text)

def change():
    codeChangerGui.lineEdit.setText("Zadejte PN")
    timeR(3)
    QtCore.QObject.connect(codeChangerGui.pushButton, QtCore.SIGNAL('clicked()'), changeCode)  

    QtCore.QObject.connect(codeChangerGui.lineEdit, QtCore.SIGNAL('returnPressed()'), changeCode)  
    return  

def openPort():
    serScanner.open()

serScanner = serial.Serial()
serScanner.port = str("COM8")  
serScanner.baudrate = int(115200)
serScanner.bytesize = serial.EIGHTBITS #number of bits per bytes
serScanner.parity = serial.PARITY_NONE #set parity check: no parity
serScanner.stopbits = serial.STOPBITS_ONE #number of stop bits          #non-block read
serScanner.xonxoff = False     #disable software flow control
serScanner.rtscts = False     #disable hardware (RTS/CTS) flow control
serScanner.dsrdtr = False       #disable hardware (DSR/DTR) flow control

#     sys.exit(app.exec_())             
##    AboutForm.show()

class RowItem(object): ##
    _slots_= "OEM", "Option_Kit", "fg_part_no", "no_barcodes","Description","Capacity_text","Speed_text","Spares_text","no_ct_digits","no_firmware_digits","ct_symbology","no_serial_digits","exp_GPN","firmware_symbology","serial_symbology","security_symbology","gpn_symbology","rd_hp_pn_label","no_box_serial_digits","box_serial_symbology","s_ColLineage","s_Generation","s_GUID","s_Lineage","no_GPN_digits"

rowItem = RowItem()
   
pathToDatabase = "U:\Python projects\\banta_drivescan.mdb"

def connectDatabase(pathToDatabase):
    try:
        global conn
        conn = pyodbc.connect("DRIVER={Microsoft Access Driver (*.mdb)};DBQ="+pathToDatabase)
        ##conn = pyodbc.connect("DRIVER={Microsoft Access Driver (*.mdb)})
    except ValueError:
        print("Unable to open database "+pathToDatabase)
        
def readingFromDatabase():
    try:
        ##Pridat kontrolu zda se nachazi v databai vice zaznamu
##        cursor = conn.cursor()
        cursor = conn.cursor()
        SQL = "SELECT * FROM tbl_drives WHERE fg_part_no='"+str(codeChangerGui.lineEdit.text())+"';" ##'661144-001'        
        cursor.execute(SQL)
        row = cursor.fetchone()
        global rowItem
##        rowItem = RowItem()
         
        ##Pridat ignorovani mezer
        rowItem.OEM = str(row.OEM)
        rowItem.no_box_serial_digits = str(row.no_box_serial_digits).replace(" ", "")
        rowItem.box_serial_symbology = str(row.box_serial_symbology).replace(" ", "")
    except ValueError:
        print("Unable to open database "+pathToDatabase)

def changeCode():
    connectDatabase(pathToDatabase)
    try:
        readingFromDatabase()
    except:
        codeChangerGui.lineEdit.setText("Error")
        timeR(3)
    
    global rowItem
    i = int(rowItem.no_box_serial_digits)
    j = str(hex(i).lstrip("0x"))
    print(j)
    
    try:
        if rowItem.box_serial_symbology == "C39":
            serScanner.write(str("$S"+'\r').encode())
            time.sleep(0.2)
            serScanner.write(str("$CC3EN01"+'\r').encode())
            time.sleep(0.2)
            serScanner.write(str("$CC3L10"+j+'\r').encode())
            time.sleep(0.2)
            serScanner.write(str("$CC8EN00"+'\r').encode())
            time.sleep(0.2)
            serScanner.write(str("$CC9EN00"+'\r').encode())
            time.sleep(0.2)
            serScanner.write(str("$Ar"+'\r').encode())
            time.sleep(0.2)
            serScanner.close()
            
            delText()
            setText("OK")
            timeR(3)
            timeC(10)
            
        if rowItem.box_serial_symbology == 'C128':
            serScanner.write(str("$S"+'\r').encode())
            time.sleep(0.2)
            serScanner.write(str("$CC3EN00"+'\r').encode())
            time.sleep(0.2)
            serScanner.write(str("$CC8EN01"+'\r').encode())
            time.sleep(0.2)
            serScanner.write(str("$CC8L10"+j+'\r').encode())
            time.sleep(0.2)
            serScanner.write(str("$CC9EN00"+'\r').encode())
            time.sleep(0.2)
            serScanner.write(str("$Ar"+'\r').encode())
            time.sleep(0.2)
            serScanner.close()
            
            delText()
            setText("OK")
            timeR(3)
            timeC(10)
                        
        if rowItem.box_serial_symbology == 'C93':
            serScanner.write(str("$S"+'\r').encode())
            time.sleep(0.2)
            serScanner.write(str("$CC3EN00"+'\r').encode())
            time.sleep(0.2)
            serScanner.write(str("$CC8EN00"+'\r').encode())
            time.sleep(0.2)
            serScanner.write(str("$CC9EN01"+'\r').encode())
            time.sleep(0.2)
            serScanner.write(str("$CC9L10"+j+'\r').encode())
            time.sleep(0.2)
            serScanner.write(str("$Ar"+'\r').encode())
            time.sleep(0.2)
            
            delText()
            setText("OK")
            timeR(3)
            timeC(10)
                        
    except:
        print("error - no code given")

def cyc():
    print(str(serScanner.read(8)).lstrip("b'").rstrip("'\r"))
    timerRte = Timer(0.5, cyc)
    timerRte.start()
    
#     while timeLeft < 5:
#         print(a)
#         a += 1
#         changeCode()
#         time.sleep(60)
#         serScanner.open()
#         print(str(serScanner.read(8)).lstrip("b'").rstrip("'"))
#         serScanner.close()
#         timeLeft = timeLeft-1
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    codeChangerForm = QtGui.QMainWindow()
    codeChangerGui = codeChanger.Ui_MainWindow()
    codeChangerGui.setupUi(codeChangerForm)
    codeChangerForm.show()
    openPort()
    change()
    sys.exit(app.exec_())
    