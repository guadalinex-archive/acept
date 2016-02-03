# -*- coding: ISO-8859-1 -*-
#
# Fichero:	watcherMods.py
# Copyright:	Junta de Andalucía <devmaster@guadalinex.org>
# Autor:	Maria Dolores Pérez Gutiérrez y Néstor Chacón Manzano
# Fecha:	lun mar 27 17:01:33 CET 2006
# Licencia:	GPL v.2
#
# Archivo que contiene conjunto de funciones empleadas por mefistofelina

import  gettext
from mefiGlobal import *
from func import parse_file, escribe_log, copia_seguridad


def conexiones ():
    """ Comprueba los puertos abiertos y los almacena en una tabla con el siguiente formato:
                tcp            ||            udp
    fila        0        1     2  ||     3       4    5
            puerto | ip | uid || puerto | ip | uid 
    
    No acepta ningun parametro de entrada"""

    # Lee las conexiones tcp actuales y lo vuelca en una lista
    ftcp=open('/proc/net/tcp','r')
    tmptcp=ftcp.readlines()
    ftcp.close()
    del(tmptcp[0])
    
    # Lee las conexiones udp actuales y lo vuelca en una lista
    fudp=open('/proc/net/udp','r')
    tmpudp=fudp.readlines()
    fudp.close()
    del(tmpudp[0])
    
    
    # Crea la estructura de la tabla
    tabla=[]
    for i in range(6):
        tabla.append([])
    
    # Inserta ip:puertos, uid tcp a la tabla
    for i in tmptcp:
        if i.split(":") !="00000000" and i.split(":") !="0100007F":
            tabla[0].append(i.split()[2])
            tabla[2].append(int(i.split()[7]))
    
    del tmptcp
    
    # Inserta ip:puertos, uid udp a la tabla
    for i in tmpudp:
        if i.split(":")[0] !="00000000" and i.split(":")[0] !="0100007F":
            tabla[3].append(i.split()[2])
            tabla[5].append(int(i.split()[7]))
    
    del tmpudp
    
    
    #Separa las ip de los puertos tcp
    filas=len(tabla[0])
    
    for j in range(filas):
        z=tabla[0][j].split(":")[1]
        tabla[1].append(tabla[0][j].split(":")[0])
        tabla[0][j]=int(z,16)
        
    filas=len(tabla[1])
    
    #Convierte las ip tcp hexadecimales
    for i in range(filas):
                
        for j in tabla[1][i]:
            tmp_car=[]
            
            for z in range(2,9,2):
                tmp_car.append(str(int(tabla[1][i][z-2:z],16)))
            
            tmp_car.reverse()
            
        ip=".".join(tmp_car)
        tabla[1][i]=ip
    
    #Separa las ip de los puertos udp
    filas=len(tabla[3])
    
    for j in range(filas):
        z=tabla[3][j].split(":")[1]
        tabla[4].append(tabla[3][j].split(":")[0])
        tabla[3][j]=int(z,16)
    
    filas=len(tabla[4])
    #Convierte las ip udp hexadecimales
    for i in range(filas):
        
        for j in tabla[4][i]:
            tmp_car=[]
            
            for z in range(2,9,2):
                tmp_car.append(str(int(tabla[4][i][z-2:z],16)))
            
            tmp_car.reverse()
        ip=".".join(tmp_car)
        tabla[4][i]=ip
        
    return tabla

def id_group (nick):
    """ Consulta /etc/passwd y devuelve el nick o el uid segun se le pase uno u otro, 
        en caso de no existir, o de pasarle un parametro incorrecto, devuelve False.
    """
    
    #Lee /etc/passwd 
    fpass=open('/etc/passwd','r')
    tmppass=fpass.readlines()
    fpass.close()
    
    usuario={}
    
    # Crea un diccionario de nicks
    for i in tmppass :
        usuario[i.split(":")[0]]=i.split(":")[3]
        
    # Consulta la existencia del nick y devuelve su gid o False
    gid=usuario.get(nick,False)
    return gid

def n2u_u2n (nick):
    """ Consulta /etc/passwd y devuelve el nick o el uid segun se le pase uno u otro, 
        en caso de no existir, o de pasarle un parametro incorrecto, devuelve False.
    """
    
    #Lee /etc/passwd 
    fpass=open('/etc/passwd','r')
    tmppass=fpass.readlines()
    fpass.close()
    
    # Valora si la consulta es una cadena(nick2uid)
    if type(nick) == str:
        usuario={}
    
        # Crea un diccionario de nicks
        for i in tmppass :
            usuario[i.split(":")[0]]=i.split(":")[2]
        
        # Consulta la existencia del nick y devuelve la uid o False
        uid=usuario.get(nick,False)
        return uid
    
    # Valora si la consulta es un entero (uid2nick)
    elif type(nick) == int:
        uid={}
        
        # Crea un diccionario de uids
        for i in tmppass :
            uid[i.split(":")[2]]=i.split(":")[0]
        
         # Consulta la existencia del uid y devuelve el nick o False
        usuario=uid.get(str(nick),False)
        return usuario
    
    # Los parametros son incorrectos.
    else:
        return False

def nick2uid(nombre):
    """ Alias para n2u_u2n """
    salida=n2u_u2n(nombre)
    return salida

def uid2nick(numero):
    """ Alias para n2u_u2n"""
    salida=n2u_u2n(numero)
    return salida  

def servicios():
    """Lee la descripcion de los servicios del archivo de configuracion 
    /etc/acept/watcherCat/watcherconf.xml  y devuelve una tabla """
    from xml import xpath
    
    # Vuelca el archivo xml
    xmldoc=parse_file(archivo.configuracion)
  
    #Crea una tabla temporal
    servicios=[]
    for i in range (3):
        servicios.append([])

    # Rellena la tabla temporal
    for i in xpath.Evaluate('/config/servicios/*',xmldoc):
        servicios[0].append(str(i.localName))
        indice=1
        for z in i.attributes.keys():
            servicios[indice].append(str(i.attributes[z].value))
            indice+=1

    cantidad=len(servicios[0])
    
    # Crea la tabla que vamos a devolver
    tabla=[]
    for num in range (3):
        tabla.append([])

    ejez=0

    # Corta varias cadenas de la tabla temporal y las coloca en campos propios,
    # lo que esta separado por ; se considera como una sucesion y lo que esta
    # separado por : como un rango. Por ejemplo
    # 1;3;9 = 1, 3, 9
    # 1;3:9 = 1, 3, 4, 5, 6, 7, 8, 9
    for i in range (cantidad):
        tabla[0].append(servicios[0][i])
        udp=servicios[1][i].split(";")
        tcp=servicios[2][i].split(";")
        tabla[1].append([])
        tabla[2].append([])
        for n in udp:
            rango=n.split(":")
            if len(rango)<2:
                tabla[1][ejez].append(n)	
            else:
                for contador in range(int(rango[0].split("-")[1]),int(rango[1].split("-")[1])+1,1):
                    tabla[1][ejez].append(rango[0].split("-")[0]+"-"+str(contador))
        for n in tcp:
            rango=n.split(":")
            if len(rango)<2:
                tabla[2][ejez].append(n)
            else:
                for contador in range(int(rango[0].split("-")[1]),int(rango[1].split("-")[1])+1,1):
                    tabla[2][ejez].append(rango[0].split("-")[0]+"-"+str(contador))
        ejez+=1
    return tabla

def usuarios ():
    """ Lee la seccion de los usuarios del archivo de configuracion y devuelve una tabla
        con los datos correspondientes a los consumos y limites de los servicios."""
    from xml import xpath
    
    # Vuelca el archivo de configuracion xml
    xmldoc=parse_file(archivo.configuracion)
    
    # Crea la tabla que vamos a devolver
    t=[]
    
    # Recorre todos los usuarios
    for i in xpath.Evaluate('/config/usuarios/*',xmldoc):
        
        # Crea el diccionario en el que almacenaremos los datos de cada usuario
        dic={}
        
        # Recorre los servicios que tiene cada usuario: web, ftp, etc.
        for z in xpath.Evaluate("/config/usuarios/"+str(i.localName)+"/*",xmldoc):
            
            # Crea una tabla en la que se almacena los datos de cada servicio: tiempo diario, etc.
	    tmp=[]
            
            # Recorre las especificaciones de cada servicio
            for y in xpath.Evaluate("/config/usuarios/"+str(i.localName)+"/"+str(z.localName)+"/*",xmldoc):
                
                # inserta en la tabla los datos del servicio: limite_diario, limite_semanal, limite_mensual,t otal_diario,
                # total_semanal, total_mensual y prorroga
		if str(y.localName) != "denegado" and str(y.localName) != "squid_pt" and y.childNodes:
			tmp.append(str(y.childNodes[0].data))
                
                # Inserta en el diccionario el contenido de la tabla, usa como primary key el nick+el servicio
            dic[str(i.localName)+"+"+str(z.localName)]=tmp
        
        # Inserta en la tabla que vamos a devolver el diccionario que hemos creado
        t.append(dic)
    
    # Ordena la tabla    
    t.sort()
    return(t)
    
##Modulo actualiza los consumos que han realizado de los servicios los usuarios
##monitorizados por acept, con la estructura de datos que recibe    
def actualiza_consumo (config):
    """ Actualiza el archivo de configuracion xml con el consumo actual de los servicios 
        Acepta como parametro una tabla con el usuario, el servicio, el campo y el tiempo.
        Campo y tiempo son listas."""
    from xml import xpath
   
    doc = parse_file(archivo.configuracion)
    
    iteraciones=len(config[0])
  
    for i in range (iteraciones):
        usuario=config[0][i]
        servicio=config[1][i]
        campo=config[2][i]
        tiempo=config[3][i]
        if xpath.Evaluate('/config/usuarios/'+usuario+'/'+servicio+'/limite_diario',doc)!=[]:
            j=0
            for c in campo:
                t=tiempo[j]
                xpath.Evaluate('/config/usuarios/'+usuario+'/'+servicio+'/'+c, doc)[0].firstChild.data=t
                j=j+1
    
    correcto=False
    while not correcto:
	try:
	    copia_seguridad() 
	    f2=open(archivo.configuracion,'w')
	    f2.write(doc.toxml())
	    f2.close()
	    correcto=True
	except:
	    correcto=False
    
    
def fecha ():
    """ Devuelve un string con la fecha con el siguiente formato:
    Hora Minuto Segundo dia_mes dia_semana semana Mes Anno, por ejemplo:
    '18 17 38 17 lun 42 10 2005'
    """
    import time

    hora=time.strftime("%H %M %S %d %a %U %m %Y",time.
    localtime())

    return hora

##Modulo devuelve la fecha del sistema registrada en el archivo de configuracion
def ultima_fecha():
    """Devuelve fecha registrada en archivo de configuracion de ultimo lanzamiento del programa"""
    from xml import xpath
    
    xmldoc=parse_file(archivo.configuracion)
    ult_fecha=xpath.Evaluate('/config/demonio/fecha',xmldoc)[0].childNodes[0].data
    
    return ult_fecha.split()
     
##Modulo modifica la fecha del sistema registrada en el archivo de configuracion
##con la fecha que recibe
def actualiza_fecha(nueva_fecha):
    """Actualiza fecha registrada en archivo de configuracion con la actual"""
    from xml import xpath
    
    xmldoc=parse_file(archivo.configuracion)
    xpath.Evaluate('/config/demonio/fecha',xmldoc)[0].childNodes[0].data=nueva_fecha
    
    correcto=False
    while not correcto:
	try:
	    copia_seguridad()
	    f2=open(archivo.configuracion,'w')
	    f2.write(xmldoc.toxml())
	    f2.close()
	    correcto=True
	except:
	    correcto=False

    
    return
     
def modifica_pam_d():
    return True
    # Comprueba que exista el directorio pam.d y se pueda escribir en el
    if os.access("/etc/pam.d",7):
        # Recorre todos los archivos dentro de /etc/pam.d
        for i in os.listdir("/etc/pam.d"):
            # Abre el archivo y lo guarda en una lista de strings
            if os.path.getsize("/etc/pam.d/"+i) > 0:
                f=open("/etc/pam.d/"+i,"r")
                fichero=f.readlines()
                f.close()
                f=open("/etc/pam.d/"+i,"w")
                lineas=len(fichero)
                hecho=False
                # Recorre el archivo buscando la cadena apropiada
                for x in range(lineas):
                    #Descomenta la cadena si existe, graba los cambios en f y modifica la bandera hecho a True
                    if fichero[x].split() == ['#','account','requisite','pam_time.so']:
                        fichero[x]="account requisite   pam_time.so"
                        f.write(fichero[x])
                        hecho=True
                    #Si ya existe sin comentar, graba los cambios en f y modifica la bandera hecho a True    
                    elif fichero[x].split() == ['account','requisite','pam_time.so']:
                        f.write(fichero[x])
                        hecho=True
                    # En cualquier otro caso graba la linea tal cual.
                    else:
                        f.write(fichero[x])
        # En caso de que no exista la cadena la incorpora al final del fichero
            if not hecho:
                f.write("account    requisite   pam_time.so\n")
        # guarda todos los cambios
            f.close()
        return True
    else:
        return False

def configura_time_conf():
    """Lee los horarios del archivo de configuracion 
    /etc/acept/watcherCat/watcherconf.xml  y configura el archivo /etc/security/time.conf """
    from xml import xpath
    
    # Vuelca el archivo xml
    xmldoc=parse_file(archivo.configuracion)
  #Crea una tabla temporal
    horarios=[]

    for i in range (2):
        horarios.append([])
    # Rellena la tabla temporal
    for i in xpath.Evaluate('/config/usuarios/*',xmldoc):
        horarios[0].append(str(i.localName))
        for z in i.attributes.keys():
            horarios[1].append(str(i.attributes[z].value))
    correcto=False
    while not correcto:
	try:
	    f=open('/etc/security/time.bak','w')
	    f1=open('/etc/security/time.conf','r')
	    for i in f1.readlines():
		f.write(i)
	    f.close()
	    f1.close()
	    
	    f2=open("/etc/security/time.conf","w")
	    elementos=len(horarios[0])
    
	    for i in range(elementos):
		#modificacion de mshk para versatilizar horarios
		f2.write("*;*;"+horarios[0][i]+";")
		nitems=len(horarios[1][i])/11 
		horas=horarios[1][i].replace('2359','2400')
		for j in range(nitems):
			f2.write(horas[j*11:(j+1)*11]+"|")
	    	f2.write("\n")

	    f2.close()
	    correcto=True
	except:
	    correcto=False



def calcula_tiempo(hora1,hora2):
    """Esta funcion calcula la diferencia de tiempo entre dos horas dadas.
   Toma dos strings como entrada, devuelve la cadena que refleja la diferencia
   de ambos tiempos """
    
    h1 = int(hora1[0:2])
    m1 = int(hora1[3:5])
    s1 = int(hora1[6:8])
    h2 = int(hora2[0:2])
    m2 = int(hora2[3:5])
    s2 = int(hora2[6:8])
    
    if s2 < s1 :
        s2=s2+60
        m2=m2-1
    if m2 < m1:
        m2=m2+60
        h2=h2-1
    if h2 < h1:
        h2=h2+24
    
    s=str(s2-s1)
    m=str(m2-m1)
    h=str(h2-h1)
    
    if len(s) < 2:
        s="0"+s
    if len(m) < 2:
        m="0"+m
    if len(h) < 2:
        h="0"+h
    
    return h+":"+m+":"+s

def suma_horas(hora1,hora2):
    """Esta funcion suma dos horas dadas.
   Toma dos string como entrada y devuelve otra que corresponde a la suma"""
    
    h1 = int(hora1[:-6])
    m1 = int(hora1[-5:-3])
    s1 = int(hora1[-2:])
    h2 = int(hora2[:-6])
    m2 = int(hora2[-5:-3])
    s2 = int(hora2[-2:])
    
    s=s1+s2
    m=m1+m2
    h=h1+h2
    
    while s > 59 or m > 59:
        if s > 59:
            s=s-60
            m=m+1
        if m > 59:
            m=m-60
            h=h+1
    
    s=str(s)
    m=str(m)
    h=str(h)
    
    if len(s) < 2:
        s="0"+s
    if len(m) < 2:
        m="0"+m
    if len(h) < 2:
        h="0"+h
    
    return h+":"+m+":"+s
    
def puerto2name(puerto,protocolo):
    """ Devuelve el nombre del servicio que corresponde a un puerto """
    serv=servicios()
    
    if protocolo == "tcp":
        iteraciones=len(serv[0])
        for i in range(iteraciones):
            for z in serv[2][i]:
                if z == "s-"+str(puerto):
                    return serv[0][i]
    elif protocolo == "udp":
        iteraciones=len(serv[0])
        for i in range(iteraciones):
            for z in serv[1][i]:
                if z == "s-"+str(puerto):
                    return serv[0][i]
    return "unknow"

def restricciones(d_us):
    """Devuelve los limites d eun usuario"""
    limit={}
    items=len(d_us)
    for i in range(items):
        for z in d_us[i].keys():
            if len(d_us[i][z]):
                lim=d_us[i][z][:3]
                lim.append(d_us[i][z][-1])
                limit[z]=lim
    return limit

def handler(signum,frame):
    	"""Funcion que se encarga de interceptar las señales que le llegan a mefistofelina"""
	import os, os.path, watcherSquid
    
	if signum == 18:
		relee.configuracion=True
	elif signum == 15:      
		
		watcherSquid.detener_squid(archivo.configuracion)
		os.system("iptables -F -t nat")
		os.system("iptables-restore < /etc/acept/watcherCat/limpia_iptables")
		finaliza.ya=True
        if os.path.isfile("/var/run/mefistofelina.pid"):
            try:
                os.remove("/var/run/mefistofelina.pid")
            except:
                pass
            
	return

##Modulo modifica todos los campos de nombre 'campo', por el valor indicado
##escribiendo cambios en archivo de configuracion
def restaura_consumo(campo,valor):
    """Modifica todos los nodos de nombre 'campo' con 'valor' """
    
    xmldoc=parse_file(archivo.configuracion)
    
    items=xmldoc.getElementsByTagName(campo)
    for item in items:
        item.firstChild.data=valor
      
    correcto=False
    while not correcto:
	try:
	    copia_seguridad()
	    f2=open(archivo.configuracion,'w')
	    f2.write(xmldoc.toxml())
	    f2.close()
	    correcto=True
	except:
	    correcto=False
  


def restaura_dia():
    """Limpia los registros correspondientes al cambio de dia"""
    restaura_consumo("total_diario","00:00:00")
    restaura_consumo("activo","1")

def restaura_semana():
    """Limpia los registros correspondientes al cambio de semana"""
    restaura_consumo("total_semanal","00:00:00")
    restaura_dia()
   
def restaura_todo():
    """Limpia todos los registros de tiempo, cuando se cambia de mes"""
    restaura_consumo("total_mensual","00:00:00")
    restaura_semana()

def verifica_users(file):
    import commands
    from func import extrae_users
    
    xmldoc = parse_file(file)
    users=extrae_users(archivo.mefilog)
    usuarios=xmldoc.getElementsByTagName('usuarios')
    
    modificado=False
    for user in users:
	orden='id -u '+user
	out=commands.getoutput(orden)
	try:
		n=int(out)
	except ValueError:
		mje='Usuario '+user+' ha desaparecido del sistema, se elimina'
		escribe_log(mje, archivo.mefilog)
		for node in usuarios[0].childNodes:
			if node.nodeName.find(user)!=-1 and user.find(node.nodeName)!=-1:
				usuarios[0].removeChild(node.previousSibling)
				usuarios[0].removeChild(node)
				modificado=True
				break
    if modificado:
	f=open(file,'w')
	f.write(xmldoc.toxml())
	f.close()

def configura_fw():
    """Construye el archivo de reglas iptables que ha de habilitarse en el sistema
    para la configuracion de usuarios y servicios actual"""
    from xml import xpath
    import os
    from func import users_conect, squid_port_user
    
    verifica_users(archivo.configuracion)    

    file_conf=archivo.configuracion
    xmldoc = parse_file(file_conf)
    reglas=[]
   
    for i in range(3):
        reglas.append([])
    
    #extrae_usuarios no-root con sesiones abiertas y configuracion de squid
    uconect=users_conect()
   
    for i in xpath.Evaluate('/config/usuarios/*',xmldoc):
        usuario=i.localName
        acceso=[]
	tiene_ftp=False
        for z in xpath.Evaluate('/config/usuarios/'+usuario+'/*',xmldoc):
            activo= xpath.Evaluate('/config/usuarios/'+i.localName+'/'+z.localName+'/activo',xmldoc)[0].childNodes[0].data
            if int(activo):
		if z.localName.find('web')!=-1:
			try:
                		wsquid=uconect.index(usuario)
			except ValueError:
                		pass
			else:
                		continue
                acceso.append(str(z.localName))
		if z.localName.find('ftp')!=-1:
			tiene_ftp=True
        reglas[0].append(str(usuario))
        reglas[1].append(acceso)
	if tiene_ftp:
		reglas[2].append('si')
	else:
		reglas[2].append('no')
    
    del xmldoc
    
    f=open("/etc/acept/watcherCat/reglas.iptables","w")

    #discrimina si insertar reglas para squid  en nat
    if uconect!=[]:#instancias de squid activas
        f.write("*nat\n")
        f.write(":PREROUTING ACCEPT [3371:578313]\n")
        f.write(":POSTROUTING ACCEPT [5996:365766]\n")
        f.write(":OUTPUT ACCEPT [6985:431198]\n")
        for user in uconect:
            cadena='proxy_'+user
            puerto=squid_port_user(user,archivo.mefilog)
            f.write(':'+cadena+' - [0:0]\n')
            f.write('-A OUTPUT -p tcp -m tcp --dport 80 -m owner --uid-owner '+user+' -j '+cadena+'\n')
            f.write('-A '+cadena+' -m owner --uid-owner squid -j RETURN\n')
            f.write('-A '+cadena+' -p tcp -j REDIRECT --to-ports '+puerto+'\n')
            
        f.write(':acept - [0:0]\n')
        f.write("COMMIT\n")
        
    f.write("*filter\n:INPUT ACCEPT [0:0]\n:FORWARD ACCEPT [0:0]\n:OUTPUT ACCEPT [0:0]\n")
    
    definiciones=servicios()
    for i in definiciones[0]:
        f.write(":"+i+" - [0:0]\n")
    f.write(":ftp_pasivo - [0:0]\n")
    
    items=len(definiciones[0])
    for i in range(items):
        for z in definiciones[1][i]:
            if len(z.split("s-")) > 1:
                f.write("-A OUTPUT -p udp --dport "+ z.split("s-")[1] +" -j "+ definiciones[0][i]+"\n")
        for z in definiciones[2][i]:
            if len(z.split("s-")) > 1:
                f.write("-A OUTPUT -p tcp --dport "+z.split("s-")[1] + " -j "+definiciones[0][i]+"\n")
      
    f.write("-A OUTPUT -p tcp --sport 1024: --dport 1024: -m state --state ESTABLISHED,RELATED -j ftp_pasivo\n")
    
    items=len(reglas[0])
    
    for i in range(items):
        todo_activo=False   
        for z in reglas[1][i]:
            if str(z) == "todo":
                todo_activo=True
		break		
            else:
                f.write("-A "+ z +" -m owner --uid-owner "+ reglas[0][i] + " -j ACCEPT\n")
	if not todo_activo:
		if reglas[2][i].find('si')!=-1:
			f.write("-A ftp_pasivo -m owner --uid-owner "+ reglas[0][i] +" -j ACCEPT\n")
		if uconect!=[]:
		    try:
			n=uconect.index(reglas[0][i])
     		    except ValueError:
			pass
		    else:
			puerto=squid_port_user(reglas[0][i],archivo.mefilog)
			f.write("-A OUTPUT -p tcp --dport "+puerto+" -m owner --uid-owner "+reglas[0][i]+" -j ACCEPT\n")
		f.write("-A OUTPUT -p ALL -d 127.0.0.1 -m owner --uid-owner "+reglas[0][i]+" -j ACCEPT\n")
		f.write("-A OUTPUT -p ALL -m owner --uid-owner "+ reglas[0][i] +" -j DROP\n")
	
    
    f.write("COMMIT\n")
    f.close()
    os.system("/sbin/iptables -F -t nat")
    os.system("iptables-restore < /etc/acept/watcherCat/limpia_iptables")
    os.system("/sbin/iptables-restore < /etc/acept/watcherCat/reglas.iptables")

def comprueba_fw():
    from random import randint
    from os import popen
    porcentaje=40
    if randint(1,100)<porcentaje:
        r=popen('iptables-save')
        reglas=r.read()
        if reglas.find('acept') < 0:
            try:
                configura_fw()    
            except:
                pass


def prorroga(us,serv):
        """ Esta funcion devuelve True si un servicio se encuentra prorrogado y false si no
        """
        from xml import xpath
        
        xmldoc=parse_file(archivo.configuracion)
        pr=xpath.Evaluate("/config/usuarios/"+us+"/"+serv+"/prorroga",xmldoc)
        if len(pr) == 0:
            return False
        else:
            seg_pr=int(pr[0].childNodes[0].data.split()[0].split(":")[2])
            min_pr=int(pr[0].childNodes[0].data.split()[0].split(":")[1])
            hora_pr=int(pr[0].childNodes[0].data.split()[0].split(":")[0])
            dia_pr=int(pr[0].childNodes[0].data.split()[1].split("/")[0])
            mes_pr=int(pr[0].childNodes[0].data.split()[1].split("/")[1])
            anno_pr=int(pr[0].childNodes[0].data.split()[1].split("/")[2])
            seg=int(fecha()[6:8])
            min=int(fecha()[3:5])
            hora=int(fecha()[0:2])
            dia=int(fecha().split()[3])
            mes=int(fecha().split()[6])
            anno=int(fecha().split()[7])
            
            if anno > anno_pr:
                return False
            elif anno_pr > anno:
                return True
            elif mes > mes_pr:
                return False
            elif  mes_pr > mes:
                return True
            elif dia > dia_pr:
                return False
            elif dia_pr > dia:
                return True
            elif hora > hora_pr:
                return False
            elif hora_pr > hora:
                return True
            elif min > min_pr:
                return False
            elif min_pr > min:
                return True
            elif seg_pr > seg:
                return True
            else:
                return False

def fija_horarios(usr,rango):
    	"""Modifica el archivo de configuracion con los nuevos horarios de acceso al pc"""

	xmldoc=parse_file(archivo.configuracion)
	usuarios=xmldoc.getElementsByTagName('usuarios')
	modificar=False
	for node in usuarios[0].childNodes:
		if node.nodeName.find(usr)!=-1 and usr.find(node.nodeName)!=-1:
		    modificar=True
		    break

	if modificar:
		node.setAttribute("acceso",rango)
	else:
		tab=usuarios[0].firstChild.nodeValue
		tab_hijo=tab+"\t"
		tab_salto="\n"+tab
		nodo_usuario=xmldoc.createElement(usr)
		nodo_usuario.setAttribute("acceso",rango)
		nodo_usuario.appendChild(xmldoc.createTextNode(tab_hijo))
		usuarios[0].appendChild(xmldoc.createTextNode(tab))
		usuarios[0].appendChild(nodo_usuario)
		usuarios[0].appendChild(xmldoc.createTextNode(tab_salto))

	correcto=False
	while not correcto:
	    try:
	        copia_seguridad()
		f2=open(archivo.configuracion,"w")
		f2.write(xmldoc.toxml())
		f2.close()
		correcto=True
	    except:
		correcto=False
		
def lista_usuarios(uid_min):
    """Muestra los usuarios a partir de un uid minimo, por defecto no muestra squid ni nobody """
    passwd=open("/etc/passwd","r")
    tmp_us=[]
    for i in passwd.readlines():
	nom=i.split(":")[0]
	uid=i.split(":")[2]
	if uid_min>=1000:
	    if int(uid)>= uid_min and nom != "nobody" and nom != "squid":
		tmp_us.append(nom)
	elif int(uid) >= uid_min:
	    tmp_us.append(nom)
	
    passwd.close()
    tmp_us.sort()
    return tmp_us



##FUNCIONES INCLUIDAS PARA ACABAR CON SESIONES DE USUARIOS
##NO PERMITIDAS

##Modulo extrae lista de usuarios actualmente conectados al sistema, ignora el usuario 'root'
def users_control_conected(file_conf):
    """Devuelve listado de usuarios definidos en acept
    con alguna sesión abierta en el sistema"""
    from xml import xpath
    import commands
    
    xmldoc=parse_file(file_conf)
    
    sal_obt=False
    while not sal_obt:
    	try:
		salida=commands.getoutput('who -q')
    	except IOError:
		pass
	else:
		sal_obt=True

    usuarios=[]
    for user in xpath.Evaluate('/config/usuarios/*', xmldoc):
        if salida.find(str(user.localName))!=-1 and user.localName.find('root')==-1:
            usuarios.append(str(user.localName))
            
    return usuarios
    
##Modulo comprueba si dia especificado se recoge en la politica de acceso 
def dia_permitido(permitido, dia):
    """Comprueba si dia esta incluido en la politica de acceso del usuario a la maquina"""
    if dia.find('LU')!=-1 or dia.find('MO')!=-1:
        return permitido.find('MO')
    if dia.find('MA')!=-1 or dia.find('TU')!=-1:
	return permitido.find('TU')
    if dia.find('MI')!=-1 or dia.find('WE')!=-1:
        return permitido.find('WE')
    if dia.find('JU')!=-1 or dia.find('TH')!=-1:
        return permitido.find('TH')
    if dia.find('VI')!=-1 or dia.find('FR')!=-1:
        return permitido.find('FR')
    if dia.find('SA')!=-1:
        return permitido.find('SA')
    if dia.find('DO')!=-1 or dia.find('SU')!=-1:
        return permitido.find('SU')
    
##Modulo extrae la lista de usuarios que no tienen acceso en este momento a la maquina
##consulta si existe algun proceso o sesion que pertenezca a alguno de estos usuarios
##si es asi los detiene o cierra
def saca_usuarios(file_conf, notif_sesion):

    """Si existen sesiones abiertas de usuarios que no pueden en este momento estar conectados
    cierra dichas sesiones mediante 'kill'"""
    import time, os, commands
    from xml import xpath
    
    xmldoc=parse_file(file_conf)
    conectados=users_control_conected(file_conf)
    
    fecha_act=time.localtime()
    dweek=time.strftime("%a",fecha_act)
    dsem=dweek[0:2]
    dsem=dsem.upper()
    
    hora_act=time.strftime("%H%M",fecha_act)

    killed=[]
    for user in conectados:
        acceso=xpath.Evaluate('/config/usuarios/'+user,xmldoc)[0].attributes["acceso"].value
        acceso=acceso.upper()
	
	indice=dia_permitido(acceso,dsem)
	fuera_horario=False

	if indice!=-1:
		#consulta horario para este dia
		hora_ini=acceso[indice+2:indice+6]
		hora_fin=acceso[indice+7:indice+11]

		if int(hora_act)>=int(hora_ini) and hora_fin.find('2359')!=-1:
			pass
		elif int(hora_act)<int(hora_ini) or int(hora_act)>=int(hora_fin):
     			fuera_horario=True
		else:
			#comprobacion para notificar aviso tiempo resta de uso
			try:
				ind=notif_sesion.index(user)
    			except ValueError:
				if int(hora_fin[:2])==int(hora_act[:2]):
					tiempo_resta=int(hora_fin[-2:])-int(hora_act[-2:])
				else:
					horas=int(hora_fin[:2])-int(hora_act[:2])
					tiempo_resta= horas*60 + int(hora_fin[-2:])-int(hora_act[-2:])	
				if tiempo_resta <= tiempo.aviso:	
					notif_sesion.append(user)
					mensaje='\"Le quedan solo '+str(tiempo_resta)+' minutos de uso del ordenador \"'
					os.system('/usr/share/acept/mensaje.py '+user+' '+mensaje+' 2>/dev/null')
			
    	else:
		fuera_horario=True

	if fuera_horario:
		mensaje='Abortando sesion de usuario '+user
		escribe_log(mensaje, archivo.mefilog)
		try:
			notif_sesion.remove(user)
		except ValueError:
			pass
    		salida=commands.getoutput('ps aux | grep '+user)
       		procesos=salida.split('\n')
       		for i in range(len(procesos)):
               		if procesos[i].find(user)==0:
               			l=len(user)
               			proceso=procesos[i][l:]
               			for j in range(len(proceso)):
                       			if proceso[j].isdigit():
                       	   			t=proceso[j:].find(' ')
                       	   			id_proceso=proceso[j:j+t]
                       				break
               			try:
                       			os.kill(int(id_proceso),15)
               			except OSError:
                       			pass 
               			else:
               				killed.append(id_proceso)
                  
            
    if killed!=[]:
        os.system('sleep 3')    
    #si tras 3 segundos procesos no han muerto los matamos con kill 9
    
    for proc in killed:
        consulta_proc=commands.getoutput('ps aux | grep '+id_proceso)
        consult_proc=consulta_proc.splitlines()
        for line in consult_proc:
            if line.find('grep')==-1:
                try:
                    os.kill(int(id_proceso),9)
                except OSError:
		    mje='Error al detener proceso '+str(id_proceso)
                    escribe_log(mje, archivo.mefilog)
     
    return notif_sesion
          

def usr_srv(usr):
    	"""Esta funcion acepta como parametros una cadena alfanumerica que es el nombre del usuario
	para el cual se van a listar los servicios que tiene configurados"""
	xmldoc=parse_file(archivo.configuracion)

	padre=xmldoc.getElementsByTagName('usuarios')[0]
	encontrado=False
	for s in padre.childNodes:
	    if s.nodeName.find(usr)!=-1 and usr.find(s.nodeName)!=-1:
		encontrado=True
		break
	srv=[]
	if encontrado:
		for i in s.childNodes:
			if i.localName:
				srv.append(i.localName)
			if i.localName == "todo":
				srv=[]
				return srv
	return srv

def uso_pc(usr):
    	""" Esta funcion acepta como parametro un nombre de usuario y devuelve tres listas
	una de horas y otra de dias de la semana en las cuales tiene permitido el acceso al pc"""

	xmldoc=parse_file(archivo.configuracion)
	usuarios=xmldoc.getElementsByTagName('usuarios')
	inicios=[]
	fines=[]
	dias=[]
	for node in usuarios[0].childNodes:
		if node.nodeName.find(usr)!=-1 and usr.find(node.nodeName)!=-1:
		    tmp=node.attributes['acceso'].value
		    num_dias=len(tmp)/11
		    for i in range(num_dias):
			dias.append(tmp[i*11:i*11+2])
			inicios.append(tmp[i*11+2:i*11+6]) 
			fines.append(tmp[i*11+7:i*11+11]) 
		    break
	
	return inicios, fines, dias

def serv_user(usr):
    	""" Esta funcion acepta como parametro un nombre de usuario, 
	devuelve un diccionario con los servicios configurados del usuario. horas consumidas y prorrogas"""
	a=-1
	
	for i in usuarios():
		a=a+1
		b=i.keys()
		
		if b and b[0].split("+")[0]==usr:
			return usuarios()[a]
	return {}

def mata_wxsu():
    	"""Se encarga de cerrar la ventana inicial que valida el password de root"""
	from os.path import exists
	from os import kill,remove
	if exists("/tmp/acept.pid"):
	    f=open("/tmp/acept.pid","r")
	    pid=f.read()
	    f.close()
	    remove('/tmp/acept.pid')
	    try:
		kill(int(pid),15)
	    except:
		pass


def elimina_srv(servicio):
    """Borra el sevicio que se le pase como argumento del archivo de configuracion"""
    from func import extrae_users, servicio_definido
    xmldoc=parse_file(archivo.configuracion)
    srvs=xmldoc.getElementsByTagName("servicios")
    j=False
    for i in srvs[0].childNodes:
	if i.localName == servicio:
	    srvs[0].removeChild(i)
	    if j:
		srvs[0].removeChild(j)
	j=i
    #si algun usuario tiene definida entrada para este servicio se elimina 
    users=extrae_users(archivo.mefilog)
    padre=xmldoc.getElementsByTagName('usuarios')[0]
    for user in users:
	if servicio_definido(user,servicio,archivo.mefilog):
		for nodo_user in padre.childNodes:
		    if nodo_user.nodeName.find(user)!=-1 and user.find(nodo_user.nodeName)!=-1:
			break	
		for hijo in nodo_user.childNodes:
			if hijo.nodeName.find(servicio)!=-1 and servicio.find(hijo.nodeName)!=-1:
				nodo_user.removeChild(hijo.previousSibling)
				nodo_user.removeChild(hijo)
				break
									    

    correcto=False
    while not correcto:
	try:
	    copia_seguridad()
	    f2=open(archivo.configuracion,"w")
	    f2.write(xmldoc.toxml())
	    f2.close()
	    correcto=True
	except:
	    correcto=False



def crea_srv(servicio,puertos_tcp,puertos_udp):
    """Acepta una cadena alfanumerica y dos listas de enteros, 
	crea un servicio de nombre igual a la cadena con los puertos tcp y udop de las listas
	y lo graba en el archivo de configuracion"""
    nivel=0
    if puertos_tcp!=['']:
	j=-10
	consecutivos=[]
	cons=False
	for i in puertos_tcp:
	    if int(i)==int(j)+1:
		consecutivos.append(str(j))
		cons=True
		if i==puertos_tcp[-1]:
		    consecutivos.append(i)
	    elif cons or i == puertos_tcp[-1]:
		consecutivos.append(j)
		consecutivos.append("-")
		cons=False
	    j=i
	cc=[]
	if len(consecutivos) > 0 and consecutivos[-1]!="-":
	    consecutivos.append("-")
	items=len(consecutivos)
	if items > 2:
	    ii=0
	    cc.append(consecutivos[ii])
	    for i in range(items):
		if consecutivos[i]=="-":
		    cc.append(consecutivos[i-1])
		    ii=i+1
		    if items!=i+1:
			cc.append(consecutivos[ii])
	    unicos_tcp=[]
	    for i in puertos_tcp:
		existe=False
		for j in consecutivos:
		    if i == j:
			existe=True
		if not existe:
		    unicos_tcp.append("s-"+i)
	    items=len(cc)
	    consecutivos_tcp=[]
	    for i in range(0,items,2):
		consecutivos_tcp.append("s-"+cc[i]+":"+"s-"+cc[i+1])
	else:
	    unicos_tcp=[]
	    consecutivos_tcp=['']
	    for i in puertos_tcp:
		unicos_tcp.append("s-"+i)
    else:
	nivel=nivel+1
	unicos_tcp=['']
	consecutivos_tcp=['']
   
    if puertos_udp!=['']:
	j=-10
	consecutivos=[]
	cons=False
	for i in puertos_udp:
	    if int(i)==int(j)+1:
		consecutivos.append(str(j))
		cons=True
		if i==puertos_udp[-1]:
		    consecutivos.append(i)
	    elif cons or i == puertos_udp[-1]:
		consecutivos.append(j)
		consecutivos.append("-")
		cons=False
	    j=i
	cc=[]
	if len(consecutivos) > 0 and consecutivos[-1]!="-":
	    consecutivos.append("-")
	items=len(consecutivos)
	if items > 2:
	    ii=0
	    cc.append(consecutivos[ii])
	    for i in range(items):
		if consecutivos[i]=="-":
		    cc.append(consecutivos[i-1])
		    ii=i+1
		    if items!=i+1:
			cc.append(consecutivos[ii])
	    unicos_udp=[]
	    for i in puertos_udp:
		existe=False
		for j in consecutivos:
		    if i == j:
			existe=True
	    
		if not existe:
		    unicos_udp.append("s-"+i)
	    items=len(cc)
	    consecutivos_udp=[]
	    for i in range(0,items,2):
		consecutivos_udp.append("s-"+cc[i]+":"+"s-"+cc[i+1])
	else:
	    unicos_udp=[]
	    consecutivos_udp=['']
	    for i in puertos_udp:
		unicos_udp.append("s-"+i)
    else:
	nivel=nivel+1
	unicos_udp=['']
	consecutivos_udp=['']
 
    if nivel != 2:
	tcp=''
	for i in unicos_tcp:
	    tcp=tcp+i+";"
	for i in consecutivos_tcp:
	    tcp=tcp+i+";"
	if tcp:
	    r=True
	    while r:
		if len(tcp)>0 and tcp[-1]==";":
		    tcp=tcp[:-1]
		else:
		    r=False
	udp=''
	for i in unicos_udp:
	    udp=udp+i+";"
	for i in consecutivos_udp:
	    udp=udp+i+";"
	if udp:
	    r=True
	    while r:
		if len(udp)>0 and udp[-1]==";":
		    udp=udp[:-1]
		else:
		    r=False


	xmldoc=parse_file(archivo.configuracion)

	todos_srv=xmldoc.getElementsByTagName("servicios")
	todos_srv[0].appendChild(xmldoc.createTextNode("\t"))
	nodo_srv=xmldoc.createElement(servicio)
	nodo_srv.setAttribute("tcp",tcp)
	nodo_srv.setAttribute("udp",udp)
	todos_srv[0].appendChild(nodo_srv)
	todos_srv[0].appendChild(xmldoc.createTextNode("\n\t"))
	correcto=False
	while not correcto:
	    try:
	        copia_seguridad()
		f2=open(archivo.configuracion,"w")
		f2.write(xmldoc.toxml())
		f2.close()
		correcto=True
	    except:
		correcto=False
	
    return nivel

def tod_serv(usuario):
    """ Comprueba si el usuario que se le pasa como parametro no tiene ninguna resctriccion en los servcios,
	en cuyo caso devuelve True, en caso de tener alguna, False"""
    xmldoc=parse_file(archivo.configuracion)
    
    padre=xmldoc.getElementsByTagName('usuarios')[0]
    encontrado=False
    for nodo in padre.childNodes:
	if nodo.nodeName.find(usuario)!=-1 and usuario.find(nodo.nodeName)!=-1:
	    encontrado=True
	    break    
   
    if encontrado:
	tod=nodo.getElementsByTagName("todo")
	if tod:
	    return True
	else:
	    return False
    else:
	return False


def avanz_usr(todos,user,tabla,listas):
    """Establece los parametros de un usuario en el archivo d econfiguracion"""
    xmldoc=parse_file(archivo.configuracion)
    usuarios=xmldoc.getElementsByTagName("usuarios")
    anterior=False	
    for i in usuarios[0].childNodes:
        if i.localName == user:
            usuarios[0].removeChild(i)
	    if anterior:
		 usuarios[0].removeChild(anterior)
	anterior=i

    usr=xmldoc.createElement(user)
    
    web=False 
    if listas!=[]: 
	web=True
	include_web=True
	cad_web="web"
    
    if todos:
        usr.appendChild(xmldoc.createTextNode("\n\t\t\t"))
        tod=xmldoc.createElement("todo")
        tod.appendChild(xmldoc.createTextNode("\n\t\t\t\t"))
        act=xmldoc.createElement("activo")
        act.appendChild(xmldoc.createTextNode("1"))
        tod.appendChild(act)
        tod.appendChild(xmldoc.createTextNode("\n\t\t\t"))
        usr.appendChild(tod)
        usr.appendChild(xmldoc.createTextNode("\n\t\t"))
	
    else:
	filas=len(tabla[0])
	for i in range(filas):
	    if web:
		if cad_web.find(tabla[0][i])!=-1:
		    include_web=False
	    usr.appendChild(xmldoc.createTextNode("\n\t\t\t"))
	    srv=xmldoc.createElement(tabla[0][i])
	    srv.appendChild(xmldoc.createTextNode("\n\t\t\t\t"))
	    if tabla[8][i]!="SL":
	    	lim_d=xmldoc.createElement("limite_diario")
	    	lim_d.appendChild(xmldoc.createTextNode(tabla[1][i]))
	    	srv.appendChild(lim_d)
	    	srv.appendChild(xmldoc.createTextNode("\n\t\t\t\t"))
	    	lim_s=xmldoc.createElement("limite_semanal")
	    	lim_s.appendChild(xmldoc.createTextNode(tabla[2][i]))
	    	srv.appendChild(lim_s)
	    	srv.appendChild(xmldoc.createTextNode("\n\t\t\t\t"))
	    	lim_m=xmldoc.createElement("limite_mensual")
	    	lim_m.appendChild(xmldoc.createTextNode(tabla[3][i]))
	    	srv.appendChild(lim_m)
	    	srv.appendChild(xmldoc.createTextNode("\n\t\t\t\t"))
	    	tot_d=xmldoc.createElement("total_diario")
	    	tot_d.appendChild(xmldoc.createTextNode(tabla[4][i]))
	    	srv.appendChild(tot_d)
	    	srv.appendChild(xmldoc.createTextNode("\n\t\t\t\t"))
	    	tot_s=xmldoc.createElement("total_semanal")
	    	tot_s.appendChild(xmldoc.createTextNode(tabla[5][i]))
	    	srv.appendChild(tot_s)
	    	srv.appendChild(xmldoc.createTextNode("\n\t\t\t\t"))
	    	tot_m=xmldoc.createElement("total_mensual")
	    	tot_m.appendChild(xmldoc.createTextNode(tabla[6][i]))
	    	srv.appendChild(tot_m)
	    	srv.appendChild(xmldoc.createTextNode("\n\t\t\t\t"))
	    	prorroga=xmldoc.createElement("prorroga")
	    	prorroga.appendChild(xmldoc.createTextNode(tabla[7][i]))
	    	srv.appendChild(prorroga)
	    	srv.appendChild(xmldoc.createTextNode("\n\t\t\t\t"))
	    
	    act=xmldoc.createElement("activo")
	    act.appendChild(xmldoc.createTextNode("1"))
	    srv.appendChild(act)
	    srv.appendChild(xmldoc.createTextNode("\n\t\t\t"))
	    usr.appendChild(xmldoc.createTextNode("\n\t\t\t"))
	    usr.appendChild(srv)
	    
    if web:
 	if include_web:
	    usr.appendChild(xmldoc.createTextNode("\n\t\t\t"))
	    srv=xmldoc.createElement("web")
	    srv.appendChild(xmldoc.createTextNode("\n\t\t\t\t"))
	    act=xmldoc.createElement("activo")
	    act.appendChild(xmldoc.createTextNode("1"))
	    srv.appendChild(act)
	    srv.appendChild(xmldoc.createTextNode("\n\t\t\t"))
	    usr.appendChild(xmldoc.createTextNode("\n\t\t\t"))
	    usr.appendChild(srv)
	
     
    usr.appendChild(xmldoc.createTextNode("\n\t\t"))
    usuarios[0].appendChild(xmldoc.createTextNode("\n\t\t"))
    usuarios[0].appendChild(usr)
    usuarios[0].appendChild(xmldoc.createTextNode("\n\t"))

    correcto=False
    while not correcto:
	try:
	    copia_seguridad()
	    f2=open(archivo.configuracion,"w")
	    f2.write(xmldoc.toxml())
	    f2.close()
	    correcto=True
	except:
	    correcto=False
 
    
##Modulo recopila datos de uso de servicios por parte de los usuarios, en mes anterior
##Es invocado cuando se detecta cambio de mes por parte de la aplicacion
##Datos almacenados corresponden a mes de ultima fecha de lanzamiento de la aplicacion
def recopila_aplic_mensual(file_conf):
    """Recopila en archivo de texto plano informacion de consumos de servicios en mes anterior"""
    from xml import xpath
    
    xmldoc=parse_file(file_conf)
    fecha=ultima_fecha()[2]+ultima_fecha()[3]
    
    file='/usr/share/acept/estadisticas/aplic_m'+fecha+'.txt'
    f=open(file,'w')
    
    servicios=xpath.Evaluate('/config/servicios/*',xmldoc)
    usuarios=xpath.Evaluate('/config/usuarios/*',xmldoc)
    for user in usuarios:
        if user.localName.find('root')==-1: # usuario no root
            for servicio in servicios:
                if xpath.Evaluate('/config/usuarios/'+user.localName+'/'+servicio.localName+'/total_mensual',xmldoc)!=[]:
                    consumido=xpath.Evaluate('/config/usuarios/'+user.localName+'/'+servicio.localName+'/total_mensual',xmldoc)[0].firstChild.data
                    if consumido.find('00:00:00')==-1:
                        f.write(str(servicio.localName)+' '+str(user.localName)+' '+consumido+' \n')
                    
    f.close()

##Modulo recopila datos de uso de servicios por parte de los usuarios, en semana anterior
##Es invocado cuando se detecta cambio de semana por parte de la aplicacion
##Datos almacenados corresponden a semana de ultima fecha de lanzamiento de la aplicacion
def recopila_aplic_semanal(file_conf):
    """Recopila en archivo de texto plano informacion de consumos de servicios en semana anterior"""
    from xml import xpath

    try:
    
        xmldoc=parse_file(file_conf)
        fecha=ultima_fecha()[1]+ultima_fecha()[3]
    
        file='/usr/share/acept/estadisticas/aplic_s'+fecha+'.txt'
        f=open(file,'w')
    
        servicios=xpath.Evaluate('/config/servicios/*',xmldoc)
        usuarios=xpath.Evaluate('/config/usuarios/*',xmldoc)
        for user in usuarios:
            if user.localName.find('root')==-1: # usuario no root
                for servicio in servicios:
                    if xpath.Evaluate('/config/usuarios/'+user.localName+'/'+servicio.localName+'/total_semanal',xmldoc)!=[]:
                        consumido=xpath.Evaluate('/config/usuarios/'+user.localName+'/'+servicio.localName+'/total_semanal',xmldoc)[0].firstChild.data
                        if consumido.find('00:00:00')==-1:
                            f.write(str(servicio.localName)+' '+str(user.localName)+' '+consumido+' \n')
        f.close()
    except:
        pass

def nodo_usuario(usr):
    """Crea la estructura basica de un usuario en el archivo de configuracion en caso de no existir"""
    xmldoc=parse_file(archivo.configuracion)
    
    padre=xmldoc.getElementsByTagName('usuarios')
    encontrado=False
    for user in padre[0].childNodes:
	if user.nodeName.find(usr)!=-1 and usr.find(user.nodeName)!=-1:
	    encontrado=True
	    break
    
    if not encontrado:
	tab=padre[0].firstChild.nodeValue+"\t"
	tab_hijo=tab+"\t"
	nodo_usuario=xmldoc.createElement(usr)
	nodo_usuario.setAttribute("acceso",'Mo0000-2359Tu0000-2359We0000-2359Th0000-2359Fr0000-2359Sa0000-2359Su0000-2359')
	nodo_usuario.appendChild(xmldoc.createTextNode(tab))
	todo=xmldoc.createElement("todo")
	activo=xmldoc.createElement("activo")
	activo.appendChild(xmldoc.createTextNode("1"))
	todo.appendChild(xmldoc.createTextNode(tab_hijo))
	todo.appendChild(activo)
	todo.appendChild(xmldoc.createTextNode(tab_hijo))
	nodo_usuario.appendChild(todo)
	nodo_usuario.appendChild(xmldoc.createTextNode(tab))
	padre[0].appendChild(xmldoc.createTextNode(padre[0].firstChild.nodeValue))
	padre[0].appendChild(nodo_usuario)
	padre[0].appendChild(xmldoc.createTextNode("\n"+padre[0].firstChild.nodeValue))
	
	
	correcto=False
	while not correcto:
	    try:
	        copia_seguridad()
		f2=open(archivo.configuracion,"w")
		f2.write(xmldoc.toxml())
		f2.close()
		correcto=True
	    except:
		correcto=False
	

