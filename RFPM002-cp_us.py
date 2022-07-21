from __future__ import division
import time
import sys
import serial
import os
import math
import datetime as dt
import threading
from threading import Timer
import numpy as np
#--------------------------- HELP MENU------------
import argparse

parser = argparse.ArgumentParser(description='Script para Adquisicion de datos del Power Meter, donde se le pasa por parametro  el tiempo en minutos o el numero de muestras que se quieren tomar.\n Example: \"RFPM002-cp_us.py s 1000 ./Mediciones_exterior Posicion1\"\n Example: \"RFPM002-cp_us.py t 10 ./Mediciones_exterior Posicion1\"', formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("[option]", help="s (samples), o \nt (time).")
parser.add_argument("Number", help="for option=s ---> numero de muestras\n"
                                     "for option=t ---> tiempo en minutos.")
parser.add_argument("Carpeta", help="Nombre o ruta de la carpeta donde se guardaran los archivos.\nEn caso de no existir la carpeta se crea automaticamente.")
parser.add_argument("Archivo", help="Nombre del archivo a guardar.")


args = parser.parse_args()
#---------------------------------------------------

class Controlador():
    def __init__(self):
        #caso linux
        puerto = [x for x in os.listdir('/dev') if x[:6]=='ttyUSB'][0]
        puerto = "/dev/"+puerto
        #caso windows
        #puerto = 'COM4'
        try:
            self.ser = serial.Serial(
            port=puerto,
            baudrate=115200,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.5
            )
            if(not self.ser.isOpen()):
                self.ser.open()

            time.sleep(3) #ESTE TIME ES LA PIEZA MAS FUNDAMENTAL DE ESTE CODIGO, SI LO QUITAN NO COMPILA
        except Exception as e:
            raise Exception("Error al incializar puerto: " + str(e))

        #self.ser.flushInput()
    
    def Escribir(self,instr):
        self.ser.write(instr.encode())
            

    def ContInput(self):
        return self.ser.inWaiting()

    def ContRead(self):
        return self.ser.readline()

    def End(self):
        self.ser.close()

class Archivo():
    def __init__(self, carpeta, narch):
        if(not os.path.exists(carpeta)):
            os.mkdir(carpeta)
        
        self.save = open(carpeta + narch, 'w')
    
    def Escribir(self,tiempo,potencia):
        self.save.write(tiempo + ',' + potencia+'\n')

    def Cerrar(self):
        self.save.close()




pw = Controlador()
pw.Escribir('c'+ '\r')
foldername = "./"+sys.argv[3]+"/"
filename=sys.argv[4]+".csv"
file = Archivo(foldername,filename)

muestras = 0

oldtiempo = "0"
VectorTimestamp=[]
meanpotencia = 0
potenciaold=-100
valid = True

EscrBuffer = 0
while(not EscrBuffer):
    EscrBuffer = pw.ContInput()
    #Este while esta puesto solo por seguridad

pw.ContRead() #Este se amplica para que no lea la instruccion.
while(EscrBuffer):
    out = str(pw.ContRead())
    data = out.split(',')
    tiempo = data[0][2:12]
    potencia = data[1][0:6]
    try:
        temptiempo = float(tiempo)
        
    except:
        valid = False
        print("muestra invalida")
    if (float(tiempo) >= float(oldtiempo)+10000) or (tiempo == '') or (float(tiempo)<float(oldtiempo)) or (not valid):
        print ("timestamp not valid")
        break

    try:
        temppotencia = float(potencia)
    except:
        valid = False
        print("potencia invalida")

    if (float(potencia)>-70) and (float(potencia)<0 ) and (len(potencia)==6) and (valid): # se descartan valores de potencia incoherentes
        muestras += 1
        file.Escribir(tiempo, potencia)
        VectorTimestamp.append(int(tiempo))
        meanpotencia = meanpotencia+pow(10,float(potencia)/10.0) #Transformacion de dbm a mWatts
        oldtiempo = tiempo
        if(muestras<=1):
            maxPeak = potencia
        elif(float(maxPeak)<float(potencia)):
            maxPeak=float(potencia)
        potenciaold=float(potencia)    
    else:
        print ("potencia is not valid: " + potencia)


    if (sys.argv[1] == "s" and muestras == int(sys.argv[2])):
        EscrBuffer = 0
        pw.End()
        VectorTimestamp_asarray=np.asarray(VectorTimestamp)
        SamplingTime=np.mean(np.diff(VectorTimestamp_asarray))*math.pow(10,-3)
        print("meanRSS is: " + str(10*math.log10(meanpotencia/muestras)))
        print("MaxPeak is: " + str(maxPeak)) 
        print("Sampling time (ms):"+str(SamplingTime))
    elif (sys.argv[1] == 't' and float(tiempo) >= float(sys.argv[2])*60*1000000):
        EscrBuffer = 0
        pw.End()
        VectorTimestamp_asarray=np.asarray(VectorTimestamp)
        SamplingTime=np.mean(np.diff(VectorTimestamp_asarray))*math.pow(10,-3)
        print("meanRSS is: " + str(10*math.log10(meanpotencia/muestras)))
        print("MaxPeak is: " + str(maxPeak)) 
        print("Sampling time (ms):"+str(SamplingTime))
    

