#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
#
# Fichero:	setup.py
# Copyright:	Junta de Andalucía <devmaster@guadalinex.org>
# Autor:	Maria Dolores Pérez Gutiérrez y Néstor Chacón Manzano
# Fecha:	lun mar 27 17:00:33 CET 2006
# Licencia:	GPL v.2
#

from distutils.core import setup

setup(name='acept',
	version='1.2.6',
	description='Aplicacion para el control electronico de acceso a Internet',
	author='Maria D. Perez, Nestor Chacon Manzano, Juan M. Ferrer Olivencia',
	author_email='mshk@caton.es nchacon@caton.es jmferrer@caton.es',
	url='http://forja.guadalinex.org/repositorio/projects/acept/',
	long_description='Herramienta permite el control del uso de un ordenador que hacen los usuarios',
	py_modules=["avanzado",
        "ayuda",
        "confSquid",
        "func_blacklists",
        "func_navegacion",
        "func","informes",
        "inicSquid",
        "mefiGlobal",
        "watcherMods",
        "watcherSquid",
        "wizard"],
	scripts=['gui-acept','acept','mefistofelina','msg'],
	data_files=[('/etc/acept/watcherCat',['config/watcherconf.xml',
					'config/asocia_contenidos',
					'config/limpia_iptables']),
	('/etc/acept/squid',['config/squid_acept.conf',
        'config/sarg_acept.conf']),
    ('/var/log/acept/squid/var/cache',['config/.ok']),
    ('/var/log/acept/squid/var/rg',['config/.ok']),
    ('/var/log/acept/squid/var/logs',['config/.ok']),
    ('/var/log/acept/squidGuard/logs',['config/.ok']),
    ('/usr/share/acept/estadisticas',['config/.ok']),
    ('/usr/share/doc/acept',['copyright']),
    ('/etc/pam.d',['config/gdm.acept','config/gdm-autologin.acept','config/login.acept']),
    ('/etc/gdm/PostLogin',['config/Default.acept']),
    ('/etc/security',['config/time.conf.acept']),
	('/usr/share/applications',['config/acept.desktop','config/acepti.desktop']),
	('/usr/share/acept',['informe.py',
        'lanza_informe.sh',
        'config/blacklists.tar.gz',
        'mas_info.py',
        'mensaje.py',
        'barra.py',
        'modelo.html'])])
