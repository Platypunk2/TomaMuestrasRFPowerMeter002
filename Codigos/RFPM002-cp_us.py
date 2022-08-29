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
            #En esta primera parte se dictan los parametros necesarios para abrir el puerto y se pueda leer y escribir en el Power Meter
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

    
    #Estos 4 metodos son comandos basicos para pyserial que permiten la escritura, lectura, contar elementos del buffer y cerrar el puerto.
    def Escribir(self,instr):
        self.ser.write(instr.encode())
        
    def ContInput(self):
        return self.ser.inWaiting()

    def ContRead(self):
        return self.ser.readline()

    def End(self):
        self.ser.close()

#Esta clase fue creada con el proposito de crear el archivo .csv lo mas simple y ordenadamente como se era posible
class Archivo():
    def __init__(self, carpeta, narch):
        if(not os.path.exists(carpeta)):
            os.mkdir(carpeta)
        
        self.save = open(carpeta + narch, 'w')
    
    #Consta de dos clases que son solo para escribir y cerrar el archivo.
    def Escribir(self,tiempo,potencia):
        self.save.write(tiempo + ',' + potencia+'\n')

    def Cerrar(self):
        self.save.close()



#Aquí se declaran las variables iniciales y se da la primera instrucción
pw = Controlador()
pw.Escribir('c'+ '\r')
foldername = "./"+sys.argv[3]+"/"
filename=sys.argv[4]+".csv"
file = Archivo(foldername,filename)

muestras = 0 #Este es el contador de muestras

#estas son variables que se utilizaran para poder verificar los datos y obtener medidas que ayuden al analisis de estos
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
    #aquí se realiza la lectura del buffer, los datos se limpian antes de ser verificados
    out = str(pw.ContRead())
    data = out.split(',')
    tiempo = data[0][2:12]
    potencia = ""
    if(len(data) == 2):
        for k in str(data[1]):
            try:
                carac = int(k)
                potencia = potencia + str(k)
            except:
                if(str(k) == "-" or str(k) == "."):
                    potencia = potencia + str(k)
    #Se procede a hacer ciertos filtros para verificar la integridad de los datos y para despues no tener problemas con el analisis de estos
    #se realiza para el tiempo y la potencia
    try:
        temptiempo = float(tiempo)
        
    except:
        valid = False
        print("muestra invalida")
    if (float(tiempo) >= float(oldtiempo)+10000) or (tiempo == '') or (float(tiempo)<float(oldtiempo)) or (not valid):
        print ("timestamp not valid")
        break
    print(tiempo, " , ", potencia)

    try:
        temppotencia = float(potencia)
    except:
        valid = False
        print("potencia invalida")

    if (float(potencia)>-70) and (float(potencia)<0 )and (valid): # se descartan valores de potencia incoherentes
        #Al ya pasar este ultimo filtro se procede a añadir los datos en el csv y a realizar operaciones iterativas para el analisis.
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


    
    #En estas dos ultimas condiciones se evalua las opciones especificadas por el usuario, tomando en cuanta el número de muestras y el tiempo que ha pasado segun el RFPM
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
    
