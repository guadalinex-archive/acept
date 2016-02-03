# -*- coding: ISO-8859-1 -*-
#
# Fichero:	confSquid.py
# Copyright:	Junta de Andalucía <devmaster@guadalinex.org>
# Autor:	Maria Dolores Pérez Gutiérrez y Néstor Chacón Manzano
# Fecha:	lun mar 27 17:01:23 CET 2006
# Licencia:	GPL v.2
#
# Funciones auxiliares para establecemiento de la configuracion de squid para
# distintos usuarios 

###Archivo contiene modulos aplican configuracion para filtrado de contenido
###seleccionada a traves del asistente o de la aplicacion avanzada
import wx
from informes import *
from func import *
_=wx.GetTranslation
##Modulo devuelve listas de blacklists que se asocian a un grupo de contenidos
##La correspondencia se establece en archivo de texto
def cadenas_grupo(grupo, file_corresp):
    """Devuelve listas de blacklists asociadas al grupo de contenidos en el archivo que establece
    las correspondencias"""
    f=open(file_corresp,'r')
    lines=f.readlines()
    f.close()
    for l in lines:
        if l.find(grupo)!=-1:
            return l[l.find(':')+2:l.find('\n')].split(' ')
    
    

##Modulo devuelve grupo de contenido al que se asocia la blacklist especificada
##La correspondencia se establece en archivo de texto
def grupo_cadena(cadena,file_corresp):
    """Devuelve el grupo de contenidos al que pertenece la lista de blacklists indicada, segun establece 
    el archivo de correspondencias"""
    f=open(file_corresp,'r')
    lines=f.readlines()
    f.close()
    
    for l in lines:
        if l.find(cadena)!=-1:
            return l[:l.find(':')]
        


##Modulo vuelca en archivo de configuracion control web establecido para el usuario
##Es invocado por asistente de configuracion 
def inic_control_web(user,denegado,file_conf):
    """Modifica archivo de configuracion con las politicas de control web
    establecidas para el usuario. Recibe el usuario y una cadena con los 
    contenidos que le van a ser bloqueados"""
    from xml import xpath
 
    xmldoc=parse_file(file_conf)
    
    if xmldoc==-1:
	mje="Error lectura previa volcado configuracion web usuario "+user
	escribe_log(mje,archivo.aceptlog)
	return

    #puerto de squid
    port=xpath.Evaluate('/config/squid/port',xmldoc)[0].firstChild.data
    
    #usuario que modificamos
    usuarios=xmldoc.getElementsByTagName('usuarios')[0]
    for usuario in usuarios.childNodes:
	if usuario.nodeName.find(user)!=-1 and user.find(usuario.nodeName)!=-1:
	    break
    
    #si no existe entrada web la creamos con correspondiente campo activo
    if xpath.Evaluate('/config/usuarios/'+user+'/web',xmldoc)==[]:
        #obtenemos tabulaciones del padre
        tab=str(usuario.firstChild.nodeValue)
        n=tab.rfind('\t')
        tab_padre=tab[:n]
        tab_hijo=tab+'\t'
        
        web=xmldoc.createElement('web')
        activo=xmldoc.createElement('activo')
        activo.appendChild(xmldoc.createTextNode('1'))
        web.appendChild(xmldoc.createTextNode(tab_hijo))
        web.appendChild(activo)
        web.appendChild(xmldoc.createTextNode(tab))
        usuario.appendChild(xmldoc.createTextNode(tab))
        usuario.appendChild(web)
        usuario.appendChild(xmldoc.createTextNode(tab_padre))
    else: #si existe en archivo entrada web para este usuario  
        for node in usuario.childNodes:
            if node.nodeName.find('web')!=-1:
                web=node
                break
        
    tab=str(web.firstChild.nodeValue)
    tab_hijo=tab+'\t'
    
    port_sq=xmldoc.createElement('squid_pt')
    port_sq.appendChild(xmldoc.createTextNode(port))
    web.insertBefore(xmldoc.createTextNode(tab),web.lastChild)
    web.insertBefore(port_sq,web.lastChild)
    i_port=int(port)
    n_port=str(i_port+1)
    xpath.Evaluate('/config/squid/port',xmldoc)[0].childNodes[0].data=n_port
                
    deny=xmldoc.createElement('denegado')
    #pr=xmldoc.createElement('lista')
    #pr.setAttribute('tag','proxy')
    deny.appendChild(xmldoc.createTextNode(tab_hijo))
    #deny.appendChild(pr)
    
    entrys=denegado.split(',')
    for ent in entrys:
        if len(ent)>0: 
            cads=cadenas_grupo(ent.strip(),'/etc/acept/watcherCat/asocia_contenidos')
            for cad in cads:
                nw=xmldoc.createElement('lista')
                nw.setAttribute('tag',cad)
                deny.appendChild(xmldoc.createTextNode(tab_hijo))
                deny.appendChild(nw)

    deny.appendChild(xmldoc.createTextNode(tab))
    web.insertBefore(xmldoc.createTextNode(tab),web.lastChild)
    web.insertBefore(deny,web.lastChild)
   
    mje='Se escribe configuracion web para usuario '+user
    escribe_log(mje,archivo.aceptlog) 
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
    

##Modulo devuelve listado de blacklists locales 
##creadas por el administrador en el sistema
def local_blacklists(file_conf):
    """Devuelve listado de nombres de  blacklists creadas localmente"""
    xmldoc=parse_file(file_conf)
   
    if xmldoc==-1:
	escribe_log("Error lectura blacklists locales",archivo.aceptlog)
	return []
 
    groups=xmldoc.getElementsByTagName('group')
    local=[]
    
    for group in groups:
        if group.attributes['local'].value.find('yes')!=-1:
            local.append(str(group.attributes['tag'].value))
        
    return local

    

##Modulo inserta entrada para blacklist en archivo de configuracion
##la blacklist se etiqueta como blacklist local
def inserta_grupo(nombre, file_conf):
    """Inserta lista de blacklist local en archivo de configuracion"""
    xmldoc=parse_file(file_conf)
 
    if xmldoc==-1:
	mje="Error lectura previa a insercion blacklist local "+nombre
	escribe_log(mje,archivo.aceptlog)
	return
   
    bl=xmldoc.getElementsByTagName('blacklists')[0]

    #tab=str(bl.firstChild.nodeValue)
    tab="\n\t"
    tab_hijo=tab+'\t'

    dm=xmldoc.createElement('entry')
    dm.setAttribute('tag','domains')
        
    gr=xmldoc.createElement('group')    
    gr.appendChild(xmldoc.createTextNode(tab_hijo))
    gr.appendChild(dm)
    gr.setAttribute('local','yes')
    gr.setAttribute('tag',nombre)
    gr.appendChild(xmldoc.createTextNode(tab))
    bl.insertBefore(xmldoc.createTextNode(tab), bl.lastChild)
    bl.insertBefore(gr, bl.lastChild)

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

    
##Modulo crea, actualiza  blacklist especificada con lista de dominios indicados
##tanto en archivo de configuracion como en base de datos de squidguard
def inserta_blacklist(nombre, lista_dominios,file_conf):
    """Crea o sobreescribe la blacklist especificada en el sistema con el contenido que se indica,
    modifica archivo de configuracion y base de datos de blacklists para incluirla"""
    import os, os.path
    from func_blacklists import existe_grupo
 
    xmldoc=parse_file(file_conf)
   
    if xmldoc==-1:
	mje="Error lectura previa a creacion blacklis local "+nombre
	escribe_log(mje,archivo.aceptlog)
	return 	 

    DBhome=consulta_campo('dbhome',archivo.aceptlog)
    
    grupos=xmldoc.getElementsByTagName('group')
    if existe_grupo(nombre,grupos)==-1 :# no existe hay que incluirlo
        inserta_grupo(nombre,file_conf)
        
    dir_blacklist=DBhome+'/'+nombre
    
    if not os.path.isdir(dir_blacklist):
        os.mkdir(dir_blacklist)
    
    file_blacklist=dir_blacklist+'/domains'
    f=open(file_blacklist,'w')
    
    for domain in lista_dominios:
        f.write(domain+'\n')
    
    f.close()
    

##Modulo devuelve listado de dominios que integran la blacklist especificada
def lee_blacklist(nombre,file_conf):
    """Lee lista de dominios que se incluyen en la blacklist especificada"""
    import os.path
    
    xmldoc=parse_file(file_conf)
   
    if xmldoc==-1:
	mje="Error lectura contenido blacklist local "+nombre
	escribe_log(mje,archivo.aceptlog)
	return []

    DBhome=consulta_campo('dbhome',archivo.aceptlog)
    
    file_blacklist=DBhome+'/'+nombre+'/domains'
    if not os.path.isfile(file_blacklist):
        lista_dominios=[]
    else:
        f=open(file_blacklist,'r')
        lines=f.readlines()
        f.close()
        lista_dominios=[]
        for line in lines:
            if line.find('#')==-1:
                lista_dominios.append(line[:line.find('\n')])
        
    return lista_dominios

    
##Modulo elimina blacklist local del sistema, del archivo de configuracion
##y de la base de datos de squidguard
def elimina_blacklist(nombre,file_conf):
    """Elimina la blacklist especificada, elimina la entrada correspondiente en 
    el archivo de configuracion y el directorio que tenia en la base de datos de
    blacklists"""
    from func_blacklists import removeall
    import os, os.path
    
    xmldoc=parse_file(file_conf)
 
    if xmldoc==-1:
	mje="Error en eliminacion de blacklist local "+nombre
	escribe_log(mje,archivo.aceptlog)
	return    

    DBhome=consulta_campo('dbhome',archivo.aceptlog)
    
    #elimina directorio correspondiente a esta blacklist en base de datos de squidguard
    dir_blacklist=DBhome+'/'+nombre
    if os.path.isdir(dir_blacklist):
        removeall(dir_blacklist,'')
        os.rmdir(dir_blacklist)
    
    #elimina entrada de esta blacklist en archivo de configuracion de acept  
    bl=xmldoc.getElementsByTagName('blacklists')[0]
    node=bl.firstChild
    for i in range(len(bl.childNodes)):
        if node.nodeName.find('group')!=-1 and node.attributes['tag'].value.find(nombre)!=-1:
            bl.removeChild(node)
            #if node.previousSibling!=None:
            #    bl.removeChild(node.previousSibling)
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
    

##Modulo extrae listado de fuentes actualmente configurado
##del que se extraen las blacklists con las que el sistema trabaja
def lee_fuentes(file_conf):
    """Extrae listado de fuentes de blacklist del sistema"""
    xmldoc=parse_file(file_conf)

    if xmldoc==-1:
	escribe_log("Error lectura listado fuentes de blacklists",archivo.aceptlog)
    	return []

    sources=xmldoc.getElementsByTagName('source')
    fuentes=[]
    for source in sources:
        for node in source.childNodes:
            if node.nodeName.find('url')!=-1:
                fuentes.append(str(node.firstChild.data))
                
    return fuentes
        
        

##Modulo modifica listado de fuentes del sistema 
##y frecuencia de actualizacion de las mismas en archivo de configuracion
def actualiza_fuentes(lista_fuentes, frecuencia, file_conf):
    """Escribe listado de fuentes especificado en archivo de configuracion"""
    #modifica frecuencia de actualizacion de blacklists
    actualiza_campo('fr_update',frecuencia, archivo.aceptlog)
    
    xmldoc=parse_file(file_conf)

    if xmldoc==-1:
	escribe_log("Error lectura previa a actualizacion fuentes de blacklists",archivo.aceptlog)
	return

    bl=xmldoc.getElementsByTagName('blacklists')[0]
        
    #registramos valores de tabuladores a emplear
    #tab=str(bl.firstChild.nodeValue)
    tab="\n\t"
    n=tab.rfind('\t')
    tab_hijo=tab+'\t'
    
    #eliminamos todos los hijos de blacklists que preceden a los grupos de blacklists
    node=bl.firstChild
    for i in range(len(bl.childNodes)):
        if node.nextSibling!=None:
            if node.nodeName.find('group')!=-1 or node.nextSibling.nodeName.find('group')!=-1:
                break
            sig_node=node.nextSibling
            bl.removeChild(node)
            node=sig_node
        else:
            break
    
    #incluye cada una de las fuentes antes de los grupos de blacklists que puedan existir
    for fuente in lista_fuentes:
        source=xmldoc.createElement('source')
        source.setAttribute('tag','nueva_fuente')
        url=xmldoc.createElement('url')  
        url.appendChild(xmldoc.createTextNode(fuente))
        source.appendChild(xmldoc.createTextNode(tab_hijo))
        source.appendChild(url)
        source.appendChild(xmldoc.createTextNode(tab))
        bl.insertBefore(xmldoc.createTextNode(tab),node)
        bl.insertBefore(source,node)
    
    #escribe cambios realizados a archivo de configuracion
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

    

##Modulo devuelve listado de blacklists (locales y bajadas desde las fuentes)
##que actualmente existen en el sistema
def listado_blacklists(file_conf):
    """Extrae listado de blacklists de sistema"""
    xmldoc=parse_file(file_conf)
        
    if xmldoc==-1:
	escribe_log("Error lectura listado completo blacklists",archivo.aceptlog)
	return []

    groups=xmldoc.getElementsByTagName('group')
    listado=[]
    for group in groups:
        listado.append(str(group.attributes['tag'].value))
    
    return listado
    


##Modulo devuelve lista blacklists a las que no tiene acceso el usuario
def lee_userblacklists(user,file_conf):
    """Extrae lista de blacklists a las que el usuario no puede acceder"""
    from xml import xpath
     
    if control_web_user(user,archivo.aceptlog)==1:
        blacklists=[]
        xmldoc=parse_file(file_conf)

    	if xmldoc==-1:
		mje="Error lectura blacklists de usuario "+user
		escribe_log(mje,archivo.aceptlog)
		return blacklists
	
	groups=xmldoc.getElementsByTagName('group')
	grupos=[]
	for grp in groups:
		grupos.append(str(grp.attributes["tag"].value))

        for list in xpath.Evaluate("/config/usuarios/"+user+"/web/denegado/*",xmldoc):
	    cad_list=str(list.attributes["tag"].value)
	    try:
		indl=grupos.index(cad_list)
	    except ValueError:
		pass
	    else:
            	blacklists.append(str(list.attributes["tag"].value))
    else:
        blacklists=[]
        
    return blacklists
    
    
 
##Modulo vuelca en archivo de configuracion control web establecido para el usuario
##Es invocado por  configurador avanzado de la aplicacion 
##Si recibe lista vacia mantiene o modifica nodo web eliminado parte corresp
def actualiza_userblacklists(user,blacklists,file_conf):
    """Modifica archivo de configuracion con las politicas de control web
    establecidas para el usuario. Recibe el usuario y una cadena con las 
    blacklists que le van a ser bloqueadas"""
    from xml import xpath

    xmldoc=parse_file(file_conf)

    if xmldoc==-1:
	mje="Error lectura previa a actualizacion blacklists usuario "+user
	escribe_log(mje,archivo.aceptlog)
	return    

    #puerto de squid
    port=xpath.Evaluate('/config/squid/port',xmldoc)[0].firstChild.data
    
    #usuario que modificamos
    usuarios=xmldoc.getElementsByTagName('usuarios')[0]
    for usuario in usuarios.childNodes:
	if usuario.nodeName.find(user)!=-1 and user.find(usuario.nodeName)!=-1:
		break

    #si no existe entrada web la creamos con correspondiente campo activo
    
    if blacklists!=[]:
        if xpath.Evaluate('/config/usuarios/'+user+'/web',xmldoc)==[]:
            #obtenemos tabulaciones del padre
            tab=str(usuario.firstChild.nodeValue)
            n=tab.rfind('\t')
            tab_padre=tab[:n]
            tab_hijo=tab+'\t'
        
            web=xmldoc.createElement('web')
            activo=xmldoc.createElement('activo')
            activo.appendChild(xmldoc.createTextNode('1'))
            web.appendChild(xmldoc.createTextNode(tab_hijo))
            web.appendChild(activo)
            web.appendChild(xmldoc.createTextNode(tab))
            usuario.appendChild(xmldoc.createTextNode(tab))
            usuario.appendChild(web)
            usuario.appendChild(xmldoc.createTextNode(tab_padre))
        else: #si existe en archivo entrada web para este usuario  
            for node in usuario.childNodes:
                if node.nodeName.find('web')!=-1:
                    web=node
                    break
        
        tab=str(web.firstChild.nodeValue)
        tab_hijo=tab+'\t'
    
        if xpath.Evaluate('/config/usuarios/'+user+'/web/denegado',xmldoc)==[]:
            port_sq=xmldoc.createElement('squid_pt')
            port_sq.appendChild(xmldoc.createTextNode(port))
            web.insertBefore(xmldoc.createTextNode(tab),web.lastChild)
            web.insertBefore(port_sq,web.lastChild)
            i_port=int(port)
            n_port=str(i_port+1)
            xpath.Evaluate('/config/squid/port',xmldoc)[0].childNodes[0].data=n_port
            web.insertBefore(xmldoc.createTextNode(tab),web.lastChild)
       
        else:
            for child in web.childNodes:
                if child.nodeName.find('denegado')!=-1:
                    web.removeChild(child)
                    break
    
        deny=xmldoc.createElement('denegado')    
    
        for list in blacklists:
            nw=xmldoc.createElement('lista')
            nw.setAttribute('tag',list)
            deny.appendChild(xmldoc.createTextNode(tab_hijo))
            deny.appendChild(nw)
    
        deny.appendChild(xmldoc.createTextNode(tab))
        web.insertBefore(deny,web.lastChild)
    
    else: # si existia entrada web con respectivos denegado y squid_pt se eliminan
        if xpath.Evaluate('/config/usuarios/'+user+'/web',xmldoc)!=[]:
            if xpath.Evaluate('/config/usuarios/'+user+'/web/denegado',xmldoc)!=[]:
                web=xpath.Evaluate('/config/usuarios/'+user+'/web',xmldoc)[0]
                for child in web.childNodes:
                    if child.nodeName.find('squid_pt')!=-1 or child.nodeName.find('denegado')!=-1:
                        web.removeChild(child)
                
                web.removeChild(web.lastChild.previousSibling)
                web.removeChild(web.lastChild.previousSibling)
                
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
  
##Modulo actualiza configuracion de filtrado de usuarios segun blacklists existentes
## en archivo de configuracion
def actualiza_filtrado_usuarios(file_conf):
    usuarios=users_control_web(file_conf)
    for user in usuarios:
        listas=lee_userblacklists(user,file_conf)
        actualiza_userblacklists(user,listas,file_conf)



##Modulo extrae lista de dominios/urls a los que se permite el acceso 
##del usuario incondicionalmente
def lee_whitelist(user, file_conf):
    """Extrae lista de dominios que forman la lista blanca para el usuario"""
    import os.path
    
    xmldoc=parse_file(file_conf)
   
    if xmldoc==-1:	
	mje="Error lectura whitelist de usuario "+user
	escribe_log(mje,archivo.aceptlog)
	return []

    DBhome=consulta_campo('dbhome',archivo.aceptlog)
    
    file_white=DBhome+'/white_'+user+'/domains'
    
    if not os.path.isfile(file_white):
        whitelist=[]
    else:
        f=open(file_white,'r')
        lines=f.readlines()
        f.close()
    
        whitelist=[]
        for line in lines:
            if line.find('#')==-1:
                whitelist.append(line[:line.find('\n')])
        
    return whitelist
    

##Modulo reescribe lista blanca para el usuario
##con la lista de dominios que se le indica
##Si no existe estructura correspondiente la crea
def actualiza_whitelist(user,whitelist,file_conf):
    """Escribe la lista blanca de dominios del usuario con lista que recibe"""
    import os, os.path
    
    xmldoc=parse_file(file_conf)

    if xmldoc==-1:
	mje="Error lectura previa a actualizacion whitelist de usuario "+user
	escribe_log(mje,archivo.aceptlog)    
	return

    DBhome=consulta_campo('dbhome',archivo.aceptlog)
    whitedir=DBhome+'/white_'+user
    
    if not os.path.isdir(whitedir):
        os.mkdir(whitedir)
    
    file_white=DBhome+'/white_'+user+'/domains'
    
    f=open(file_white,'w')
    for list in whitelist:
        f.write(list+'\n')
    
    f.close()
    orden='chmod -R 770 '+whitedir
    os.system(orden)
    orden='chown -R squid:admin '+whitedir
    os.system(orden)


###MODULOS PARA CONFIGURADOR DE REGISTROS DE NAVEGACION

##Modulo extrae lista de periodos de tiempo para los que se dispone
##de registros de navegacion almacenados
def extrae_periodos(file_conf):
    """Extrae lista de periodos para los que se dispone de registros de navegacion"""
    import time
    import os, os.path
    
    usuarios=users_control_web(archivo.aceptlog)
    if usuarios==[]:
	return []

    periodos=[]
    Varhome=consulta_campo('sargrg',archivo.aceptlog)
    
    for user in usuarios:
        user_path=Varhome+'/'+user
        if not os.path.isdir(user_path):
		os.mkdir(user_path)
	else:
		list=os.listdir(user_path)
        	for item in list:
        	    fpath=os.path.join(user_path,item)
        	    if os.path.isdir(fpath) and item.find('images')==-1:
        	        try:
        	            n=periodos.index(item)
        	        except ValueError:
        	            periodos.append(item)
                
    last_date=consulta_campo('last_date',archivo.aceptlog)
    date=time.localtime()
    act_date=time.strftime("%d%b%Y",date)
    if act_date.find(last_date)==-1:
        name_reg=last_date.capitalize()+'-'+act_date.capitalize()
        periodos.append(name_reg)

    return periodos
    

##Modulo extrae lista de periodos de tiempo para los que se dispone
##de registros de navegacion almacenados para el usuario especificado
def extrae_periodos_user(user, file_conf):
    """Extrae lista de periodos para los que se dispone de registros de navegacion
    para el usuario"""
    import time
    import os, os.path
    
    periodos=[]
    Varhome=consulta_campo('sargrg',archivo.aceptlog)
    if Varhome=='':
	return []

    
    user_path=Varhome+'/'+user
    if not os.path.isdir(user_path):
	os.mkdir(user_path)
    else:
    	list=os.listdir(user_path)
    	for item in list:
    	    fpath=os.path.join(user_path,item)
    	    if os.path.isdir(fpath) and item.find('images')==-1:
    	        periodos.append(item)
                
    last_date=consulta_campo('last_date',archivo.aceptlog)
    date=time.localtime()
    act_date=time.strftime("%d%b%Y",date)
    if act_date.find(last_date)==-1:
        name_reg=last_date.capitalize()+'-'+act_date.capitalize()
        periodos.append(name_reg)
    
    return periodos
    


##Devuelve contenido de fichero en forma de lista de cadenas
##Para extraer resultados que se han volcado en archivo de texto
def lee_fichero(file):
    """Devuelve contenido de fichero como lista de cadenas"""
    f=open(file,'r')
    
    salida=[]
    lines=f.readlines()
    for line in lines:
        salida.append(line[:line.find('\n')])
    
    return salida
    

##Modulo obtiene informacion de navegacion web solicitada 
##para usuario (si procede) y periodo indicado 
def mostrar_reg_nav(opcion,usuario,periodo,file_conf,clave):    
    """Devuelve informacion solicitada en periodo, para usuario"""
    import time, os.path
    
    Varhome=consulta_campo('sargrg',archivo.aceptlog)
    SQdirlog='/var/log/acept/squid/'

    if Varhome=='':
        return []
    

    Rghome=SQdirlog+'var/rg'

    date=time.localtime()
    act_date=time.strftime("%d%b%Y",date)

    if usuario.find('Todos')!=-1:
        usuario=' '
        
    if periodo.find(act_date.capitalize())!=-1:
        genera_registros_nuevos(file_conf)
    
    lee=True
    
    if opcion=='A':#num. pags. visitadas por usuario
        file=Rghome+'/'+periodo+'_npg'
        if not os.path.isfile(file):
            cuenta_pg_users(Varhome,periodo,Rghome,file_conf)
    elif opcion=='B':#trafico por usuario
        file=Rghome+'/'+periodo+'_trafic'
        if not os.path.isfile(file):
            trafico_usuario(Varhome,periodo,Rghome,file_conf)
            
    elif opcion=='C':#pags. visitadas ordenadas por usuario
        file=Rghome+'/'+periodo+'_pguser'
        if not os.path.isfile(file):
            pag_usuario(Varhome,periodo,Rghome,file_conf)
            
    elif opcion=='D':#pags. visitadas ordenadas por url
        if usuario.isspace():
            file=Rghome+'/'+periodo+'_pgurl'
        else:
            file=Rghome+'/'+periodo+'_pgurl_'+usuario
        
        if not os.path.isfile(file):
            pag_url(Varhome,periodo,Rghome,usuario,file_conf)
            
    elif opcion=='E':#pags. visitadas ordenadas cronologicamente
        if usuario.isspace():
            file=Rghome+'/'+periodo+'_pgcron'
        else:
            file=Rghome+'/'+periodo+'_pgcron_'+usuario
        
        if not os.path.isfile(file):
            pag_cron(Varhome,periodo,Rghome,usuario,file_conf)
        
    elif opcion=='F':#pags. visitadas ordenadas visitas
        if usuario.isspace():
            file=Rghome+'/'+periodo+'_pgnvisit'
        else:
            file=Rghome+'/'+periodo+'_pgnvisit_'+usuario
        
        if not os.path.isfile(file):
            pag_nvisit(Varhome,periodo,Rghome,usuario,file_conf)
        
    elif opcion=='G':#pags. visitadas ordenadas trafico
        if usuario.isspace():
            file=Rghome+'/'+periodo+'_pgtrafic'
        else:
            file=Rghome+'/'+periodo+'_pgtrafic_'+usuario
        
        if not os.path.isfile(file):
            pag_trafic(Varhome,periodo,Rghome,usuario,file_conf)
    elif opcion=='H':
        salida=pag_clave(Varhome,periodo,usuario,file_conf,clave)
        lee=False
    
    if lee:
        salida=lee_fichero(file)
    
    return salida
   
##Modulo extrae listado de periodos (de meses, o semanas, segun indique tipo) 
##de los que se tiene informacion del uso de aplicaciones
def extrae_periodos_uso_aplic(tipo):
    """Devuelve listado de periodos de los que se tiene informacion (mensuales [tipo=m] 
    o semanales [tipo=s]) del uso de aplicaciones"""
    import os, os.path
    
    directorio='/usr/share/acept/estadisticas'
    periodos=[]
    for entry in os.listdir(directorio):
        objeto=os.path.join(directorio, entry)
        if os.path.isfile(objeto):
            if entry.find('aplic_'+tipo)!=-1:
                periodo=entry[entry.find(tipo)+1:entry.find('.')]
                periodo=extiende_periodo(tipo,periodo)
                periodos.append(periodo)
    return periodos
        

##Modulo obtiene informacion del uso de aplicaciones solicitado
##a traves del entorno grafico
def mostrar_uso_aplicaciones(opcion, usuario, tipo, periodo,file_conf):
    """Devuelve informacion de uso de las aplicaciones solicitado"""

    if tipo=='m':
        periodo=periodo[:6]
    periodo=tipo+str(periodo)
   
    if opcion=='A': # muestra aplicaciones usadas por tiempo de uso
        salida=aplic_tmp_uso(usuario, periodo, file_conf)
    elif opcion=='B':#muestra aplicaciones usadas por usuario
        salida=aplic_usuario(periodo, file_conf)
    else: #muestra aplicaciones usadas por usuario y tiempo gastado
	salida=aplic_usuario_tmp(periodo, file_conf)
	
    return salida
