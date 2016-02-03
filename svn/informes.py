# -*- coding: ISO-8859-1 -*-
#
# Fichero:	informes.py
# Copyright:	Junta de Andalucía <devmaster@guadalinex.org>
# Autor:	Maria Dolores Pérez Gutiérrez y Néstor Chacón Manzano
# Fecha:	lun mar 27 17:01:28 CET 2006
# Licencia:	GPL v.2
#
# Archivo recoge funciones empleadas para la consulta de estadisticas de uso web y
# de aplicaciones, sera llamadas desde aplicacion grafica

from func import *
from func_navegacion import *


##Modulo comprueba si existen en el sistema registros de navegacion en el periodo
##indicado para el usuario especificado
def existe_registro(usuario,periodo,file_conf):
    """Verifica si existe el directorio que almacena registros de navegacion del usuario en
    el periodo indicado'"""
    import os.path
    
    Varhome=consulta_campo('sargrg',archivo.aceptlog)
    registro=Varhome+'/'+usuario+'/'+periodo
    
    if os.path.isdir(registro):
        return True
    else:
        return False

##Modulo devuelve lista de usuarios con politicas de control web definidas que cuentan
##con registros de navegacion para el periodo especificado
def users_con_registro(periodo, file_conf):
    """Devuelve listado de usuarios cuentan con registros de navegacion en ese periodo"""
    usuarios=users_control_web(archivo.aceptlog)
    
    r_users=[]
    for user in usuarios:
        if existe_registro(user,periodo,file_conf):
            r_users.append(user)
    
    return r_users

#FUNCIONES QUE APARECEN A CONTINUACION EXTRAEN INFORMACION DE ARCHIVO RESUMEN
#DE ACCESOS DE UN USUARIO EN UN PERIODO QUE GENERA SARG
#ARCHIVO SE ENCUENTRA EN /var/www/squid-reports/$USER/$PERIODO/sites
#RECOGE UNA ENTRADA POR CADA PAGINA DISTINTA ACCEDIDA 
#formato del archivo: Num_visitas Trafico_bytes [Tiempo_acceso]* Url
#[Tiempo_acceso] para archivos generados con version de sarg 2.0 o superior
     
##Modulo obtiene el numero de paginas distintas visitadas por un usuario concreto
def cuenta_pg_user(file):
    """Devuelve el numero de entradas distintas que aparecen en el archivo especificado"""
    d_file=urllib.urlopen(file)
    
    n_pg=len(d_file.readlines())

    d_file.close()

    return n_pg
    
##Modulo obtiene el numero de paginas visitadas por los usuarios con
##politicas de control web definidas
##el resultado es volcado en un archivo de texto plano con formato:
## nombre_usuario num_paginas_visito
def cuenta_pg_users(Varhome,periodo,Rghome,file_conf):
    """Escribe en fichero, numero de paginas visitadas por usuarios en periodo indicado"""
    rcpu=Rghome+'/'+periodo+'_npg'
    r_file=open(rcpu,'w')
    
    usuarios=users_con_registro(periodo,file_conf)
    
    r_file.write('USUARIO NUM_PAGS_VISITADAS \n\n')
    for user in usuarios:
        file=Varhome+'/'+user+'/'+periodo+'/sites'
        num_pg=cuenta_pg_user(file)
        r_file.write(user+'  \t'+str(num_pg)+'\n')
    
    r_file.close()
    
    
##Modulo obtiene el trafico web que ha registrado cada usuario
##con politicas de acceso web definidas
##vuelca resultado en archivo de texto plano con formato
##nombre_usuario cantidad_bytes_transferidos %trafico_web_registrado
def trafico_usuario(Varhome,periodo,Rghome,file_conf):
    """Escribe en fichero trafico web registrado por usuarios con control web"""
    rtrafic=Rghome+'/'+periodo+'_trafic'
    r_trf=open(rtrafic,'w')
    usuarios=users_con_registro(periodo,file_conf)
    
    total_bytes=0
    bytes_user=[]
    
    for usuario in usuarios:
        file=Varhome+'/'+usuario+'/'+periodo+'/sites' 
        d_file=urllib.urlopen(file)
        b_user=0
        for line in d_file.readlines():
            datos=line[:line.find('\n')].split(' ')
            b_user=b_user+long(datos[1])
        bytes_user.append(b_user)
        total_bytes=total_bytes+b_user
        d_file.close()
        
        
    r_trf.write('USUARIO   TOTAL_BYTES     %TRAFICO\n\n')
     
    for i in range(len(usuarios)):
        if int(total_bytes) > 0:
            porcentaje=(float(bytes_user[i])/float(total_bytes))*100.0
            porcen=normaliza_cad(str(porcentaje))
        else:
            porcen='0.00'
        r_trf.write(usuarios[i]+'   \t'+str(bytes_user[i])+'    \t'+porcen+'%\n')
    
    r_trf.close()
    
    
##Modulo obtiene paginas visitadas ordenadas por usuario accedio
##el resultado es volcado en archivo de texto plano con formato
##  url usuario1 (usuario2) ...
def pag_usuario(Varhome,periodo,Rghome,file_conf):
    """Vuelca en archivo las paginas visitadas en el sistema por los usuarios con control
    web, ordenadas por los usuarios que accedieron a ellas"""

    rpu=Rghome+'/'+periodo+'_pguser'
    r_file=open(rpu,'w')
    usuarios=users_con_registro(periodo,file_conf)
    
    urls=[]
    users_url=[]
    nurls=0
    
    for user in usuarios:
        file=Varhome+'/'+user+'/'+periodo+'/sites'
        d_file=urllib.urlopen(file)
        for line in d_file.readlines():
            datos=line[:line.find('\n')].split(' ')
            url=datos[len(datos)-1]
            try :
                ind=urls.index(url)
            except ValueError:
                users_url.append([user])
                urls.append(url)
                nurls+=1
            else:
                users_url[ind].append(user)
                    
        d_file.close()
    
    r_file.write('_____URL_______________    USUARIOS \n\n')
    #urls ordenadas por usuario, se imprimen en archivo
    for i in range(nurls):
        r_file.write(urls[i]+'  \t')
        for user in users_url[i]:
            r_file.write(user+'  ')
        r_file.write('\n')
    

    r_file.close()
    
##Modulo obtiene paginas web visitadas, ordenadas por nombre 
##accedidas por todos los usuarios o por uno concreto
##salida se registra en archivo de texto plano con el formato:
## url
def pag_url(Varhome, periodo, Rghome,usuario,file_conf):
    """Vuelca en correspondiente archivo paginas visitadas por alguno, o todos
    los usuarios con control web, ordenadas por nombre"""
    
        
    urls=[]
    nurls=0
        
    if usuario.isspace():
        rpurl=Rghome+'/'+periodo+'_pgurl'
        r_file=open(rpurl,'w')
        usuarios=users_con_registro(periodo,file_conf)
      
        for user in usuarios:
            file=Varhome+'/'+user+'/'+periodo+'/sites'
            d_file=urllib.urlopen(file)
            for line in d_file.readlines():
                datos=line[:line.find('\n')].split(' ')
                url=datos[len(datos)-1]
                try :
                    ind=urls.index(url)
                except ValueError:
                    urls.append(url)
                    nurls+=1
            d_file.close()
            
    else:
        rpurl=Rghome+'/'+periodo+'_pgurl_'+usuario
        r_file=open(rpurl,'w')
        if not existe_registro(usuario,periodo,file_conf):
            r_file.close()
            return None
            
        file=Varhome+'/'+usuario+'/'+periodo+'/sites'
        d_file=urllib.urlopen(file)

        for line in d_file.readlines():
            datos=line[:line.find('\n')].split(' ')
            url=datos[len(datos)-1]
            urls.append(url)
            nurls=nurls+1
            
        d_file.close()
        
        
    r_file.write('URLs ORDENADAS ALFABETICAMENTE\n\n')
    urls.sort()   
    for i in range(nurls):
        r_file.write(urls[i]+'\n')
            
    r_file.close()
        

   
##Modulo obtiene paginas visitadas por orden cronologico
##por todos los usuarios con control web o por uno de ellos
##el resultado se vuelca en archivo de texto plano con el formato
## url  ultimo_acceso
def pag_cron(Varhome, periodo, Rghome,usuario,file_conf):
    """Vuelca en correspondiente archivo paginas visitadas por alguno, o todos
    los usuarios con control web, ordenadas cronologicamente"""
    import commands
    import os.path
 
    #consultamos version de sarg instalada, ya que salida distinta
    version=commands.getoutput('/usr/bin/dpkg-query -p sarg | grep Version')
    nversion=float(version.split(' ')[1][:3])
    
    if usuario.isspace():
        rpcron=Rghome+'/'+periodo+'_pgcron'
        r_file=open(rpcron,'w')
        usuarios=users_con_registro(periodo,file_conf)
        
        nurls=0
        urls=[]
        accesos=[]
        
        for user in usuarios:
            file=Varhome+'/'+user+'/'+periodo+'/sites'
            if not os.path.isfile(file):
		r_file.close()
		return None
	    if nversion >= 2.0:
                cab=extrae_cab(user, periodo,file_conf)
            d_file=urllib.urlopen(file)
            for line in d_file.readlines():
                datos=line[:line.find('\n')].split(' ')
                url=datos[len(datos)-1]
                t_url=transforma_url(url)
                if nversion>=2.0:
                    f_user='tt'+cab+'-'+t_url+'.html'
                    df_user=Varhome+'/'+user+'/'+periodo+'/'+cab+'/'+f_user
                else:
                    f_user='tt127.0.0.1-'+t_url+'.html'
                    df_user=Varhome+'/'+user+'/'+periodo+'/'+f_user
                acceso=ultimo_acceso(df_user,url)
                try :
                    ind=urls.index(url)
                except ValueError:
                    urls.append(url)
                    #incluye ultimo acceso
                    accesos.append([nurls,acceso])
                    nurls+=1
                else:#recalcula ultimo acceso
                    if cmp_acceso(accesos[ind][1],acceso)==1:
                        accesos.pop(ind)
                        accesos.insert(ind,[ind,acceso])
              
            d_file.close()
    else:
        rpcron=Rghome+'/'+periodo+'_pgcron_'+usuario
        r_file=open(rpcron,'w')
        if not existe_registro(usuario,periodo,file_conf):
            r_file.close()
            return None
        
        file=Varhome+'/'+usuario+'/'+periodo+'/sites'
        if not os.path.isfile(file):
		r_file.close()
		return None
        d_file=urllib.urlopen(file)
        if nversion>=2.0:
            cab=extrae_cab(usuario, periodo,file_conf)
                
        nurls=0
        urls=[]
        accesos=[]
    
        for line in d_file.readlines():
            datos=line[:line.find('\n')].split(' ')
            url=datos[len(datos)-1]
            urls.append(url)
            #busca ultimo acceso a la pagina
            t_url=transforma_url(url)
            if nversion>=2.0:
                f_user='tt'+cab+'-'+t_url+'.html'
                df_user=Varhome+'/'+usuario+'/'+periodo+'/'+cab+'/'+f_user
            else:
                f_user='tt127.0.0.1-'+t_url+'.html'
                df_user=Varhome+'/'+usuario+'/'+periodo+'/'+f_user
            acceso=ultimo_acceso(df_user,url)
            accesos.append([nurls,acceso])
            nurls+=1
            
        d_file.close()
        
    r_file.write('_____URL_______________  ULTIMO ACCESO \n\n')
    accesos.sort(lambda x,y:cmp_acceso(x[1],y[1]))
    for i in range(nurls):
        r_file.write(urls[accesos[i][0]]+'  \t'+str(accesos[i][1])+'\n')
        
    r_file.close()
        
    
##Modulo obtiene paginas web visitadas ordenadas por numero de visitas
##accedidas por todos los usuarios o por uno concreto
##vuelca resultado en archivo de texto plano con formato
## url numero_visitas
def pag_nvisit(Varhome, periodo, Rghome,usuario,file_conf):
    """Vuelca en correspondiente archivo paginas visitadas por alguno, o todos
    los usuarios con control web, ordenadas por numero de visitas"""
    if usuario.isspace():
        rpnvisit=Rghome+'/'+periodo+'_pgnvisit'
        r_file=open(rpnvisit,'w')
        usuarios=users_con_registro(periodo,file_conf)
        
        n_visit=[]
        urls=[]
        nurls=0
        
        for user in usuarios:
            file=Varhome+'/'+user+'/'+periodo+'/sites'
            d_file=urllib.urlopen(file)
            for line in d_file.readlines():
                datos=line[:line.find('\n')].split(' ')
                url=datos[len(datos)-1]
                #extraigo num accesos del usuario
                nvisitas=long(datos[0])
                try :
                    ind=urls.index(url)
                except ValueError:
                    urls.append(url)
                    #incluye num accesos
                    n_visit.append([nurls,nvisitas])
                    nurls+=1
                else:#recalcula ultimo acceso
                    nvisit=n_visit.pop(ind)[1]
                    tvisit=int(nvisitas)+int(nvisit)
                    n_visit.insert(ind,[ind,tvisit])
                    
            d_file.close()    
    else:
         
        rpnvisit=Rghome+'/'+periodo+'_pgnvisit_'+usuario
        r_file=open(rpnvisit,'w')
        if not existe_registro(usuario,periodo,file_conf):
            r_file.close()
            return None
        
        file=Varhome+'/'+usuario+'/'+periodo+'/sites'
        d_file=urllib.urlopen(file)
                
        n_visit=[]
        urls=[]
        nurls=0
        for line in d_file.readlines():
            datos=line[:line.find('\n')].split(' ')
            url=datos[len(datos)-1]
            urls.append(url)
            #extraigo num accesos
            nvisitas=long(datos[0])
            #incluye numero visitas
            n_visit.append([nurls,nvisitas])
            nurls=nurls+1
            
        d_file.close()
    
    
    r_file.write('_____URL______________   NUM_VISITAS \n\n')
    n_visit.sort(lambda x, y: numeric_compare(x[1],y [1]))
   
    for i in range(nurls):
        r_file.write(urls[n_visit[i][0]]+' \t'+str(n_visit[i][1])+'\n')
            
    r_file.close()

      

##Modulo obtiene paginas web visitadas ordenadas segun trafico web acapararon
##para un solo usuario del sistema o para todos los controlados por acept
##vuelca salida en archivo de texto plano con formato:
## url  cant_bytes_transferidos %_trafico_web_acaparo
def pag_trafic(Varhome,periodo,Rghome,usuario,file_conf):
    """Vuelca en correspondiente archivo paginas visitadas por alguno, o todos
    los usuarios con control web, ordenadas por trafico registrado"""
    if usuario.isspace():
        rptrafic=Rghome+'/'+periodo+'_pgtrafic'
        r_file=open(rptrafic,'w')
        usuarios=users_con_registro(periodo,file_conf)

        v_trafic=[]
        t_trafic=0#acumula trafico total en el sistema
        urls=[]
        nurls=0
        
        for user in usuarios:
            file=Varhome+'/'+user+'/'+periodo+'/sites'
            d_file=urllib.urlopen(file)
            for line in d_file.readlines():
                datos=line[:line.find('\n')].split(' ')
                url=datos[len(datos)-1]
                #extraigo vol trafico del usuario
                vtrafico=long(datos[1])
                t_trafic=t_trafic+vtrafico
                #incluye  volumen total trafico de url
                try :
                    ind=urls.index(url)
                except ValueError:
                    urls.append(url)
                    #incluye num accesos
                    v_trafic.append([nurls,vtrafico])
                    nurls+=1
                else:#recalcula ultimo acceso
                    trafic=v_trafic.pop(ind)[1]
                    ttrafic=int(vtrafico)+int(trafic)
                    v_trafic.insert(ind,[ind,ttrafic])
                    
            d_file.close()
            
    else:
        
        rptrafic=Rghome+'/'+periodo+'_pgtrafic_'+usuario
        r_file=open(rptrafic,'w')
        if not existe_registro(usuario,periodo,file_conf):
            r_file.close()
            return None
            
        file=Varhome+'/'+usuario+'/'+periodo+'/sites'
        d_file=urllib.urlopen(file)
        
        v_trafic=[]
        t_trafic=0#acumula trafico total registrado en el sistema por el usuario
        urls=[]
        nurls=0
        for line in d_file.readlines():
            datos=line[:line.find('\n')].split(' ')
            url=datos[len(datos)-1]
            urls.append(url)
            #extraigo volumen de trafico
            vtrafic=long(datos[1])
            #incluye volumen de trafico
            v_trafic.append([nurls,vtrafic])
            nurls=nurls+1
            t_trafic=t_trafic+vtrafic
        
        d_file.close()
        
    r_file.write('_____URL_____________  TRAFICO REGISTRADO \n\n')
    
    v_trafic.sort(lambda x, y: numeric_compare(x[1],y [1]))
   
    for i in range(nurls):
        p_trafic=(float(v_trafic[i][1])/float(t_trafic))*100.0
        n_ptrafic=normaliza_cad(str(p_trafic))
        r_file.write(urls[v_trafic[i][0]]+' \t'+str(v_trafic[i][1])+' '+n_ptrafic+'%\n')
            
    r_file.close()

    
##Modulo obtiene paginas accedidas en cuyo nombre aparece una palabra clave
##por un usuario concreto del sistema o por todos los usuarios acept
##vuelca resultado en archivo de texto plano con siguiente formato:
## url
def pag_clave(Varhome,periodo,usuario,file_conf,clave):
    """Extrae lista de paginas visitadas por alguno o todos los usuarios con control web
    que contienen la palabra clave especificada"""
    urls=[]
    if usuario.isspace():
        usuarios=users_con_registro(periodo,file_conf)
       
        for user in usuarios:
            file=Varhome+'/'+user+'/'+periodo+'/sites'
            d_file=urllib.urlopen(file)
            for line in d_file.readlines():
                datos=line[:line.find('\n')].split(' ')
                #se obtiene url accedida
                url=datos[len(datos)-1]
                #se comprueba si contiene la palabra clave
                if url.find(clave)!=-1:
                    try :
                        ind=urls.index(url)
                    except ValueError:
                        #se incluye en url si no se habia echo antes
                        urls.append(url)
            
            d_file.close()
            
    else:
        if not existe_registro(usuario,periodo,file_conf):
            return urls
        
        file=Varhome+'/'+usuario+'/'+periodo+'/sites'
        d_file=urllib.urlopen(file)
                   
        for line in d_file.readlines():
            datos=line[:line.find('\n')].split(' ')
            url=datos[len(datos)-1]
            if url.find(clave)!=-1:
                urls.append(url)
                
        d_file.close()
        
    return urls
        
##Modulo genera registros de navegacion de los ultimos dias 
##que son posteriormente utilizados por usuario para obtener informes
def genera_registros_nuevos(file_conf):
    """Genera registros de navegacion desde ultima fecha hasta la fecha actual"""
    import os, os.path
    import time, commands
    
    xmldoc=parse_file(file_conf)
    
    #extrae usuarios con control web
    usuarios=users_control_web(archivo.aceptlog)
    
    #fechas comprende registro a generar
    last_date=consulta_campo('last_date',archivo.aceptlog)
    date=time.localtime()
    act_date=time.strftime("%d%b%Y",date)
    
    name_reg=last_date.capitalize()+'-'+act_date.capitalize()
    sarg_bin=consulta_campo('sargbin',archivo.aceptlog)
    dir_conf=consulta_campo('conf_sq',archivo.aceptlog)
    dir_log=consulta_campo('logdir',archivo.aceptlog)
    sargrg=consulta_campo('sargrg',archivo.aceptlog)
    
    for user in usuarios:
        destino=sargrg+'/'+user+'/'+name_reg
	mje='Extrayendo registros de navegacion de user '+user
        escribe_log(mje, archivo.mefilog)
        if  not os.path.isdir(destino):
            orden=sarg_bin+' -f '+dir_conf+'sarg_'+user+'.conf'
            salida=commands.getoutput(orden)
            if salida.find('No se encontraron registros')==-1:
                n_reg=salida[salida.rfind('/')+1:]
                dest_tmp=sargrg+'/'+user+'/'+n_reg
                if dest_tmp.find(destino)==-1:
                    modifica_html(user, name_reg, n_reg, file_conf)
                    os.system('mv '+dest_tmp+' '+destino)
                clean='echo " " >'+dir_log+user+'/access.log'
                os.system(clean)
                
    actualiza_campo('last_date',act_date, archivo.aceptlog)
            
##Modulo extrae informacion acerca del uso de los servicios declarados en el sistema, por parte
##de los usuarios monitorizados (todos, o el especificado concretamente), 
##ordenadolos por tiempo de uso   
def aplic_tmp_uso(usuario,periodo,file_conf):
    """Extrae datos de uso de las aplicaciones monitorizadas en el sistema por parte de todos los
    usuarios o alguno concreto, devuelve diccionario con consumo para cada servicio"""
    from xml import xpath
    from watcherMods import suma_horas
    import os.path
    
    xmldoc=parse_file(file_conf)
    
    servicios_def=xpath.Evaluate('/config/servicios/*',xmldoc)
    consumo_servicios={}

    for serv in servicios_def:
        consumo_servicios[serv.localName]="00:00:00"
    
    file='/usr/share/acept/estadisticas/aplic_'+periodo+'.txt'
    
    if not os.path.isfile(file):
	return consumo_servicios
    
    f=open(file,'r')
    
    for line in f.readlines():
        datos=line[:line.find('\n')].split(' ')
        if usuario.find('Todos')!=-1 or datos[1].find(usuario)!=-1:
            consumo_servicios[datos[0]]=suma_horas(consumo_servicios[datos[0]],datos[2])
    for key in consumo_servicios.keys():
        if consumo_servicios[key].find("00:00:00")!=-1:
            del(consumo_servicios[key])
 
    f.close()
    return consumo_servicios
   
##Modulo consulta las aplicaciones usadas por los usuarios monitorizados en el sistema
##en el periodo de tiempo especificado
def aplic_usuario(periodo, file_conf):
    """Extrae aplicaciones usadas en el sistema por parte de los usuarios monitorizados,
    devuelve diccionario, cada servicio(=elemento del diccionario) tiene asociada
    lista de usuarios"""
    import os.path
    
    file='/usr/share/acept/estadisticas/aplic_'+periodo+'.txt'
    
    if not os.path.isfile(file):
	return {}
    
    f=open(file,'r')
    serv_usados={}

    for line in f.readlines():
        datos=line[:line.find('\n')].split(' ')
        if serv_usados.has_key(datos[0]):
            serv_usados[datos[0]].append(datos[1])
        else:
            serv_usados[datos[0]]=[datos[1]]
            
    f.close()    
    return serv_usados
    
##Modulo consulta las aplicaciones usadas por los usuarios monitorizados en el sistema
##en el periodo de tiempo especificado junto con el tiempo gastado
def aplic_usuario_tmp(periodo, file_conf):
    """Extrae aplicaciones usadas en el sistema por parte de los usuarios monitorizados,
    devuelve diccionario, cada servicio(=elemento del diccionario) tiene asociada
    lista de usuarios"""
    import os.path
    
    file='/usr/share/acept/estadisticas/aplic_'+periodo+'.txt'
    
    if not os.path.isfile(file):
	return {}
    
    f=open(file,'r')
    entrys={}

    
    for line in f.readlines():
        datos=line[:line.find('\n')].split(' ')
        if entrys.has_key(datos[1]):
	    entrys[datos[1]].append(datos[0]+'  '+datos[2])
	else:
	    entrys[datos[1]]=[datos[0]+'  '+datos[2]]
    
    f.close()    
    return entrys

def extiende_periodo(tipo, periodo):
    """Agrega a periodo que corresponde a un mes aclaracion indicando nombre de mes y anno"""

    if tipo=='m':
        if periodo[:2]=='01':
            mes='Enero'
        elif periodo[:2]=='02':
            mes='Febrero'
        elif periodo[:2]=='03':
            mes='Marzo'
        elif periodo[:2]=='04':
            mes='Abril'
        elif periodo[:2]=='05':
            mes='Mayo'
        elif periodo[:2]=='06':
            mes='Junio'
        elif periodo[:2]=='07':
            mes='Julio'
        elif periodo[:2]=='08':
            mes='Agosto'
        elif periodo[:2]=='09':
            mes='Septiembre'
        elif periodo[:2]=='10':
            mes='Octubre'
        elif periodo[:2]=='11':
            mes='Noviembre'
        else:
            mes='Diciembre'
        periodo=periodo+'('+mes+periodo[2:]+')'       
    
    return periodo

