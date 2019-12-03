#######################################################
# Author: rcontreras
# 
# Agregar target a datasources existentes
########################################################

import sys
from java.lang import System
from java.io import FileInputStream

def cabecera(conexion):
    print ''
    print '---------------------------------------------------------------------------'
    print '## Datos de Conexion : '
    print '## url      : ' + str(conexion['url'])
    print '## username : ' + str(conexion['user'])
    print '## password : ' + str(conexion['pswd'])
    print '## target   : ' + str(conexion['target'])
    print '---------------------------------------------------------------------------'
    print ''
    return

def iniciarConexionWL(wlparams):
    try:
        cabecera(wlparams);
        connect (wlparams['user'], wlparams['pswd'], wlparams['url'])
        
    except Exception, e:
        print '>> Error durante la conexion!!!'
        print e
        
    return



def obtenerParametrosGenerales():
    propInputStream = FileInputStream("01_config.properties")
    configProps = Properties()
    configProps.load(propInputStream)
    grl = {}
    grl['user'] = configProps.get("admin.userName")
    grl['pswd'] = configProps.get("admin.password")
    grl['url'] = configProps.get("admin.url")
    grl['type'] = configProps.get("datasource.target.type")
    grl['target'] = configProps.get("datasource.target.list")
    grl['dominio'] = configProps.get("domain.name")
    return grl



def obtenerListaDataSources(mainParams):
    propInputStream = FileInputStream("02_datasources.properties")
    fdProps = Properties()
    fdProps.load(propInputStream)
    totalds = int(fdProps.get("ds.total"))
    print '>> total data sources : ' + str(totalds)
    listaDs = []
    i = 1
    while (i <= totalds):
        recurso = {}
        recurso['dominio'] = mainParams['dominio']
        recurso['name'] = fdProps.get("ds.%s.name" %(str(i)))
        recurso['target'] = mainParams['target']
        recurso['type'] = mainParams['type']

        listaDs.append(recurso)
        print '>> [%s] item' %(str(i))
        i = i + 1
    
    return listaDs



def addTargetsListaDataSources(listaDataSources):
    try:
        
        print '>> Iniciando Proceso de Asignación de targets a DataSources'
        for recurso in listaDataSources:
            print '>> ' + str(recurso)
            addTargetDataSource(recurso);
        
    except Exception, e:
        print '>> Error durante la Asignación de targets a DataSources!!!'
        print e
        
    return


def addTargetDataSource(dsParams):
    try:
        print '> Iniciando Asignación de Target ...'
        # Generamos Bloqueo en el Servidor
        edit()
        startEdit()
        
        print("Data-Source: " + dsParams['name'])
        dataSource = lookup(dsParams['name'], "JDBCSystemResource")
		
        # Targets
        listaDestinos = str(dsParams['target']).split(',')
        print '--------------'
        print listaDestinos
        print '--------------'
        
        for destino in listaDestinos:
            trg = dsParams['type'] +'/' +destino
            print '------------------------------------------------------------------'
            print '>>> Buscando Destino : ' + trg
            targetMBean = getMBean(trg)
            if targetMBean is None:
                print '>>> (' + trg + ') NO ENCONTRADO. -----------> VERIFICAR!!!!!'
            else:
                dataSource.addTarget(targetMBean)
                print '>>> (' + trg + ') ASIGNADO'
        
        print '------------------------------------------------------------------'        
        
        # Levantamos el Bloqueo del Servidor
        save()
        activate()
        print '> Despliegue Finalizado Existosamente!'
        
    except Exception, e:
        print '> Asignación de DataSource con Errores!'
        print e
        undo('true','y')
    return



print '*[INI]************************************'
general = obtenerParametrosGenerales();
print general

iniciarConexionWL(general);

listaDataSources = obtenerListaDataSources(general);
print listaDataSources
addTargetsListaDataSources(listaDataSources);