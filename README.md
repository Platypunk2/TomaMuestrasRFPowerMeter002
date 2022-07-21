<br />
<div align="center">

  <h3 align="center">Toma de Muestras RF Power Meter 002</h3>

  <p align="center">
    con Python
  </p>
</div>

## Descripción

Esta aplicación es especificamente para el RF Power Meter 002 de HCF ENGINEERING. La idea de este código es lograr conectarse con este aparato y poder insertar y extraer informacion del buffer.

### 🛠 Construído con:

* [Docker](https://www.docker.com)
* [Python](https://www.python.org)

## Sobre el código

El codigo ocupa dos paquetes de python que se deben de instalar mediante pip: pyserial y numpy. Gracias a que se realizo un docker, no es necesario que usted los insatele ya que estos estan especificados en el Dockerfile.

La idea del algoritmo es poder recompilar muestras en un csv, asi que simplemente lo que hace es habrir el puerto, se da una instrucción al buffer y se va monitoreando lo que el buffer tire como respuesta. Los datos son guardados en un .csv con el nombre especificado en las varibles al compilar el código.

## :shipit: Instalación

En primer lugar, se debe de tener claros los pre-requisitos, estas son:

### Pre-Requisitos

Tener Docker instalado
* [Installation Guide](https://docs.docker.com/compose/install/)

### Primeros pasos

Cabe decir que este codigo esta pensado para ser ocupado en sistema linux, preferiblemente ubuntu debido a donde se almacenan las tty que será de bastante importancia para trabajar con el puerto serial. 

Al ya tener los archivos del git descargados en las carpetas que más guste se procede a realizar los comandos de docker. Para crear la imagen se utiliza:

```curl
docker build -t ['nombre de la imagen en minusculas'] .
```

Luego se procede a realizar el docker run con los siguientes parametros:

```curl
docker run -it --name ['nombre del contenedor'] --privileged -v /dev:/dev ['nombre imagen']
```

Con estos dos comandos ya esta creada la imagen y el contenedor, para poder entrar a este se utilizar el siguiente comando:

```curl
docker start -i ['nombre contenedor']
```

Cuando salga de este debe aplicar el comando

```curl
docker stop ['nombre contenedor']
```

### Código

Al ya tener montado el contenedor solo queda ejecutar el código. El codigo se llama "RFPM002-cp_us.py" y al usar el comando desde la consola:

```curl
python RFPM002-cp_us.py -h
```
Se mostrara las variables que se deben de declarar para en la ejecución desde la cosola:

```curl
usage: RFPM002-cp_us.py [-h] [option] Number Carpeta Archivo

Script para Adquisicion de datos del Power Meter, donde se le pasa por parametro  el tiempo en minutos o el numero de muestras que se quieren tomar.
 Example: "RFPM002-cp_us.py s 1000 ./Mediciones_exterior Posicion1"
 Example: "RFPM002-cp_us.py t 10 ./Mediciones_exterior Posicion1"

positional arguments:
  [option]    s (samples), o 
              t (time).
  Number      for option=s ---> numero de muestras
              for option=t ---> tiempo en minutos.
  Carpeta     Nombre o ruta de la carpeta donde se guardaran los archivos.
              En caso de no existir la carpeta se crea automaticamente.
  Archivo     Nombre del archivo a guardar.

optional arguments:
  -h, --help  show this help message and exit

```
Al ya compilar el código con las configuraciones insertadas, este tardara 3 segundos incialmente para iniciar el buffer y despues, lo que se vaya a demorar, dependera de las opciones especificadas como la cantidad de muestras o el tiempo de captura.

## Elementos extras

* Power Meter

![image](https://user-images.githubusercontent.com/90724923/180317810-1f942937-644c-408d-a36d-47d258273130.png)

