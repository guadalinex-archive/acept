# -*- coding: ISO-8859-1 -*-
#
# Fichero:	mefiGlobal.py
# Copyright:	Junta de Andaluc� <devmaster@guadalinex.org>
# Autor:	Maria Dolores P�ez Guti�rez y N�tor Chac� Manzano
# Fecha:	lun mar 27 17:01:31 CET 2006
# Licencia:	GPL v.2
#
# Aqui se definen los objetos que tienen que poder modificarse desde cualquir punto del programa"""
#

# Clases

class glob:
    pass

# Bucle : Esta variable controla el while en mefistofelina.py que viene a ser el nucleo del programa.
# En caso de recibir un kill -15 se modifica a False.

# relee: al recibir un SIGCONT (18) el demonio vuelve a leer el archivo de configuracion
relee=glob()
relee.configuracion=False

archivo=glob()
archivo.configuracion='/etc/acept/watcherCat/watcherconf.xml'
archivo.backup='/etc/acept/watcherCat/watcherconf.bak'
archivo.mefilog='/var/log/acept/mefistofelina.log'
archivo.aceptlog='/var/log/acept/acept.log'

pathAcept=glob()
pathAcept.path='/usr/share/acept'

finaliza=glob()
finaliza.ya=False

actualizar=glob()
actualizar.config=False

indice=glob()
indice.matriz=0

tiempo=glob()
tiempo.aviso=5
tiempo.intervalo=45

usuari=glob()
usuari.id=""
usuari.serv=""

xy=glob()
xy.posicion=(0,0)

uid=glob()
uid.min="1001"

bl_lst=glob()
bl_lst.nombre=''

child=glob()
child.horarios=False
child.contenidos=False
child.servicios=False
child.listas=False
child.uso_web=False
child.uso_aplic=False
child.como=False
child.expresiones=False
