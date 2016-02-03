#!/usr/bin/env python
# -*- coding: ISO-8859-15 -*-
#
# Fichero:	mensaje.py
# Copyright:	Junta de Andalucía <devmaster@guadalinex.org>
# Autor:	Maria Dolores Perez Gutierrez y Nestor Chacon Manzano
# Fecha:	lun mar 27 17:01:32 CET 2006
# Licencia:	GPL v.2
#
# Busca todas las conexiones al sistema de un usuario dado y le lanza un mensaje

import os
import utmp
from sys import argv, exit
from time import sleep
from UTMPCONST import USER_PROCESS

# Comprueba que el numero de argumentos es el correcto 
# y si no sale
if len(argv) == 3 :
    usuario = argv[1]
    mensaje = argv[2]
else :
    exit()
    
# Define donde esta el home del usuario.
# en caso de no existir finaliza la ejecucion
f=open("/etc/passwd","r")
passwd=f.readlines()
f.close()
home=""
for i in passwd:
    if i.split(":")[0] == usuario:
	home = i.split(":")[5]
	break
if not home:
    exit()

        
# Almacena donde está el usuario. 
# Si no esta conectado al sistema termina. 
lugares=[]
a = utmp.UtmpRecord()
for b in a:
    if b.ut_type == USER_PROCESS:
        if b.ut_user == usuario:
                lugares.append(b.ut_line)
a.endutent()

if not lugares:
    exit()

# Lanza el mensaje alli donde se encuentre el usuario 
for j in lugares:
    grafico=len(j.split(":"))
    
    # mensajes en modo texto
    if grafico == 1 :
	try:
	    f=open('/dev/'+j,'w')
	    f.write('\n'+mensaje+'\n\n')
	    f.close()
	except:
	    pass
    
    # mensajes en modo gráfico
    elif grafico == 2 :
	subproceso=os.fork()
	if not subproceso :
	    
	    # Establece las variables de entorno.
	    # En caso de no encontrar el archivo Xauthority del usuario, 
	    # finaliza el subproceso
	    if os.path.exists(home+"/.Xauthority"):
		os.environ["XAUTHORITY"]=home+"/.Xauthority"
		os.environ["DISPLAY"]=j
	    else:
		exit()

	    import wx
	    class Alerta(wx.Frame):
		def __init__(self, *args, **kwds):
		    kwds["style"] = wx.DEFAULT_FRAME_STYLE
		    wx.Frame.__init__(self, *args, **kwds)
		    msj="- "+mensaje+" -"
		    self.label_1 = wx.StaticText(self, -1, msj)
		    self.button_1 = wx.Button(self, -1, "Aceptar")

		    self.__set_properties()
		    self.__do_layout()

		    wx.EVT_BUTTON(self,self.button_1.GetId(),self.cierra)

		def __set_properties(self):
		    self.SetTitle("Alarma ACEPT")
		    self.label_1.SetFont(wx.Font(18, wx.DEFAULT, wx.BOLD, wx.NORMAL, False,""))
		    _icon = wx.EmptyIcon()
		    _icon.CopyFromBitmap(wx.Bitmap("/usr/share/acept/pixmaps/fondo_junta.gif", wx.BITMAP_TYPE_ANY))
		    self.SetIcon(_icon)

		def __do_layout(self):
		    sizer_1 = wx.BoxSizer(wx.VERTICAL)
		    sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		    sizer_4 = wx.BoxSizer(wx.VERTICAL)
		    sizer_2.Add((20, 20), 0, 0, 0)
		    sizer_4.Add((20, 20), 1, 0, 0)
		    sizer_4.Add(self.label_1, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
		    sizer_4.Add((20, 20), 1, 0, 0)
		    sizer_4.Add(self.button_1, 0, wx.EXPAND, 0)
		    sizer_4.Add((20, 20), 0, 0, 0)
		    sizer_2.Add(sizer_4, 1, wx.EXPAND, 0)
		    sizer_2.Add((20, 20), 0, 0, 0)
		    sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
		    self.SetAutoLayout(True)
		    self.SetSizer(sizer_1)
		    sizer_1.Fit(self)
		    sizer_1.SetSizeHints(self)
		    self.Layout()
		
		def cierra (self, event) :
		    self.Close()
	    
	    class Inicio_App(wx.App):
		""" Inicializa el entorno Gráfico """
		def OnInit(self):
		    wx.InitAllImageHandlers()
		    self.alerta=Alerta(None,-1,"")
		    self.alerta.Show()
		    return True
		
	    inicio=Inicio_App()
	    inicio.MainLoop()
	    
	    exit()
	
	else:
	    # Espera un tiempo tras lanzar el mensaje grafico
	    sleep(1)

