# -*- coding: ISO-8859-1 -*-
#
# Fichero:	func_blacklists.py
# Copyright:	Junta de Andalucía <devmaster@guadalinex.org>
# Autor:	Maria Dolores Pérez Gutiérrez y Néstor Chacón Manzano
# Fecha:	lun mar 27 17:01:25 CET 2006
# Licencia:	GPL v.2
#
# Funciones auxiliares para la descarga y actualizacion de la BD de blacklists


from mefiGlobal import *
from func import copia_seguridad,escribe_log
import os,os.path

##MODULO PARA ESTANDARIZACION DEL LENGUAJE
def _(cadena):
    return cadena
    
    
##MODULOS PARA ELIMINACION DE DIRECTORIOS
def rmgeneric(path, __func__):
    try:
        __func__(path)
    except OSError, (errno, strerror):
        print ERROR_STR % {'path': path, 'error': strerror}
    
    
def removeall(path,flog):
    """Elimina el contenido del directorio especificado, si no se trata de un directorio no hace nada"""
    if not os.path.isdir(path):
        return
    
    files=os.listdir(path)
    for x in files:
        fullpath=os.path.join(path,x)
        if os.path.isfile(fullpath):
            f=os.remove
            rmgeneric(fullpath,f)   
        elif os.path.isdir(fullpath):
            removeall(fullpath,flog)
            f=os.rmdir
            rmgeneric(fullpath,f)
            
    
##Modulo comprueba si directorio especificado existe
##si existe lo borra con todo su contenido
##creal el directorio
def renuevadir(nombre, flog):
    """Se crea directorio especificado, borrandolo antes si existia"""
    if os.path.exists(nombre):
        removeall(nombre,flog)
        os.rmdir(nombre)
    os.mkdir(nombre)
    
##Modulo crea directorio si no existe 
def creadir(nombre, flog):
    """Se crea directorio si no existia"""
    if os.path.exists(nombre)!=1:
        os.mkdir(nombre,0750)
   

##Modulo consulta fecha de version de archivo existente en el sistema
##Si no encuentra entrada para archivo devuelve -1
##devuelve fecha de version existente
def consulta_fecha(archivo,Ddown):
    """Devuelve fecha de version de archivo segun archivo de control de versiones, -1 si no se 
    ha descargado"""
    #archivo registra version de fichero descargado
    f_version=Ddown+'/.versiones'
    if not os.path.isfile(f_version):
        return -1
    f=open(f_version)
    flines=f.readlines()
    for i in range(len(flines)):
        if flines[i].find(archivo)!=-1:
            m=flines[i].rfind('=')
            fecha=flines[i][m+1:]
            f.close()
            return fecha
    
    f.close()
    return -1
    
##Modulo descarga archivo url
##comprueba si url responde ,si el objeto es de tipo aplicacion y si no se dispone de version mas reciente
##en caso afirmativo se descarga
def descarga (url,nombre,temporal,destino,Ddown,flog):
    """Descarga archivo si la url responde, es de tipo aplicacion y no se dispone ya de la version
    mas reciente"""
    import urllib


    try:
        u=urllib.urlopen(url)
    except IOError:
        msj= 'Error al abrir url '+url
        escribe_log(msj,flog)
        return 'ERROR'


    block_size = 4096
    i = 0
    headers = u.info()
    try:
        size = int(headers['Content-Length'])
        data = open (temporal, 'wb')
    
        while i < size:
            data.write (u.read(block_size))
            i += block_size
    except:
        return "ERROR"

    data.close()
    u.close()
    #comprueba que la url responde, en caso contrario lo recoge en archivo de logs
    return nombre 
    
##Modulo que descomprime el archivo en directorio temporal 
##devuelve indice de cadena nombre en la que termina nombre de archivo 
##sin extension de compresion
def descomprime(nombre,DirTmp,archivo):
    """Descomprime archivo descargado segun el tipo de extension
    Se expera un archivo 'tar.gz' o '.gz'
    Si no se entiende el formato devuelve -1"""
    import commands,os
  
    out_cmd=''
    if nombre.find('.tar.gz')!=-1 or nombre.find('.tgz')!=-1 :
        orden='tar zxvf'+' '+archivo+ ' -C'+DirTmp
        out_cmd=commands.getoutput(orden)
        resul=out_cmd[:out_cmd.find('/')]
        if resul == ".":
            aux_cmd = out_cmd[out_cmd.find('/')+1:]
            resul = aux_cmd[:aux_cmd.find('/')]
    elif nombre.find('.gz')!=-1:
        n_archivo=nombre[:nombre.find('.gz')]
        dest_desc=DirTmp+'/'+n_archivo
        orden='gunzip -c '+archivo+' > '+dest_desc
        out_cmd=commands.getoutput(orden)
        resul=out_cmd[:out_cmd.find('/')]
    else: #si no cuenta con terminacion aclaratoria se intenta con tar zxvf
        narchivo=archivo+'.tar.gz'
        renombra='mv '+archivo+' '+ narchivo
        os.system(renombra)
        nombre=nombre+'.tar.gz'
        orden='tar zxvf'+' '+narchivo+ ' -C'+DirTmp
        out_cmd=commands.getoutput(orden)
        resul=out_cmd[:out_cmd.find('/')]
    return resul 
    
    
##Recibe nombre de grupo y una lista de grupos 
##Si alguno de los grupos de la lista tiene su valor de tag (etiqueta) 
##con el mismo nombre que el grupo proporcionado devuelve 1
##en caso contrario devuelve -1
def existe_grupo(nombre, grupos):
    """Comprueba si el nombre de grupo ya se encuentra entre la lista
    de grupos que se tiene"""
    for grupo in grupos:
        ngrupo=str(grupo.attributes["tag"].value)
        if nombre.find(ngrupo)!=-1 and ngrupo.find(nombre)!=-1:
            return 1
        
    return -1

##Funcion con la que se incluye un grupo que aun no se recogia en el archivo de configuracion  
##El grupo puede contener descripcion de: dominios, urls y/o expressiones
def append_grupo(grupo,descrip,f_obj,archivo,DBdest):
    """Se agrega grupo a archivo de configuracion, con las respectivas entradas
    que ese grupo engloba"""
    import os

    cad_domains='domains'
    cad_urls='urls'
    cad_expressions='expressions'
    #comprueba descripciones que incluye el grupo
    
    
    #elemento dentro del que se inserta el grupo
    bl=f_obj.getElementsByTagName('blacklists')[0]

    #tab=str(bl.firstChild.nodeValue)
    tab="\n\t"
    n=tab.rfind('\t')
    tab_padre=tab[:n]
    tab_hijo=tab+'\t'
    tab_hijo2=tab_hijo+'\t'

    ds=f_obj.createElement('descripcion')
    ds.appendChild(f_obj.createTextNode(tab_hijo2))
    ds.appendChild(f_obj.createTextNode(descrip))
    ds.appendChild(f_obj.createTextNode(tab_hijo))
    
    dm=f_obj.createElement('entry')
    dm.setAttribute('tag','domains')
    ur=f_obj.createElement('entry')
    ur.setAttribute('tag','urls')    
    ex=f_obj.createElement('entry')
    ex.setAttribute('tag','expressions')

    gr=f_obj.createElement('group')    
    gr.appendChild(f_obj.createTextNode(tab_hijo))
    gr.appendChild(ds)

    if os.path.isfile(DBdest+"/domains"):
        gr.appendChild(f_obj.createTextNode(tab_hijo))
        gr.appendChild(dm)

    if os.path.isfile(DBdest+"/urls"):
        gr.appendChild(f_obj.createTextNode(tab_hijo))
        gr.appendChild(ur)
    if os.path.isfile(DBdest+"/expressions"):
        gr.appendChild(f_obj.createTextNode(tab_hijo))
        gr.appendChild(ex)    
        
    gr.setAttribute('local','no')
    gr.setAttribute('tag',grupo)
    gr.appendChild(f_obj.createTextNode(tab))
  
    bl.insertBefore(f_obj.createTextNode(tab),bl.lastChild)
    bl.insertBefore(gr,bl.lastChild)
    
    correcto=False
    while not correcto:
        try:
            copia_seguridad()
            f=open(archivo,'w')
            f.write(f_obj.toxml())
            f.close()
            correcto=True
        except:
            correcto=False    

def revisa_grupo(grupo,descrip,f_obj,archivo,DBdest):
    """Se revisa grupo en archivo de configuracion, con las respectivas entradas
    que ese grupo engloba"""

    cad_domains='domains'
    cad_urls='urls'
    cad_expressions='expressions'
    nlista={'domains':0,'urls':0,'expressions':0}
    actual={'domains':0,'urls':0,'expressions':0}
   
    #comprueba descripciones que incluye el grupo
    for content in os.listdir(DBdest):
        if cad_domains.find(content)!=-1:
            nlista['domains']=1   
        if cad_urls.find(content)!=-1:
            nlista['urls']=1   
        if cad_expressions.find(content)!=-1:
            nlista['expressions']=1   
        
    #elemento dentro del que se inserta el grupo
    bl=f_obj.getElementsByTagName('blacklists')[0]

    #tab=str(bl.firstChild.nodeValue)
    tab="\n\t"
    tab_hijo=tab+'\t'
    for node in bl.childNodes:

        actual['domains']=0
        actual['urls']=0
        actual['expressions']=0

        if node.nodeName.find('group')!=-1:
            if node.attributes['tag'].value.find(grupo)!=-1:
                for hijo in node.childNodes:

                    if hijo.nodeName.find('entry')!=-1:
                        if cad_domains.find(hijo.attributes['tag'].value)!=-1:
                            actual['domains']=1		
                        if cad_urls.find(hijo.attributes['tag'].value)!=-1:
                            actual['urls']=1		
                        if cad_expressions.find(hijo.attributes['tag'].value)!=-1:
                            actual['expressions']=1		
    
    
                if nlista['domains']==1 and actual['domains']==0:
                    dm=f_obj.createElement('entry')
                    dm.setAttribute('tag','domains')
                    node.insertBefore(f_obj.createTextNode(tab_hijo),node.lastChild)
                    node.insertBefore(dm,node.lastChild)

                if nlista['urls']==1 and actual['urls']==0:
                    ur=f_obj.createElement('entry')
                    ur.setAttribute('tag','urls')
                    node.insertBefore(f_obj.createTextNode(tab_hijo),node.lastChild)
                    node.insertBefore(ur,node.lastChild)
    
                if nlista['expressions']==1 and actual['expressions']==0:
                    ex=f_obj.createElement('entry')
                    ex.setAttribute('tag','expressions')
                    node.insertBefore(f_obj.createTextNode(tab_hijo),node.lastChild)
                    node.insertBefore(ex,node.lastChild)
    

    correcto=False
    while not correcto:
        try:
            copia_seguridad()
            f=open(archivo,'w')
            f.write(f_obj.toxml())
            f.close()
            correcto=True
        except:
            correcto=False    
    
##Modulo archivos de grupo en destino: 
##discrimina solo copiando los archivos que no son parches a versiones anteriores (.diff)    
def copia_grupo(orig,DBdest):
    """Copia contenido de grupo descargado, sin incluir archivos de parches y similares"""
    import shutil, os
  
    os.mkdir(DBdest)
    for obj in os.listdir(orig):

        if obj.find('.diff')==-1:
            origen=os.path.join(orig,obj)
            destino=os.path.join(DBdest,obj)
            MLO = open("/tmp/milog2","a")
            MLO.write("orig: %s DBdest: %s obj: %s\n" %(orig,DBdest,obj))
            MLO.write("Copiando desde origen %s a destino %s\n" %(origen,destino))
            MLO.close()
            try:
                shutil.copy(origen,destino)
                orden='chmod 664 '+destino
                os.system(orden)
            except:
                pass



def actualiza_file(origen,destino):
    
    fr=open(destino,'r')
    lines=fr.readlines()
    fr.close()
    
    
    fnew=open(origen,'r')
    fold=open(destino,'a')
    
    for newline in fnew.readlines():
        include=True
        for line in lines:
            if newline.find(line)!=-1 and line.find(newline)!=-1:
                include=False
                break
        if include:
            fold.write(newline)	    	
    fnew.close()
    fold.close()

def actualiza_grupo(orig,DBdest):
    """Se actualiza contenido de grupo con el contenido nuevo, sin incluir archivos de parches y similares"""
    import shutil, os, os.path
    
    for obj in os.listdir(orig):
        if obj.find('.diff')==-1:
            origen=os.path.join(orig,obj)
            destino=os.path.join(DBdest,obj)
            try:
                orden='cat '+destino+' >> '+origen
                os.system(orden)
                orden='sort '+origen+' | uniq >'+destino 
                os.system(orden)
                #shutil.copy(origen,destino)
                orden='chmod 664 '+destino
                os.system(orden) 
            except:
                pass

##Modulo que inserta las blacklist descargadas de una url en el directorio
##temporal a la base de datos, a la vez que comprueba si los grupos que en
##ellas aparecen se recogen en la base de datos, si no es asi se incluyen en archivo
##de configuracion
def inserta_blacklists(fullpath,DBhome,nombre,xmldoc,flog,file_conf):
    """Inserta blacklists descargadas, incluyendo en archivo de configuracion
    grupos que no estuvieran considerados"""
    import shutil


    MLOG = open("/tmp/milog2","a")
    MLOG.write("#Inserta_blacklists\n")
    MLOG.write("Procedemos a limpiar Blacklists antiguas\n")
    MLOG.close()

    if os.path.isdir(fullpath): #listas descargadas contenidas en directorio
        if fullpath.count("blacklists") == 0:
           fullpath=fullpath
        files=os.listdir(fullpath)
        MLOG = open("/tmp/milog2","a")
        MLOG.write("#Listado Blacklist\n")
        MLOG.write("-%s\n" %files)
        MLOG.close()
        if os.path.isdir("/etc/acept/watcherCat/expresiones"):
            os.system("cp -r /etc/acept/watcherCat/expresiones "+fullpath)
            MLOG = open("/tmp/milog2","a")
            MLOG.write("Copiando expresiones regulares\n")
            MLOG.close()
        
        files=os.listdir(fullpath)
        for x in files:
            #print x
            DBdest=os.path.join(DBhome,x) #se compone destino
            orig=os.path.join(fullpath,x) #orig apunta a objeto a copiar
            if os.path.isdir(orig):  #directorio se copia completo y se comprueba si ya se tiene grupo
                if os.path.exists(DBdest):#si existia como directorio hay que eliminarlo
                    MLOG = open("/tmp/milog2","a")
                    MLOG.write("#Actualizo grupo\n")
                    MLOG.write("Con Origen %s a Destino %s\n" %(orig,DBdest))
                    MLOG.close()
                    actualiza_grupo(orig,DBdest)

                else:
                    MLOG = open("/tmp/milog2","a")
                    MLOG.write("#Copio grupo\n")
                    MLOG.close()
                    #en lugar de copiar todo, solo copiar archivos principales
                    copia_grupo(orig,DBdest)

                #se comprueba si ya se tiene incluido grupo en arch de configuracion
                grupos=xmldoc.getElementsByTagName('group')
                if existe_grupo(x,grupos)==-1 :# no existe hay que incluirlo
                    append_grupo(x,'',xmldoc,file_conf, DBdest)
                    MLOG = open("/tmp/milog2","a")
                    MLOG.write("#Agrego Grupo\n")
                    MLOG.close()
                else:
                    revisa_grupo(x,'',xmldoc,file_conf,DBdest) 
                    MLOG = open("/tmp/milog2","a")
                    MLOG.write("#Reviso Grupo\n")
                    MLOG.close()
            
            elif os.path.isfile(orig):#si es un archivo se copia salvo q se trate del README
                if x.find('README')!=-1:
                    continue
                shutil.copyfile(orig,DBdest)
            
    elif os.path.isfile(fullpath):
        DBdest=os.path.join(DBhome,nombre)
        shutil.copyfile(fullpath,DBdest)
    else:
        pass 

def revisa_blacklists(file_conf):
    from func import parse_file

    xmldoc=parse_file(file_conf)
 
    bl=xmldoc.getElementsByTagName('blacklists')[0]
    #tab=str(bl.firstChild.nodeValue)
    tab="\n\t"
    node=bl.firstChild
    for i in range(len(bl.childNodes)):
	if node.nextSibling==None:
            bl.removeChild(node)
	    bl.appendChild(xmldoc.createTextNode(tab))
            break
        node=node.nextSibling


    correcto=False
    while not correcto:
        try:
            copia_seguridad()
            f=open(file_conf,'w')
            f.write(xmldoc.toxml())
            f.close()
            correcto=True
        except:
            correcto=False	

