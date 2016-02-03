# -*- coding: ISO-8859-1 -*-
#
# Fichero:	func.py
# Copyright:	Junta de Andalucía <devmaster@guadalinex.org>
# Autor:	Maria Dolores Pérez Gutiérrez y Néstor Chacón Manzano
# Fecha:	lun mar 27 17:01:26 CET 2006
# Licencia:	GPL v.2
#
# Archivo contiene modulos basicos que son comunes a casi la totalidad de la aplicacion

from mefiGlobal import *
from xml.dom import minidom

def integridad_config():
    from shutil import copyfile
    from os.path import exists
 
    f=open(archivo.configuracion,'r')
    contenido=f.readlines()
    f.close()
    if not contenido:
	if exists(archivo.backup):
	    escribe_log('Se copia configuracion backup',archivo.mefilog)
	    copyfile(archivo.backup,archivo.configuracion)
	    return 0
	else:
	    escribe_log('Configuracion irrecuperable',archivo.mefilog)
	    return 0
    
    return 1

def copia_seguridad():
    from shutil import copyfile

    if integridad_config()==1:
	copyfile(archivo.configuracion,archivo.backup)


#Modulo parsea el contenido del archivo y lo devuelve
#llevando a cabo hasta 5 intentos en caso de fallo en la lectura
def parse_file(file_conf):
    """Parsea contenido de archivo y devuelve estructura parseada
    de archivo xml"""
    parsed=False
    intentos=0

    while not parsed and intentos < 10:
	try:
		xmldoc=minidom.parse(file_conf)
	except:
		pass
	else:
		parsed=True
	intentos=intentos+1

    if not parsed:
	return -1

    return xmldoc

#Modulo
def escribe_log(cadena,file):
    """Escribe cadena introducida en archivo de descriptor recibida
    anteponiendo el momento y la fecha del mensaje"""
    import time, os.path

    tmp=time.strftime("%d%m%y %H:%M:%S",time.localtime())
    
    if not os.path.isfile(file):
	f=open(file,'w')
    else:
	f=open(file,'a')
    
    f.write(tmp+' '+cadena+'\n')
  
    f.close()


##Modulo extrae valor de campo especificado, se considera unico en archivo de configuracion
def consulta_campo(campo,file_log):
    """Devuelve valor del campo especificado"""
    from xml import xpath
    xmldoc=parse_file(archivo.configuracion)
    
    if xmldoc==-1:
	mje='Error en lectura de campo '+campo+' de archivo de configuracion'
    	escribe_log(mje,file_log)	
    	return ''

    valor=xpath.Evaluate('/config/squid/'+campo,xmldoc)[0].firstChild.data
    
    return str(valor)
    
    
##Modulo modifica valor de campo por el especificado
def actualiza_campo(campo,valor, file_log):
    """Establece valor de campo especificado al indicado"""
    xmldoc=parse_file(archivo.configuracion)
    
    if xmldoc==-1:
	escribe_log("Intento fallido de escritura en archivo de configuracion",file_log)
	return

    padre=xmldoc.getElementsByTagName('squid')[0]
    for node in padre.childNodes:
	if node.nodeName.find(campo)!=-1 and campo.find(node.nodeName)!=-1:
    	    node.firstChild.data=valor
	    break
    
    #escribe cambios realizados a archivo de configuracion
    correcto=False
    while not correcto:
	try:
	    copia_seguridad()
    	    f=open(archivo.configuracion,'w')
    	    f.write(xmldoc.toxml())
    	    f.close()
	    correcto=True
	except:
	    correcto=False

def servicio_definido(user,servicio,file_log):
    """Devuelve True si el servicio aparece definido para el usuario"""
    from xml import xpath
    
    xmldoc=parse_file(archivo.configuracion)

    if xmldoc==-1:
	escribe_log("Error en lectura de servicios de archivo de configuracion",file_log)
	return False

    if xpath.Evaluate('/config/usuarios/'+user+'/'+servicio,xmldoc)==[]:
        return False #servicio no monitorizado
    else:
        return True
    
##Modulo comprueba si se esta monitorizando ese servicio para ese usuario, y esta
##activo
def servicio_monitorizado(user,servicio,file_log):
    """Devuelve True si el servicio esta definido, si el usuario tambien lo esta no siendo root
    y el servicio es monitorizado para dicho usuario y se encuentra activo"""
    from xml import xpath
    
    xmldoc=parse_file(archivo.configuracion)

    if xmldoc==-1:
	escribe_log("Error en lectura de servicios de archivo de configuracion",file_log)
	return False

    if xpath.Evaluate('/config/servicios/'+servicio,xmldoc)==[]:
        return False #servicio no monitorizado
    elif xpath.Evaluate('/config/usuarios/'+user,xmldoc)==[] or user.find('root')!=-1:
        return False # usuario no considerado o root
    elif xpath.Evaluate('/config/usuarios/'+user+'/'+servicio,xmldoc)==[]:
        return False #servicio no considerado para usuario
    elif xpath.Evaluate('/config/usuarios/'+user+'/'+servicio+'/limite_diario',xmldoc)==[]:
        return False #servicio sin limite de uso para usuario
    elif xpath.Evaluate('/config/usuarios/'+user+'/'+servicio+'/activo',xmldoc)[0].firstChild.data=='1':
        return True
    else:
        return False
        
##Modulo comprueba si se esta monitorizando ese servicio para ese usuario, y esta
##activo
def servicio_activo(user,servicio,file_log):
    """Devuelve True si el servicio esta definido, si el usuario tambien lo esta no siendo root
    y el servicio es monitorizado para dicho usuario y se encuentra activo"""
    from xml import xpath
    
    xmldoc=parse_file(archivo.configuracion)

    if xmldoc==-1:
	escribe_log("Error en lectura de servicios de archivo de configuracion",file_log)
	return False

    if xpath.Evaluate('/config/servicios/'+servicio,xmldoc)==[]:
        return False #servicio no monitorizado
    elif xpath.Evaluate('/config/usuarios/'+user,xmldoc)==[] or user.find('root')!=-1:
        return False # usuario no considerado o root
    elif xpath.Evaluate('/config/usuarios/'+user+'/'+servicio,xmldoc)==[]:
        return False #servicio no considerado para usuario
    elif xpath.Evaluate('/config/usuarios/'+user+'/'+servicio+'/activo',xmldoc)[0].firstChild.data=='1':
        return True
    else:
        return False
        
##Modulo comprueba si web activo para usuario 
def web_activo(user,file_log):
    """Comprueba si el servicio web esta activo para el usuario """

    return servicio_activo(user,'web',file_log)

    
##Modulo extrae lista de usuarios monitorizados en el sistema
##del archivo de configuracion de acept especificado
##Usada en funciones: cuenta_pg_users,trafico_usuario, pag_usuario,
##pag_cron, pag_nvisit, pag_trafic y pag_clave
def extrae_users(file_log):
    """Devuelve lista de usuarios que aparecen definidos en archivo de configuracion"""
    from xml import xpath
    
    f=parse_file(archivo.configuracion)
    
    if f==-1:
	escribe_log("Error en lectura de usuarios de archivo de configuracion",file_log)
	return []
    
    usuarios=[]
    
    for user in xpath.Evaluate('/config/usuarios/*', f):
        usuarios.append(str(user.localName))
    return usuarios
    
##Modulo comprueba si usuario especificado tiene alguna politica de acceso web definida
##en cuyo caso devuelve 1, sino devuelve 0
##Usada en:
def control_web_user(user, file_log):
    """Comprueba si usuario tiene alguna politica de filtrado web definida, si es asi devuelve 1"""
    from xml import xpath
    
    doc=parse_file(archivo.configuracion)
    
    if doc==-1:
	escribe_log("Error en lectura de politica web de archivo de configuracion",file_log)	
    	return 0

    try:
        if xpath.Evaluate('/config/usuarios/'+user+'/web/denegado/*',doc)==[]:
            return 0
        else:
            return 1
    except:
        return 0
        

##Modulo extrae lista de usuarios con servicio web monitorizado por squid en el sistema
##del archivo de configuracion de acept especificado
##Usada en funciones: cuenta_pg_users,trafico_usuario, pag_usuario,
##pag_cron, pag_nvisit, pag_trafic y pag_clave
def users_control_web(file_log):
    """Devuelve lista de usuarios con politicas de filtrado web definidas"""
    from xml import xpath
    
    f=parse_file(archivo.configuracion)

    if f==-1:
	escribe_log("Error en lectura de usuarios web de archivo de configuracion", file_log)
	return []

    usuarios=[]
    for user in xpath.Evaluate('/config/usuarios/*', f):
        if xpath.Evaluate('/config/usuarios/'+user.localName+'/web/denegado/*',f)!=[]:
            usuarios.append(str(user.localName))
    return usuarios
        

##Modulo extrae lista de usuarios no-root con sesiones abiertas y web activo  
##usadas para incluir reglas para redireccion de squid
##llamada desde: apply_conf_squid(watcherSquid), configura_fw(watcherMods)
def users_conect():
    """Devuelve lista de usuarios no-root con sesiones abiertas en el sistema, politicas de filtrado
   definidas y servicio web activo"""
    import commands
    #se extrae lista de usuarios conectados mediante orden 'who -q'
    #devuelve usuarios con sesiones abiertas y num. de sesiones
    orden='who -q'
    
    orden_executed=False
    while not orden_executed:
	try:
    		users=commands.getoutput(orden)
    	except IOError:
		pass
	else:
		orden_executed=True

    n_users=int(users[users.rfind('=')+1:]) #num de sesiones abiertas
    l_users=users.split(' ')
    
    #construye lista de usuarios no-root con sesiones abiertas y politicas de control web 
    controlados=[]

    for i in range(n_users):
        if l_users[i].find('\n')!=-1:
            l_users[i]=l_users[i][:l_users[i].find('\n')]
        if l_users[i].find('root')==-1:
            try:
                n=controlados.index(l_users[i])
            except ValueError:
                if control_web_user(l_users[i], archivo.mefilog)==1 and web_activo(l_users[i],archivo.mefilog):#si tiene politicas de control web definidas se incluye
                    controlados.append(l_users[i])
               
    
    return controlados

###Modulo consulta puerto configurado para configuracion de squid del usuario indicado        
def squid_port_user(user, file_log):
    """Devuelve puerto en el que se asigna escuche instancia de squid que corresponde a ese usuario"""
    from xml import xpath
    xmldoc = parse_file(archivo.configuracion)
    
    if xmldoc==-1:
	mje='Error en lectura de puerto squid de usuario '+user+' de archivo de configuracion'
	escribe_log(mje,file_log)
	return '55000'

    port=xpath.Evaluate('/config/usuarios/'+user+'/web/squid_pt',xmldoc)[0].childNodes[0].data
    
    return str(port)

    
def indice_mes(mes):
    """Devuelve indice numerico de mes indicado"""
    nombre=mes.capitalize()    

    if nombre.find('Jan')!=-1 or nombre.find('Ene')!=-1:
        return '01'
    if nombre.find('Feb')!=-1 :
        return '02'
    if nombre.find('Mar')!=-1 :
        return '03'
    if nombre.find('Apr')!=-1 or nombre.find('Abr')!=-1 :
        return '04'
    if nombre.find('May')!=-1 :
        return '05'
    if nombre.find('Jun')!=-1 :
        return '06'
    if nombre.find('Jul')!=-1 :
        return '07'
    if nombre.find('Aug')!=-1 or nombre.find('Ago')!=-1 :
        return '08'
    if nombre.find('Sep')!=-1 :
        return '09'
    if nombre.find('Oct')!=-1 :
        return '10'
    if nombre.find('Nov')!=-1 :
        return '11'
    if nombre.find('Dec')!=-1 or nombre.find('Dic')!=-1:
        return '12'
    else:
        return '00'
        
def dias_mes(mes):
    """Devuelve numero dias componen mes indicado"""
    nombre=mes.capitalize()

    if nombre.find('Jan')!=-1 or nombre.find('Ene')!=-1:
        return 30
    if nombre.find('Feb')!=-1:
        return 28
    if nombre.find('Mar')!=-1:
        return 31
    if nombre.find('Apr')!=-1 or nombre.find('Abr')!=-1:
        return 30
    if nombre.find('May')!=-1:
        return 31
    if nombre.find('Jun')!=-1:
        return 30
    if nombre.find('Jul')!=-1:
        return 31
    if nombre.find('Aug')!=-1 or nombre.find('Ago')!=-1:
        return 31
    if nombre.find('Sep')!=-1:
        return 30
    if nombre.find('Oct')!=-1:
        return 31
    if nombre.find('Nov')!=-1:
        return 30
    if nombre.find('Dec')!=-1 or nombre.find('Dic')!=-1:
        return 31
    else:
        return 0
        

