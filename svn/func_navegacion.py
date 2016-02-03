# -*- coding: ISO-8859-1 -*-
#
# Fichero:	func_navegacion.py
# Copyright:	Junta de Andalucía <devmaster@guadalinex.org>
# Autor:	Maria Dolores Perez Gutierrez y Nestor Chacon Manzano
# Fecha:	lun mar 27 17:01:25 CET 2006
# Licencia:	GPL v.2
#
# Archivo recoge modulos auxiliares para las funciones con las que se obtienen
# las estadisticas de los registros de navegacion web 

import urllib
from mefiGlobal import *

##Funcion para comparacion numerica de dos objetos
##Usada en funciones: pag_nvisit , pag_trafic
def numeric_compare(x, y):
    """Devuelve diferencia entera entre ambos numeros"""
    return int(y)-int(x)  

    
##Funcion normaliza resultado porcentaje 
##mantiene solo dos cifras decimales del resultado completo
##Usada en funciones: trafico_usuario , pag_trafic
def normaliza_cad(cad):
    """Normaliza la cadena en resultado similar en el que solo se mantienen dos cifras decimales"""
    cad2=''
    for i in range(len(cad)):
        if cad[i]=='.':
            cad2=cad2+cad[i:i+3]
            break
        else:
            cad2=cad2+cad[i]
        
    return cad2
    
##Modulo transforma nombre url al formato con el que se nombran los archivos
##sustituye '.' y '-' por '_'
##Usada en funcion: pag_cron
def transforma_url(url):
    """Transforma url a formato en el que se sustituye '.' y '-' port '_' """
    t_url=''
    for i in range(len(url)):
        if(url[i]=='.') or (url[i]=='-')or (url[i]==':'):
            t_url=t_url+'_'
        else:
            t_url=t_url+url[i]
        
    return t_url
    
   
##Modulo accede a archivo especificado y devuelve ultima fecha de acceso registrada
##en ese archivo con formato 'dd/mm/aaaa hh:mm:ss'
##Funcion usada en: pag_cron
def ultimo_acceso(archivo,url):
    """Devuelve fecha de acceso registrada para url especificada en archivo"""
    import os.path
   
    if not os.path.isfile(archivo):
	return ''

    d_file=urllib.urlopen(archivo)
    lines=d_file.readlines()
    tam=len(lines)
    for i in range(tam):
        j=tam-i-1
        n=lines[j].find(url)
        if n!=-1:#ultima linea contiene url detalla ultimo acceso
            #fecha formato dd/mm/aaa
            fi=lines[j].find('/20')-5
            fecha= lines[j][fi:fi+10]
            #hora formado hh:mm:ss
            hi=lines[j].find(':')-2
            hora= lines[j][hi:hi+8]
            break
        
    acceso=fecha+' '+hora
    return acceso
    
    
##Modulo recibe dos fechas con formato 'dd/mm/aaa hh:mm:ss'
##devuelve 1 si la segunda es mas actual
##devuelve 0 si son iguales
##devuelve -1 si la primera es mas actual
##Funcion usada en: pag_cron
def cmp_acceso(ult_acceso, acceso):
    """Compara cual de las dos fechas recibidas es la mas actual(-1:la primera, 1:la segunda),
    0 si coinciden"""
    if len(ult_acceso)==0:
	if len(acceso)==0:
		return 0
	else:
		return 1
    else:
	if len(acceso)==0:
		return -1 
	else:
		pass

    if int(acceso[6:10])>int(ult_acceso[6:10]):#comprueba anno
        return 1
    elif int(acceso[6:10])==int(ult_acceso[6:10]):
        if int(acceso[3:5])>int(ult_acceso[3:5]):#comprueba mes
            return 1
        elif int(acceso[3:5])==int(ult_acceso[3:5]):
            if int(acceso[0:2])>int(ult_acceso[0:2]):#comprueba dia
                return 1
            elif int(acceso[0:2])==int(ult_acceso[0:2]):
                if int(acceso[11:13])>int(ult_acceso[11:13]):#comprueba hora
                    return 1
                elif int(acceso[11:13])==int(ult_acceso[11:13]):
                    if int(acceso[14:16])>int(ult_acceso[14:16]):#comprueba min
                        return 1
                    elif int(acceso[14:16])==int(ult_acceso[14:16]):
                        if int(acceso[17:19])>int(ult_acceso[17:19]):#comprueba seg
                            return 1
                        elif int(acceso[17:19])==int(ult_acceso[14:16]):
                            return 0
        
    return -1

###LOS SIGUIENTES MODULOS EXTRAEN LOS DATOS QUE INDICAN SEGUN FORMATO
###EXISTENTE EN ARCHIVOS DE SALIDA QUE PROPORCIONA SARG
    
    
def cambia_cadena(archivo, cad_nueva, cad_anterior):
    """Sustituye en archivo especificado, apariciones de cadena cad_anterior
    por cad_nueva"""
    d_file=urllib.urlopen(archivo)
    lines=d_file.readlines()
    d_file.close()
    
    fw=open(archivo,'w')
    
    for line in lines:
        if line.find(cad_anterior)!=-1:
            iter=line.count(cad_anterior)
            for i in range(iter):
                n=line.find(cad_anterior)
                line=line[:n]+cad_nueva+line[n+len(cad_anterior):]
        fw.write(line)
    
    fw.close()
    
##Modulo modifica archivos de registros generados por sarg para usuario
##estableciendo en ellos la nomenclatura de periodo considerada en acept
##formato considera acept: Ultfecha-fechaActual (ddmmmaaaa-ddmmmaaaa)
def modifica_html(user,nombre_final, nombre_orig, file_conf):
    """Modifica registros generados para usuario estableciendo nomenclatura para 
    periodo considerado por acept en lugar del que por defecto establece sarg"""
    from func import consulta_campo
    
    sargrg=consulta_campo('sargrg',archivo.mefilog)
    
    #Modifica entrada en archivo index.html del usuario
    file=sargrg+'/'+user+'/index.html'
    cambia_cadena(file, nombre_final, nombre_orig)
    #Modifica entrada en index.html de subdirectorio 
    file=sargrg+'/'+user+'/'+nombre_orig+'/index.html'
    cambia_cadena(file, nombre_final, nombre_orig)
    #Modifica entrada en index.html de subdirectorio 
    file=sargrg+'/'+user+'/'+nombre_orig+'/siteuser.html'
    cambia_cadena(file, nombre_final, nombre_orig)
    #Modifica entrada en index.html de subdirectorio 
    file=sargrg+'/'+user+'/'+nombre_orig+'/topsites.html'
    cambia_cadena(file, nombre_final, nombre_orig)
    
##Modulo empleado cuando version de sarg en sistema es 2.0 o superior
##Obtiene nombre de directorio donde se recogen archivos de acceso a cada url
##para extraer posteriormente fechas de acceso
def extrae_cab(user, periodo, file_conf):
    """Extrae nombre de directorio que aparece en directorio donde se almacenan regs.
    de navegacion resumen de sarg. Se usa para version de sarg 2.0 o superior"""
    from func import consulta_campo
    import os, os.path
    
    sargrg=consulta_campo('sargrg',archivo.mefilog)
    
    path=sargrg+'/'+user+'/'+periodo
    list=os.listdir(path)
    cab=''
    for item in list:
        path_item=os.path.join(path,item)
        if os.path.isdir(path_item):
            cab=item[item.rfind('/')+1:]
        
    return cab
