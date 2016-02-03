# -*- coding: ISO-8859-1 -*-
#
# Fichero:	watcherSquid.py
# Copyright:	Junta de Andalucía <devmaster@guadalinex.org>
# Autor:	Maria Dolores Pérez Gutiérrez y Néstor Chacón Manzano
# Fecha:	lun mar 27 17:01:37 CET 2006
# Licencia:	GPL v.2
#
# Archivo contiene funciones ponen en marcha filtrado de contenido y 
# acciones asociadas (registros de navegacion, actualizacion de blacklists)

from func import *
from watcherMods import configura_fw,nick2uid,id_group
from inicSquid import reload_squid_conf_user
import func_blacklists

###COmpila base de datos de blacklists
def compila_libreria(objetivo,file_log):
    import os, os.path
    from inicSquid import actualiza_sqg_conf
    
    DBhome=consulta_campo('dbhome',file_log)
    SQGbin=consulta_campo('sqguard',file_log)
    SQconf=consulta_campo('conf_sq',file_log)
   
 
    actualiza_sqg_conf(file_log)

    if objetivo.find('all')!=-1:
        for entry in os.listdir(DBhome):
            name_entry=os.path.join(DBhome,entry)
            if os.path.isdir(name_entry):
                d_entry=name_entry+'/domains'
                if os.path.isfile(d_entry):
                    orden=SQGbin+' -c '+SQconf+'squidGuard.conf -C '+entry+'/domains'
                    MLOG = open("/tmp/milog2","a")
                    MLOG.write("voy a ejecutar %s\n" %orden)
                    MLOG.close()
                    os.system(orden)
                u_entry=name_entry+'/urls'
                if os.path.isfile(u_entry):
                    orden=SQGbin+' -c '+SQconf+'squidGuard.conf -C '+entry+'/urls'
                    MLOG = open("/tmp/milog2","a")
                    MLOG.write("voy a ejecutar %s\n" %orden)
                    MLOG.close()
                    os.system(orden)
    else:
        name_entry=os.path.join(DBhome,objetivo)
        if os.path.isdir(name_entry): 
            d_entry=name_entry+'/domains'
            if os.path.isfile(d_entry):
                orden=SQGbin+' -c '+SQconf+'squidGuard.conf -C '+objetivo+'/domains'
                MLOG = open("/tmp/milog2","a")
                MLOG.write("voy a ejecutar %s\n" %orden)
                MLOG.close()
                os.system(orden)
            u_entry=name_entry+'/urls'
            if os.path.isfile(u_entry):
                orden=SQGbin+' -c '+SQconf+'squidGuard.conf -C '+objetivo+'/urls'
                MLOG = open("/tmp/milog2","a")
                MLOG.write("voy a ejecutar %s\n" %orden)
                MLOG.close()
                os.system(orden)

###Modulo examina el estado de squid para el usuario indicado
def lanzado_squid(user,SQdirlog):
    """Devuelve True si instancia de squid para usuario indicado esta lanzada, 
    False en caso contrario"""
    import os.path 
    from os import system 

    file_pid=SQdirlog+user+'/squid.pid'
    if os.path.isfile(file_pid):
        return True
    return False	
    

###Modulo lanza la configuracion de squid del usuario indicado
def inic_squid(user,SQconf):
    """Inicia instancia de squid correspondiente a usuario indicado"""
    import os

    mje='Lanzando squid para usuario '+user
    escribe_log(mje,archivo.mefilog)

    reload_squid_conf_user(user, archivo.mefilog)
    orden='/usr/sbin/squid -D -f '+SQconf+'squid_'+user+'.conf 2>/dev/null'
    MLOG = open("/tmp/milog2","a")
    MLOG.write("orden %s\n" %orden)
    MLOG.close()

    os.system(orden)
    
###Modulo detiene la configuracion de squid del usuario indicado
def stop_squid(user,SQconf):
    """Detiene instancia de squid para usuario indicado"""
    import os

    mje='Deteniendo squid para usuario '+user
    escribe_log(mje,archivo.mefilog)
    orden='/usr/sbin/squid -k shutdown -f '+SQconf+'squid_'+user+'.conf 2>/dev/null'
    os.system(orden)
    
###Modulo aplica la nueva configuracion de squid para el usuario indicado
def reconf_squid(user,SQconf):
    """Realiza cambios pertinentes en instancia de squid para usuario indicado"""
    import os

    mje='Reconfigurando squid para usuario '+user
    escribe_log(mje,archivo.mefilog)
    orden='/usr/sbin/squid -k reconfigure -f '+SQconf+'squid_'+user+'.conf 2>/dev/null'
    os.system(orden)

    
###Modulo detiene todas las instancias lanzadas de squid
def detener_squid(file_conf):
    """Examina que instancias de squid estan activas y ordena su deteccion"""
    
    xmldoc=parse_file(file_conf)
    
    if xmldoc==-1:
        escribe_log("Error lectura previa a deteccion instancias de squid",archivo.mefilog)
        return

    SQdirlog=consulta_campo('logdir',archivo.mefilog)
    SQconf=consulta_campo('conf_sq',archivo.mefilog)
    usquid=users_control_web(archivo.mefilog)
    
    for user in usquid:
        if lanzado_squid(user,SQdirlog):
                stop_squid(user,SQconf)
                

###Modulo invocado por aplicacion para aplicar cambios producidos
###en instancias de squid lanzadas en el sistema
def reconfigure_squid(file_conf):
    """Examina que instancias de squid estan activas y las actualiza si han sufrido modificaciones en su configuracion"""
    
    xmldoc = parse_file(file_conf)
    
    if xmldoc==-1:
        escribe_log("Error lectura previa a reconfiguracion instancias de squid",archivo.mefilog)
        return
   
    SQdirlog=consulta_campo('logdir',archivo.mefilog)
    SQconf=consulta_campo('conf_sq',archivo.mefilog)
    
    uconect=users_conect()
    for user in uconect:
        if lanzado_squid(user,SQdirlog):
            reconf_squid(user,SQconf)
    
##Funcion examina que usuarios tienen abierta una sesion
##en el sistema, si para ellos existe una configuracion de squid
##y aun no esta lanzada, se lanza
##Se encarga a su vez de detener configuraciones de squid cuyo usuario
##ya ha abandonado el sistema
def apply_conf_squid(file_conf, squid_stopped):
    """Funcion encargada de activar, mantener y detener las diferentes instancias de
    squid configuradas en el sistema, segun si sus usuarios tiene sesiones abiertas
    y tienen habilitado el servicio web"""
   
    carga_iptables=False

    xmldoc=parse_file(file_conf)

    if xmldoc==-1:
        escribe_log("Error lectura previa a actualizacion instancias de squid",archivo.mefilog)
        return
 
    SQdirlog=consulta_campo('logdir',archivo.mefilog)
    SQconf=consulta_campo('conf_sq',archivo.mefilog)
  
    #extrae usuarios con sesiones abiertas y configuracion para squid
    #si su configuracion de squid no esta activa se inicia
    uconect=users_conect()


    for user in uconect:
        if not lanzado_squid(user,SQdirlog):
            inic_squid(user,SQconf)
            #ferrer, lo meto dentro del if, no se si esta dentro del if o del for.
        carga_iptables=True
        
    #extrae usuarios con politica de squid definida
    #si no tienen sesion abierta o servicio web activo y su configuracion de squid esta lanzada 
    #se detiene
    usquid=users_control_web(archivo.mefilog)
    for user in usquid:
        try:
            n=uconect.index(user)
        except ValueError:
            if lanzado_squid(user,SQdirlog):
                try:
                    ind=squid_stopped.index(user)
                except ValueError:
                    squid_stopped.append(user)
                    stop_squid(user,SQconf)
                carga_iptables=True
            else:
                try:
                    squid_stopped.remove(user)
                except ValueError:
                    pass
                    

    #se refrescan las iptables del sistema si ha cambiado la situacion
    if carga_iptables:
    	configura_fw()
    
    return squid_stopped

##Modulo comprueba si los directorios sobre los que trabaja acept tiene establecidos
##de manera correcta los permisos para el funcionamiento sin problemas de la aplicacion
def establece_permisos(file_conf):
    """Examina si la estructura de directorios de acept tiene los permisos correctos,
    si no es asi los modifica"""
    import os
    
    xmldoc = parse_file(file_conf)
   
    if xmldoc==-1:
        escribe_log("Error lectura previa a revision permisos sistema ",archivo.mefilog)
        return
 
    SQconf=consulta_campo('conf_sq',archivo.mefilog)
    SQGdir=consulta_campo('dir_sqg',archivo.mefilog)
    DBhome=consulta_campo('dbhome',archivo.mefilog)
    SARGdir=consulta_campo('sargrg',archivo.mefilog)
    SQGlib=consulta_campo('dbhome',archivo.mefilog)
    
    path=SQconf
    orden='chown -R squid:admin '+path
    os.system(orden)
    orden='chmod -R 770 '+path
    os.system(orden)
    
    path=SQGdir
    orden='chown -R squid:admin '+path
    os.system(orden)
    orden='chmod -R 770 '+path
    os.system(orden)
    
    path=DBhome[:DBhome.rfind('/')]
    orden='chown -R squid:admin '+path
    os.system(orden)    
    orden='chmod -R 770 '+path
    os.system(orden)
        
    path=SARGdir
    orden='chown -R squid:admin '+path
    os.system(orden)
    orden='chmod -R 770 '+path
    os.system(orden)
        
    path=SQGlib[:SQGlib.rfind('/')]
    orden='chown -R squid:admin '+path
    os.system(orden)

        
##Modulo comprueba si los directorios sobre los que trabaja acept tiene establecidos
##de manera correcta los permisos para el funcionamiento sin problemas de la aplicacion
def examina_permisos(file_conf):
    """Examina si la estructura de directorios de acept tiene los permisos correctos,
    si no es asi los modifica"""
    import os
    
    id_squid=nick2uid('squid')
    gid_squid=id_group('squid')
    xmldoc = parse_file(file_conf)
   
    if xmldoc==-1:
        escribe_log("Error lectura previa a revision permisos sistema ",archivo.mefilog)    
        return
 
    SQconf=consulta_campo('conf_sq',archivo.mefilog)
    SQGdir=consulta_campo('dir_sqg',archivo.mefilog)
    DBhome=consulta_campo('dbhome',archivo.mefilog)
    SARGdir=consulta_campo('sargrg',archivo.mefilog)
    SQGlib=consulta_campo('dbhome',archivo.mefilog)
    
    path=SQconf
    perm=os.stat(path)
    if perm[4]!=id_squid or perm[5]!=gid_squid:
        mje="Modificando permisos de "+path
        escribe_log(mje,archivo.mefilog)
        orden='chown -R squid:admin '+path
        os.system(orden)
    
    path=SQGdir
    perm=os.stat(path)
    if perm[4]!=id_squid or perm[5]!=gid_squid:
        mje="Modificando permisos de "+path
        escribe_log(mje,archivo.mefilog)
        orden='chown -R squid:admin '+path
        os.system(orden)
    
    path=DBhome[:DBhome.rfind('/')]
    perm=os.stat(path)
    if perm[4]!=id_squid or perm[5]!=gid_squid:
        mje="Modificando permisos de "+path
        escribe_log(mje,archivo.mefilog)
        orden='chown -R squid:admin '+path
        os.system(orden)    
        
    path=SARGdir
    perm=os.stat(path)
    if perm[4]!=id_squid or perm[5]!=gid_squid:
        mje="Modificando permisos de "+path
        escribe_log(mje,archivo.mefilog)
        orden='chown -R squid:admin '+path
        os.system(orden)
        
    path=SQGlib[:SQGlib.rfind('/')]
    perm=os.stat(path)
    if perm[4]!=id_squid or perm[5]!=gid_squid:
        mje="Modificando permisos de "+path
        escribe_log(mje,archivo.mefilog)
        orden='chown -R squid:admin '+path
        os.system(orden)

""" Modulos definidos para registro automatico de informacion de navegacion"""
        
##Modulo  lanza la herramienta que recopila la informacion de navegacion web (sarg)
##de los usuarios que tienen filtrado el acceso web
def genera_registros_periodicos(file_conf):
    """Lanza sqrg para los usuarios que tiene filtrado el acceso web, recopilando la 
    informacion en el directorio /var/www/squid-reports/$USER/Ultfecha-Actfecha"""
    
    import os, os.path
    import time, commands
    from func_navegacion import modifica_html
    
    xmldoc = parse_file(file_conf)

    if xmldoc==-1:
        escribe_log("Error lectura previa a generacion registros web ",archivo.mefilog)
        return 

    #extrae usuarios con control web
    usuarios=users_control_web(archivo.mefilog)
    
    #fechas comprende registro a generar
    last_date=consulta_campo('last_date',archivo.mefilog)
    date=time.localtime()
    act_date=time.strftime("%d%b%Y",date)
    
    name_reg=last_date.capitalize()+'-'+act_date.capitalize()
    sarg_bin=consulta_campo('sargbin',archivo.mefilog)
    SQconf=consulta_campo('conf_sq',archivo.mefilog)
    dir_log=consulta_campo('logdir',archivo.mefilog)
    sargrg=consulta_campo('sargrg',archivo.mefilog)
    
    for user in usuarios:
        destino=sargrg+'/'+user+'/'+name_reg
        
        if  not os.path.isdir(destino):
            mje='Se generan registros web de usuario '+user
            escribe_log(mje,archivo.mefilog)
            orden=sarg_bin+' -f '+SQconf+'sarg_'+user+'.conf'
            salida=commands.getoutput(orden)
            #comprobamos se han recogido resultados
            if salida.find('No se encontraron registros')==-1:       
                n_reg=salida[salida.rfind('/')+1:]
                dest_tmp=sargrg+'/'+user+'/'+n_reg
                if dest_tmp.find(destino)==-1:
                    modifica_html(user,name_reg,n_reg,file_conf)
                    os.system('mv '+dest_tmp+' '+destino)
                clean='echo " " >'+dir_log+user+'/access.log'
                os.system(clean)
    
    #modifica campo ultimos registros generados de fichero de configuracion
    escribe_log('Se actualiza fecha ultimos registros web generados',archivo.mefilog)
    actualiza_campo('last_date',act_date,archivo.mefilog)
    
#Funcion comprueba si han transcurrido los dias establecidos para recopilar
#los registros de navegacion de los usuarios controlados por squid
#Como restricción se supone este periodo no va a ser superior a 30 dias
#Compara la fecha registrada de la ultima recopilacion de registros de navegacion
#con la fecha actual del sistema
#formato fecha ultima actualizacion en fichero de config: dd/Mmm/aaaa
def guardar_reg_nav(file_conf):
    """Devuelve True si ha transcurrido el periodo establecido desde la ultima fecha
    para la recopilacion de los registros de navegacion, False en caso contrario"""
    import time
    
    xmldoc = parse_file(file_conf)

    if xmldoc==-1:
        escribe_log("Error lectura previa a almacenamiento registros web ",archivo.mefilog)
        return False
    
    #extrae fecha ultima generacion de regs de navegacion
    ult_act=consulta_campo('last_date',archivo.mefilog)
    frecuencia=consulta_campo('fr_recol',archivo.mefilog)
    date=time.localtime()
    act_date=time.strftime("%d%b%Y",date)
    
    if ult_act[5:].find(act_date[5:])!=-1:#fechas de mismo anno
        if ult_act[2:5].find(act_date[2:5])!=-1:#fechas de mismo mes
            if int(act_date[:2])-int(ult_act[:2])>=int(frecuencia):
                return True
            else:
                return False
        else:
            ult_m=indice_mes(ult_act[2:5])
            act_m=indice_mes(act_date[2:5])
            if int(act_m)-int(ult_m)==1:
                t_dias=dias_mes(ult_act[2:5])-int(ult_act[:2])+int(act_date[:2])
                if t_dias>=int(frecuencia):
                    return True
                else:
                    return False
            else:
                return True
            
    else:
        ult_m=indice_mes(ult_act[2:5])
        act_m=indice_mes(act_date[2:5])
        if int(ult_m)==12 and int(act_m)==1:
            t_dias=dias_mes(ult_act[2:5])-int(ult_act[:2])+int(act_date[:2])
            if t_dias>=int(frecuencia):
                return True
            else:
                return False
        else:
            return True
            
        
""" Modulos definidos para actualizacion automatica de blacklists"""

##Modulo comprueba si es necesario lanzar la actualizacion de las blacklists
##formato fecha ultima actualizacion en fichero de config: dd/mm/aaaa
##se supone todos los meses tienen 30 dias
def actualiza_blacklists(file_conf):
    """Devuelve True si se ha de lanzar la actualizacion automatica de blacklists con
    la configuracion actual, False en caso contrario"""
    import time
    
    xmldoc = parse_file(file_conf)

    if xmldoc==-1:
        escribe_log("Error lectura previa a comprobacion actualizacion blacklists ",archivo.mefilog)
        return False
 
    ult_act=consulta_campo('last_update',archivo.mefilog)
    frecuencia=consulta_campo('fr_update',archivo.mefilog)
    if frecuencia=='0':
        return False
    date=time.localtime()
    act_date=time.strftime("%d/%m/%Y",date)
    
    if ult_act[6:].find(act_date[6:])!=-1:#fechas de mismo anno
        if ult_act[3:5].find(act_date[3:5])!=-1:#fechas de mismo mes
            if int(act_date[:2])-int(ult_act[:2])>=int(frecuencia):
                return True
            else:
                return False
        else:
            nm= int(act_date[3:5])-int(ult_act[3:5])
            t_dias=(nm*30)-int(ult_act[:2])+int(act_date[:2])
            if t_dias>=int(frecuencia):
                return True
            else:
                return False
            
    else:
        nm=12-int(ult_act[3:5])+int(act_date[3:5])
        t_dias=(nm*30)-int(ult_act[:2])+int(act_date[:2])
        if t_dias>=int(frecuencia):
            return True
        else:
            return False


def limpia_espacio(file_conf):

    f=open(file_conf,"r")
    lineas=f.readlines()
    f.close()

    f=open(file_conf,"w")

    for i in lineas:
        if i!='\n' and i!='\t\n':
            f.write(i)

    f.close()

    
##Modulo lanza la actualizacion de las blacklists, comprueba para cada fuente
##si se dispone de version mas actual, si no es asi, se descarga, descomprime
##y actualiza archivo de configuracion en consecuencia
def ublacklists(file_conf):
    """Inicia el proceso de actualizacion de las blacklists a partir de las fuentes configuradas en el sistema"""
    import os, os.path, shutil
    from confSquid import actualiza_filtrado_usuarios,listado_blacklists,elimina_blacklist
    
    #elimina listas 
    # locales para evitar problemas filtrado usuario las tuviera configuradas
    # no locales para evitar problemas al cambiar blacklists
    listas=listado_blacklists(file_conf)
    for bl in listas:
        elimina_blacklist(bl,file_conf)

    xmldoc = parse_file(file_conf)

    if xmldoc==-1:
        escribe_log("Error lectura previa a actualizacion blacklists ",archivo.mefilog)
        return

    #ferrer Log
    milog2 = open("/tmp/milog2","a")
    milog2.write("#Iniciacion de Variables\n")
    milog2.close()

    #Ubicacion base de datos utiliza squidGuard
    DBhome=consulta_campo('dbhome',archivo.mefilog)
    #Ubicacion archivos de logs
    DLog=consulta_campo('logdir',archivo.mefilog)

    #Ubicacion archivos temporales
    TMP=consulta_campo('tmpdir',archivo.mefilog)
    #Denominacion archivo de log de esta aplicacion
    NLG=consulta_campo('filelog',archivo.mefilog)
    resultado_ok=0

    #ruta de archivo de logs
    FileLog=DLog+NLG
    #directorio donde se descargan archivos
    Ddown=DBhome+'/download'

    msj='Invocada actualizacion de blacklists'
    escribe_log(msj,FileLog)


    directorios = os.listdir(DBhome)
    if len(directorios) >= 1:
        for i in directorios:
            if i.find("white") == -1:
                orden = "rm -rf "+DBhome+"/"+i
                os.system(orden)
                MLOG = open("/tmp/milog2","a")
                MLOG.write("#Elimino/Limpio Blacklists "+i+"\n")
                MLOG.close()

    milog2 = open("/tmp/milog2","a")
    milog2.write("#Variables Inicializadas con exito\n")
    milog2.write("#Lanzando Control de Directorios\n")
    milog2.close()

    #Revision/recreacion de directorios implicados
    # temporal se limpia su contenido si existia
    func_blacklists.renuevadir(TMP,FileLog)
    # directorio de descarga se crea si no existia
    func_blacklists.creadir(Ddown,FileLog)
    milog2 = open("/tmp/milog2","a")
    milog2.write("#Terminado Control de Directorios\n")
    milog2.close()
    #lectura de fuentes url especificadas en archivo xml
    blacklists=xmldoc.getElementsByTagName('source')

    problems=[[],[]]
    for list in blacklists:
        #extrae direccion de etiqueta url en blacklist
        url=list.getElementsByTagName('url')[0].firstChild.data
        #extrae nombre de archivo a descargar
        m1=url.rfind('/')
        m2=url.rfind('=')
        if m1>m2:
            m=m1
        else:
            m=m2

        nombre_archivo=url[m+1:] #extrae nombre archivo a descargar

        #construye destinos temporal y final del archivo
        destino=Ddown+'/'+nombre_archivo
        dest_tmp=TMP+'/'+nombre_archivo

        milog2 = open("/tmp/milog2","a")
        milog2.write("#Contruyendo estructurac instalacion Blacklists\n")
        milog2.write("Creando destino %s - destino_temporal %s\n" %(dest_tmp,destino))
        milog2.close()

        #Modulo que descarga el archivo en una ubicacion temporal
        #comprueba se trate de una version mas reciente (si se dispone
        #de una anterior)
        #devuelve -1: ya se cuenta con la version actualizada
        #devuelve 1: no se tiene o necesita actualizarse
        cad_error='ERROR'
        milog2 = open("/tmp/milog2","a")
        milog2.write("#Procedemos a la descarga de Blacklists\n")
        milog2.close()
        nuevo_nombre=func_blacklists.descarga(url,nombre_archivo, dest_tmp,destino,Ddown,FileLog)
        milog2 = open("/tmp/milog2","a")
        milog2.write("#Terminada Descarga\n")
        milog2.close()
        if nuevo_nombre != '' :
            if nuevo_nombre.find(cad_error)!=-1:
                problems[0].append(url)
                problems[1].append(0)
            else:
                nombre_archivo=nuevo_nombre
                #reconstruye destinos temporal y final del archivo, una vez descargado
                destino=Ddown+'/'+nombre_archivo
                dest_tmp=TMP+'/'+nombre_archivo
                #se desplaza archivo a su destino
                shutil.copyfile(dest_tmp,destino)
                #se descomprime el archivo en carpeta temporal
                milog2 = open("/tmp/milog2","a")
                milog2.write("#Descomprimiendo Sources descargadas\n")
                milog2.close()
                resultado=func_blacklists.descomprime(destino,TMP,dest_tmp)

                if resultado != '':
                    resultado_ok=1
                    fullpath=os.path.join(TMP,resultado)
                    #se inserta las blacklists en la base de datos del xmldoc
                    xmldoc = parse_file(file_conf)
                    func_blacklists.inserta_blacklists(fullpath,DBhome,resultado,xmldoc,FileLog,file_conf)
                    milog2 = open("/tmp/milog2","a")
                    milog2.write("#Se procede a la Indexacion de las Blacklists\n")
                    milog2.close()
                else:
                    problems[0].append(url)
                    problems[1].append(1)

    if resultado_ok == 1:
        compila_libreria('all',archivo.mefilog)
        milog2 = open("/tmp/milog2","a")
        milog2.write("#Terminada Indexacion de las Blacklists\n")
        milog2.close()
        func_blacklists.renuevadir(TMP,FileLog)
        msj='Finalizada actualizacion de blacklists'
        escribe_log(msj,FileLog)
        actualiza_filtrado_usuarios(file_conf)
        limpia_espacio(file_conf)

    orden="rm -rf /var/tmp/BDB*"
    os.system(orden)
    milog2 = open("/tmp/milog2","a")
    milog2.write("Limpiando restos de indexacion\n")
    milog2.close()
    return problems

##Modulo evita colisiones con instancias de squid residuales no detenidas al detenerse mefistofelina
##Comprueba si hay algun proceso squid, o squidGuard lanzado y lo detiene
##si existe algun archivo de ejecucion de squid tambien lo elimina
def squid_residual(file_conf):
    """Elimina instancias de squid residuales y archivos de ejecucion de squid espureos"""
    import commands
    import os, os.path
    
    ##Si existe algun proceso de squid residual ejecutandose lo detiene
    orden='ps -e | grep squid'
    salida=commands.getoutput(orden)
    procs=salida.split('\n')
    aviso=False
    
    for proc in procs:
        if proc.find('squid')!=-1 and proc.find('ps -e | grep squid')==-1:
            if not aviso:
                mje='Limpiando instancias de squid'
                escribe_log(mje,archivo.mefilog)	
                aviso=True
                proc=proc.lstrip()
                id_proc=proc.split(' ')[0]
                try:
                    os.kill(int(id_proc),9)
                except OSError:
                    mje='Error deteniendo instacia de squid'
                    escribe_log(mje,archivo.mefilog)
        
    ##Si existe algun archivo residual de alguna ejecucion de squid lo elimina
    usuarios=users_control_web(archivo.mefilog)
    SQdirlog=consulta_campo('logdir',archivo.mefilog)

    if usuarios==[] or SQdirlog=='':
        return

    for usuario in usuarios:
        file_squid=SQdirlog+usuario+'/squid.pid'
        if os.path.isfile(file_squid):
            os.remove(file_squid)

