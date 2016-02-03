# -*- coding: ISO-8859-1 -*-
#
# Fichero:	inicSquid.py
# Copyright:	Junta de Andalucía <devmaster@guadalinex.org>
# Autor:	Maria Dolores Pérez Gutiérrez y Néstor Chacón Manzano
# Fecha:	lun mar 27 17:01:29 CET 2006
# Licencia:	GPL v.2
#
# Archivo contiene funciones para inicializacion de archivos configuran
# filtrado de contenido

from func import *

def reload_squid_conf_user(user, file_log):
    """ Vierte configuracion de squid para los usuarios en los respectivos archivos de configuracion 
   para squid """
    import commands
    import os  
    
    mje="Recargando configuracion squid usuario "+user
    escribe_log(mje, archivo.mefilog) 

    #toda la configuracion en archivo .xml
    xmldoc=parse_file(archivo.configuracion)
    #directorio donde se encuentra instalado squid
    SQdirlog=consulta_campo('logdir',file_log)
    #archivo plantilla de configuracion de squid
    SQconf=consulta_campo('conf_sq',file_log)
    #ruta donde se encuentra squidGuard
    SQguard=consulta_campo('sqguard',file_log)

    SQconffile=SQconf+'squid_acept.conf'
    squid_file=open(SQconffile,'r')


    lines=squid_file.readlines()

    #obtiene nombre maquina en la que se trabaja
    hostname=commands.getoutput('hostname')
    
    #obtiene direccion(es) IP(s) publica(s) de la maquina
    ips=[]
    out=commands.getoutput('/sbin/ifconfig | grep inet.addr')
    
    cad_ips=out.split()
    for cad in cad_ips:
        if cad.find('addr')!=-1:
            if cad.find('127.0.0.1')==-1:
                c=cad.split(':')
                ips.append(c[1])

    #archivo de config de squid para user
    SQUSERconf=SQconf+'squid_'+user+'.conf'
    
    MLOG = open("/tmp/milog2","a")
    MLOG.write("SQconf %s : SQUSERconf%s\n" %(SQconf,SQUSERconf))
    MLOG.close()
    

    #abrir archivo squid que vamos a sobreescribir
    squ_file=open(SQUSERconf,'w')
    #puerto destinado para configuracion de squid de este usuario
    squ_port=squid_port_user(user,file_log)
    
    ip_incluida=False
    
    sqg_user='squidGuard_'+user+'.conf'
    
    MLOG = open("/tmp/milog2","a")
    MLOG.write("http_port %s transparent\n" %squ_port)
    MLOG.write("access_log %s%s/access.log\n" %(SQdirlog,user))
    MLOG.write("cache_log %s%s/cache.log\n" %(SQdirlog,user))
    MLOG.write("cache_store_log %s%s/store.log\n" %(SQdirlog,user))
    MLOG.write("redirect_program %s -c %s%s\n" %(SQguard,SQconf,sqg_user))
    MLOG.write("visible_hostname %s\n" %hostname)
    MLOG.close()

    #escribimos configuracion personalizando para el usuario 'user'
    for i in range(len(lines)):
        if lines[i].find('http_port')!=-1 and lines[i].find('#')==-1:
            squ_file.write('http_port '+squ_port+' transparent\n')
        elif lines[i].find('access_log')!=-1 and lines[i].find('#')==-1:
            squ_file.write('access_log '+SQdirlog+user+'/access.log\n')
        elif lines[i].find('cache_log')!=-1 and lines[i].find('#')==-1:
            squ_file.write('cache_log '+SQdirlog+user+'/cache.log\n')
        elif lines[i].find('cache_store_log')!=-1 and lines[i].find('#')==-1:
            squ_file.write('cache_store_log '+SQdirlog+user+'/store.log\n')
        elif lines[i].find('pid_filename')!=-1 and lines[i].find('#')==-1:
            squ_file.write('pid_filename '+SQdirlog+user+'/squid.pid\n')
        elif lines[i].find('redirect_program')!=-1 and lines[i].find('#')==-1:
            squ_file.write('redirect_program '+SQguard+' -c '+SQconf+sqg_user+'\n')
        elif lines[i].find('visible_hostname')!=-1 and lines[i].find('#')==-1:
            squ_file.write('visible_hostname '+hostname+'\n')
        elif lines[i].find('acl hostname')!=-1 and not ip_incluida:
            for ind in range(len(ips)):
               	squ_file.write('acl '+hostname+' src '+ips[ind]+'/32 \n')
            ip_incluida=True
        elif lines[i].find('http_access allow hostname')!=-1:
            squ_file.write('http_access allow '+hostname+'\n')
        else:
            squ_file.write(lines[i])
        
    squ_file.close()
  
    
##Modulo crea archivos de configuracion de squid para los usuarios del sistema
##a los que se les aplica configuracion se squid (algun filtrado de su acceso web)
def inic_squid_users(file_log):
    """ Vierte configuracion de squid para los usuarios en los respectivos archivos de configuracion 
   para squid """
    import commands
    import os  
 
    #toda la configuracion en archivo .xml
    xmldoc=parse_file(archivo.configuracion)
    #directorio donde se encuentra instalado squid
    SQdirlog=consulta_campo('logdir',file_log)
    #archivo plantilla de configuracion de squid
    SQconf=consulta_campo('conf_sq',file_log)
    #ruta donde se encuentra squidGuard
    SQguard=consulta_campo('sqguard',file_log)

    usuarios=users_control_web(file_log)

    SQconffile=SQconf+'squid_acept.conf'
    squid_file=open(SQconffile,'r')
    lines=squid_file.readlines()

    #obtiene nombre maquina en la que se trabaja
    hostname=commands.getoutput('hostname')
    
    #obtiene direccion(es) IP(s) publica(s) de la maquina
    ips=[]
    out=commands.getoutput('/sbin/ifconfig | grep inet.addr')
    
    cad_ips=out.split()
    for cad in cad_ips:
        if cad.find('addr')!=-1:
            if cad.find('127.0.0.1')==-1:
                c=cad.split(':')
                ips.append(c[1])

    MLOG = open("/tmp/milog2","a")
    MLOG.write("http_port %s transparent\n" %squ_port)
    MLOG.write("access_log %s  %s /access.log\n" %(SQdirlog,user))
    MLOG.write("cache_log %s  %s /cache.log\n" %(SQdirlog,user))
    MLOG.write("cache_store_log %s %s /store.log\n" %(SQdirlog,user))
    MLOG.close()
    
    for user in usuarios:
        #archivo de config de squid para user
        SQUSERconf=SQconf+'squid_'+user+'.conf'
        #abrir archivo squid que vamos a sobreescribir
        squ_file=open(SQUSERconf,'w')
        #puerto destinado para configuracion de squid de este usuario
        squ_port=squid_port_user(user,file_log)
        #escribimos configuracion personalizando para el usuario 'user'
        ip_incluida=False
        for i in range(len(lines)):
            if lines[i].find('http_port')!=-1 and lines[i].find('#')==-1:
                squ_file.write('http_port '+squ_port+' transparent\n')
            elif lines[i].find('access_log')!=-1 and lines[i].find('#')==-1:
                squ_file.write('access_log '+SQdirlog+user+'/access.log\n')
            elif lines[i].find('cache_log')!=-1 and lines[i].find('#')==-1:
                squ_file.write('cache_log '+SQdirlog+user+'/cache.log\n')
            elif lines[i].find('cache_store_log')!=-1 and lines[i].find('#')==-1:
                squ_file.write('cache_store_log '+SQdirlog+user+'/store.log\n')
            elif lines[i].find('pid_filename')!=-1 and lines[i].find('#')==-1:
                squ_file.write('pid_filename '+SQdirlog+user+'/squid.pid\n')
            elif lines[i].find('redirect_program')!=-1 and lines[i].find('#')==-1:
                sqg_user='squidGuard_'+user+'.conf'
                squ_file.write('redirect_program '+SQguard+' -c '+SQconf+sqg_user+'\n')
            elif lines[i].find('visible_hostname')!=-1 and lines[i].find('#')==-1:
                squ_file.write('visible_hostname '+hostname+'\n')
            elif lines[i].find('acl hostname')!=-1 and not ip_incluida:
                for ind in range(len(ips)):
                    squ_file.write('acl '+hostname+' src '+ips[ind]+'/32\n')
                ip_incluida=True
            elif lines[i].find('http_access allow hostname')!=-1:
                squ_file.write('http_access allow '+hostname+'\n')
            else:
                squ_file.write(lines[i])
        
        squ_file.close()
        orden='chown squid:admin '+SQUSERconf
        os.system(orden)
  
##Modulo crea archivos de configuracion de sarg para los usuarios del sistema
##a los que se les aplica configuracion se squid (algun filtrado de su acceso web)
def inic_sarg_users(file_log):
    """Escribe archivos para configuracion de sarg para los usuarios con el servicio
    web filtrado"""
    #toda la configuracion en archivo .xml
    xmldoc=parse_file(archivo.configuracion)
    #directorio donde se encuentra instalado squid
    SQdirlog=consulta_campo('logdir',file_log)
    #archivo plantilla de configuracion de sarg
    SARGconf=consulta_campo('conf_sarg',file_log)
    #directorio donde se almancenan registros generados por sarg
    SARGdir=consulta_campo('sargrg',file_log)
    
    usuarios=users_control_web(file_log)

    MLOG = open("/tmp/milog2","a")
    MLOG.write("---------inic_sarg_users\n")
    MLOG.write("SARGconf %s : SARGdir %s\n" %(SARGconf,SARGdir))
    MLOG.close()

    sarg_file=open(SARGconf,'r')
    lines=sarg_file.readlines()

    for user in usuarios:
        #archivo de config de squid para user
        path=SARGconf[:SARGconf.rfind('/')]
        SARGUSERconf=path+'/sarg_'+user+'.conf'
        #abrir archivo squid que vamos a sobreescribir
        sgu_file=open(SARGUSERconf,'w')
        #escribimos configuracion personalizando para el usuario 'user'

        for i in range(len(lines)):
            if lines[i].find('access_log')!=-1 and lines[i].find('#')==-1:
                sgu_file.write('access_log '+SQdirlog+user+'/access.log\n')
            elif lines[i].find('output_dir')!=-1 and lines[i].find('#')==-1:
                sgu_file.write('output_dir '+SARGdir+'/'+user+'\n')
            else:
                sgu_file.write(lines[i])
        
        sgu_file.close()

##Modulo que refleja la configuracion de squidguard definida en el archivo de configuracion xml
##en los archivos de los usuarios involucrados    
def apply_conf_squidguard(file_log):
    """Vierte configuracion de filtrado de contenido para usuarios recogida en archivo de configuracion
    en correspondientes archivos con los que trabajaran las instancias de squidguard"""
    from xml import xpath
    import os   
    
 
    xmldoc=parse_file(archivo.configuracion)
    
    #directorio donde se encuentra instalado squid
    SQconf=consulta_campo('conf_sq',file_log)
    DBHOME=consulta_campo('dbhome',file_log)
    LOGDIR=consulta_campo('logdir',file_log)
    #extrae pag. muestra por defecto cuando acceso denegado a alguna url
    PAGE_DFL=consulta_campo('page_dfl',file_log)
    
    usuarios=users_control_web(file_log)

    groups=xmldoc.getElementsByTagName('group')
    grupos_actuales=[]
    for grp in groups:
        grupos_actuales.append(str(grp.attributes["tag"].value))

    for user in usuarios:
        #archivo de config de squidguard para user
        SQGconf=SQconf+'squidGuard_'+user+'.conf'
        #abrir archivo squidguard.conf que vamos a sobreescribir
        sqg_file=open(SQGconf,'w')

        sqg_file.write('dbhome '+DBHOME+'\n')
        sqg_file.write('logdir '+LOGDIR+'\n')

        sqg_file.write('\n#DESTINATION CLASSES\n')
        #inserta los grupos en la seccion DESTINATION CLASSES

        list_usuario=[]
        for list in xpath.Evaluate("/config/usuarios/"+user+"/web/denegado/*",xmldoc):
            list_usuario.append(str(list.attributes["tag"].value))
        
        for grp in groups:
            nombre_group=str(grp.attributes["tag"].value)
            try:
                ind_lu=list_usuario.index(nombre_group)
            except ValueError:
                pass
            else:
            	sqg_file.write('dest '+nombre_group+' {\n')
            	for entry in grp.childNodes:
            	    if entry.localName:
            	        if entry.localName.find('entry')!=-1:
            	            tag=entry.attributes["tag"].value
            	            sqg_file.write('\t '+tag[:-1]+'list \t'+nombre_group+'/'+tag+'\n')
            	sqg_file.write('\n}\n')
 
        #inserta la lista blanca definida para el usuario
        sqg_file.write('dest white_'+user+' {\n')
        sqg_file.write('\t domainlist \t white_'+user+'/domains\n')
        sqg_file.write('\n}\n')
    
        sqg_file.write('\n #ACL DEFIITIONS\n')
        #inserta las acls en la seccion ACL DEFINITIONS

        sqg_file.write('acl {\n')
        sqg_file.write('\t default {\n')
        sqg_file.write('\t\t pass white_'+user)
        for list in xpath.Evaluate("/config/usuarios/"+user+"/web/denegado/*",xmldoc):
            cad_list=str(list.attributes["tag"].value)
            try:
                indg=grupos_actuales.index(cad_list)
            except ValueError:
                pass
            else:   
                sqg_file.write(' !'+cad_list)
        sqg_file.write('\n\t\t redirect '+PAGE_DFL+'\n\t}\n}\n')
    

    
        sqg_file.close()
        orden='chown squid:admin '+SQGconf      
        os.system(orden) 

##Modulo examina si existen los directorios que se necesitan para el filtrado de contenido
##para cada usuario, si no existen se crean y se establecen los permisos adecuados
def inic_direct_users(file_log):
    """Crea estructura para filtrado de contenido para usuarios para ls que se ha configurado
    con permisos correspondientes"""
    import os, os.path
    xmldoc=parse_file(archivo.configuracion)
    
    SQconf=consulta_campo('conf_sq',file_log)
    SQdirlog=consulta_campo('logdir',file_log)
    SARGdir=consulta_campo('sargrg',file_log)
    DBhome=consulta_campo('dbhome',file_log)
 
    usuarios=users_control_web(file_log)
    
    for user in usuarios:
        #comprobar si tiene su directorio de logs
        dlog=SQdirlog+user
        if not os.path.isdir(dlog):
            os.system('mkdir '+dlog)
            fwdlog=dlog+'/access.log'
            f=open(fwdlog,'w')
            f.close()
        #comprobar si tiene su lista blanca creada, con archivo de dominios
        wlist=DBhome+'/white_'+user
        if not os.path.isdir(wlist):
            os.system('mkdir '+wlist)
            fwlist=wlist+'/domains'
            f=open(fwlist,'w')
            f.close()
        #comprobar si tiene su directorio para sarg
        sgdir=SARGdir+'/'+user
        if not os.path.isdir(sgdir):
            os.system('mkdir '+sgdir)        
        
        permiso='chmod -R 770 '
        os.system(permiso+SQconf)
        os.system(permiso+DBhome)
        os.system(permiso+SARGdir)
        permiso='chown -R squid:admin '
        os.system(permiso+SQconf)
        os.system(permiso+DBhome)
        os.system(permiso+SARGdir)

    varlog='chown -R squid:admin /var/log/acept'
    os.system(varlog)

##Modulo crea archivos de configuracion de squid para los usuarios del sistema
##a los que se les aplica configuracion se squid (algun filtrado de su acceso web)
def inic_squid_user(user,file_log):
    """ Vierte configuracion de squid para los usuarios en los respectivos archivos de configuracion 
   para squid """
    import commands
    import os  

 
    #toda la configuracion en archivo .xml
    xmldoc=parse_file(archivo.configuracion)
    #directorio donde se encuentra instalado squid
    SQdirlog=consulta_campo('logdir',file_log)
    #archivo plantilla de configuracion de squid
    SQconf=consulta_campo('conf_sq',file_log)
    #ruta donde se encuentra squidGuard
    SQguard=consulta_campo('sqguard',file_log)

    SQconffile=SQconf+'squid_acept.conf'
    squid_file=open(SQconffile,'r')
    lines=squid_file.readlines()

    #obtiene nombre maquina en la que se trabaja
    hostname=commands.getoutput('hostname')
    

    #obtiene direccion(es) IP(s) publica(s) de la maquina
    ips=[]
    out=commands.getoutput('/sbin/ifconfig | grep inet.addr')
    
    cad_ips=out.split()
    for cad in cad_ips:
        if cad.find('addr')!=-1:
                if cad.find('127.0.0.1')==-1:
                    c=cad.split(':')
                    ips.append(c[1])

    #archivo de config de squid para user
    SQUSERconf=SQconf+'squid_'+user+'.conf'
    #abrir archivo squid que vamos a sobreescribir
    squ_file=open(SQUSERconf,'w')
    #puerto destinado para configuracion de squid de este usuario
    squ_port=squid_port_user(user,file_log)
    #escribimos configuracion personalizando para el usuario 'user'
    ip_incluida=False


    for i in range(len(lines)):
        if lines[i].find('http_port')!=-1 and lines[i].find('#')==-1:
            squ_file.write('http_port '+squ_port+' transparent\n')
        elif lines[i].find('access_log')!=-1 and lines[i].find('#')==-1:
            squ_file.write('access_log '+SQdirlog+user+'/access.log\n')
        elif lines[i].find('cache_log')!=-1 and lines[i].find('#')==-1:
            squ_file.write('cache_log '+SQdirlog+user+'/cache.log\n')
        elif lines[i].find('cache_store_log')!=-1 and lines[i].find('#')==-1:
            squ_file.write('cache_store_log '+SQdirlog+user+'/store.log\n')
        elif lines[i].find('pid_filename')!=-1 and lines[i].find('#')==-1:
            squ_file.write('pid_filename '+SQdirlog+user+'/squid.pid\n')
        elif lines[i].find('redirect_program')!=-1 and lines[i].find('#')==-1:
            sqg_user='squidGuard_'+user+'.conf'
            squ_file.write('redirect_program /usr/bin/squidGuard -c '+SQconf+sqg_user+'\n')
        elif lines[i].find('visible_hostname')!=-1 and lines[i].find('#')==-1:
            squ_file.write('visible_hostname '+hostname+'\n')
        elif lines[i].find('acl hostname')!=-1 and not ip_incluida:
            for ind in range(len(ips)):
               	squ_file.write('acl '+hostname+' src '+ips[ind]+'/32\n')
            ip_incluida=True
        elif lines[i].find('http_access allow hostname')!=-1:
            squ_file.write('http_access allow '+hostname+'\n')
        else:
            squ_file.write(lines[i])
        
    squ_file.close()
    orden='chown squid:admin '+SQUSERconf
    os.system(orden)
  
##Modulo crea archivos de configuracion de sarg para los usuarios del sistema
##a los que se les aplica configuracion se squid (algun filtrado de su acceso web)
def inic_sarg_user(user,file_log):
    """Escribe archivos para configuracion de sarg para los usuarios con el servicio
    web filtrado"""
    #toda la configuracion en archivo .xml
    xmldoc=parse_file(archivo.configuracion)
    #directorio donde se encuentra instalado squid
    SQdirlog=consulta_campo('logdir',file_log)
    #archivo plantilla de configuracion de sarg
    SARGconf=consulta_campo('conf_sarg',file_log)
    #directorio donde se almancenan registros generados por sarg
    SARGdir=consulta_campo('sargrg',file_log)
    
    sarg_file=open(SARGconf,'r')
    lines=sarg_file.readlines()

    #archivo de config de squid para user
    path=SARGconf[:SARGconf.rfind('/')]
    SARGUSERconf=path+'/sarg_'+user+'.conf'
    #abrir archivo squid que vamos a sobreescribir
    sgu_file=open(SARGUSERconf,'w')
    #escribimos configuracion personalizando para el usuario 'user'
    for i in range(len(lines)):
        if lines[i].find('access_log')!=-1 and lines[i].find('#')==-1:
            sgu_file.write('access_log '+SQdirlog+user+'/access.log\n')
        elif lines[i].find('output_dir')!=-1 and lines[i].find('#')==-1:
            sgu_file.write('output_dir '+SARGdir+'/'+user+'\n')
        else:
            sgu_file.write(lines[i])
        
    sgu_file.close()

##Modulo que refleja la configuracion de squidguard definida en el archivo de configuracion xml
##en los archivos de los usuarios involucrados    
def apply_conf_squidguard_user(user,file_log):
    """Vierte configuracion de filtrado de contenido para usuarios recogida en archivo de configuracion
    en correspondientes archivos con los que trabajaran las instancias de squidguard"""
    from xml import xpath
    import os

    xmldoc=parse_file(archivo.configuracion)
    
    #directorio donde se encuentra instalado squid
    SQconf=consulta_campo('conf_sq',file_log)
    DBHOME=consulta_campo('dbhome',file_log)
    LOGDIR=consulta_campo('logdir',file_log)
    #extrae pag. muestra por defecto cuando acceso denegado a alguna url
    PAGE_DFL=consulta_campo('page_dfl',file_log)
    

    #archivo de config de squidguard para user
    SQGconf=SQconf+'squidGuard_'+user+'.conf'
    #abrir archivo squidguard.conf que vamos a sobreescribir
    sqg_file=open(SQGconf,'w')

    sqg_file.write('dbhome '+DBHOME+'\n')
    sqg_file.write('logdir '+LOGDIR+'\n')

    sqg_file.write('\n#DESTINATION CLASSES\n')
    #inserta los grupos en la seccion DESTINATION CLASSES

    list_usuario=[]
    for list in xpath.Evaluate("/config/usuarios/"+user+"/web/denegado/*",xmldoc):
        list_usuario.append(str(list.attributes["tag"].value))
    
    groups=xmldoc.getElementsByTagName('group')
    for grp in groups:
        nombre_group=str(grp.attributes["tag"].value)
        try:
            ind_lu=list_usuario.index(nombre_group)
        except ValueError:
            pass
        else:
            sqg_file.write('dest '+nombre_group+' {\n')
            for entry in grp.childNodes:
                try:
                    if entry.localName.find('entry')!=-1:
			    tag=entry.attributes["tag"].value
			    sqg_file.write('\t '+tag[:-1]+'list \t'+nombre_group+'/'+tag+'\n')
                except:
                    pass
            sqg_file.write('\n}\n')

    #inserta la lista blanca definida para el usuario
    sqg_file.write('dest white_'+user+' {\n')
    sqg_file.write('\t domainlist \t white_'+user+'/domains\n')
    sqg_file.write('\n}\n')
    
    sqg_file.write('\n #ACL DEFIITIONS\n')
    #inserta las acls en la seccion ACL DEFINITIONS

    sqg_file.write('acl {\n')
    sqg_file.write('\t default {\n')
    sqg_file.write('\t\t pass white_'+user)
    for list in xpath.Evaluate("/config/usuarios/"+user+"/web/denegado/*",xmldoc):
        sqg_file.write(' !'+str(list.attributes["tag"].value))   
    sqg_file.write('\n\t\t redirect '+PAGE_DFL+'\n\t}\n')
    
    sqg_file.write('}\n')
    
    sqg_file.close()
    
    orden='chown squid:admin '+SQGconf      
    os.system(orden) 
       
##Modulo examina si existen los directorios que se necesitan para el filtrado de contenido
##para cada usuario, si no existen se crean y se establecen los permisos adecuados
def inic_direct_user(user,file_log):
    """Crea estructura para filtrado de contenido para usuarios para ls que se ha configurado
    con permisos correspondientes"""
    import os, os.path
    xmldoc=parse_file(archivo.configuracion)
    
    SQconf=consulta_campo('conf_sq',file_log)
    SQdirlog=consulta_campo('logdir',file_log)
    SARGdir=consulta_campo('sargrg',file_log)
    DBhome=consulta_campo('dbhome',file_log)
    SQGdir=consulta_campo('dir_sqg',file_log)
 
    #comprobar si tiene su directorio de logs
    dlog=SQdirlog+user
    if not os.path.isdir(dlog):
        os.system('mkdir '+dlog)
        fwdlog=dlog+'/access.log'
        f=open(fwdlog,'w')
        f.close()
    #comprobar si tiene su lista blanca creada, con archivo de dominios
    wlist=DBhome+'/white_'+user
    if not os.path.isdir(wlist):
        os.system('mkdir '+wlist)
        fwlist=wlist+'/domains'
        f=open(fwlist,'w')
        f.close()
    #comprobar si tiene su directorio para sarg
    sgdir=SARGdir+'/'+user
    if not os.path.isdir(sgdir):
        os.system('mkdir '+sgdir)        
      
    permiso='chmod -R 770 '
    os.system(permiso+SQconf)
    os.system(permiso+DBhome)
    os.system(permiso+SARGdir)
    os.system(permiso+SQGdir)
    permiso='chown -R squid:admin '
    os.system(permiso+SQconf)
    os.system(permiso+DBhome)
    os.system(permiso+SARGdir)
    os.system(permiso+SQGdir)
    
    varlog='chown -R squid:admin /var/log/acept/'
    os.system(varlog)

##Modulo que refleja la configuracion de squidguard definida en el archivo de configuracion xml
##en los archivos de los usuarios involucrados    
def actualiza_sqg_conf(file_log):
    """Vierte configuracion de filtrado de contenido para usuarios recogida en archivo de configuracion
    en correspondientes archivos con los que trabajaran las instancias de squidguard"""
    from xml import xpath
    import os

    xmldoc=parse_file(archivo.configuracion)
    
    #directorio donde se encuentra instalado squid
    SQconf=consulta_campo('conf_sq',file_log)
    DBHOME=consulta_campo('dbhome',file_log)
    LOGDIR=consulta_campo('logdir',file_log)
    #extrae pag. muestra por defecto cuando acceso denegado a alguna url
    PAGE_DFL=consulta_campo('page_dfl',file_log)
    

    #archivo de config de squidguard para user
    SQGconf=SQconf+'squidGuard.conf'


    #abrir archivo squidguard.conf que vamos a sobreescribir
    sqg_file=open(SQGconf,'w')

    sqg_file.write('dbhome '+DBHOME+'\n')
    sqg_file.write('logdir '+LOGDIR+'\n')

    sqg_file.write('\n#DESTINATION CLASSES\n')
    #inserta los grupos en la seccion DESTINATION CLASSES

    groups=xmldoc.getElementsByTagName('group')
    for grp in groups:
        MLOG = open("/tmp/open","a")
        MLOG.write("Mirando el grupo %s\n" %grp)
        MLOG.close()
        nombre_group=str(grp.attributes["tag"].value)
        sqg_file.write('dest '+nombre_group+' {\n')
        for entry in grp.childNodes:
            if entry.localName:
                if entry.localName.find('entry')!=-1:
                    tag=entry.attributes["tag"].value
                    sqg_file.write('\t '+tag[:-1]+'list \t'+nombre_group+'/'+tag+'\n')
        sqg_file.write('\n}\n')
 
    sqg_file.write('\n #ACL DEFIITIONS\n')
    #inserta las acls en la seccion ACL DEFINITIONS

    sqg_file.write('acl {\n')
    sqg_file.write('\t default {\n')
    sqg_file.write('\t\t pass all')
    sqg_file.write('\n\t\t redirect '+PAGE_DFL+'\n\t}\n')
    
    sqg_file.write('}\n')
    
    sqg_file.close()
    
    orden='chown squid:admin '+SQGconf      
    os.system(orden) 
