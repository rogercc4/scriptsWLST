#----------------------------------------------------------------------
# Creacion de DataSources
#----------------------------------------------------------------------

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

def crearDataSource(dsParams):
    try:
        print '> Iniciando Creacion de DataSource ...'
        # Generamos Bloqueo en el Servidor
        edit()
        startEdit()
        
        def addJDBC(prefix):
            print ("")
            print (">>> Creando la configuracion en el servidor : " + dsParams["dominio"])
        
        print("DataSource: " + dsParams['name'])
        jdbcSystemResource = create(dsParams['name'],"JDBCSystemResource")
        myFile = jdbcSystemResource.getDescriptorFileName()
        print ("Descriptor JDBC: " + myFile)
        
        jdbcResource = jdbcSystemResource.getJDBCResource()
        jdbcResource.setName(dsParams['name'])
        
        # JDBCDataSourceParams
        dpBean = jdbcResource.getJDBCDataSourceParams()
        dpBean.setJNDINames([dsParams['jndi']])
        dpBean.setGlobalTransactionsProtocol(dsParams['gblTrPr'])
        
        # JDBCDriverParams
        drBean = jdbcResource.getJDBCDriverParams()
        drBean.setPassword(dsParams['pswd'])
        drBean.setUrl(dsParams['url'])
        drBean.setDriverName(dsParams['drvr'])
        
        propBean = drBean.getProperties()
        driverProps = Properties()
        driverProps.setProperty("user",dsParams['user'])
        
        e = driverProps.propertyNames()
        while e.hasMoreElements() :
           propName = e.nextElement()
           myBean = propBean.createProperty(propName)
           myBean.setValue(driverProps.getProperty(propName))
        
        # JDBCConnectionPoolParams
        ppBean = jdbcResource.getJDBCConnectionPoolParams()
        ppBean.setInitialCapacity(int(dsParams['iniCap']))
        ppBean.setMaxCapacity(int(dsParams['maxCap']))
        ppBean.setConnectionReserveTimeoutSeconds(int(dsParams['timeOut']))
        
        if not dsParams['shrink'] == None:
           ppBean.setShrinkFrequencySeconds(dsParams['shrink'])
        if not dsParams['testQry'] == None:
           ppBean.setTestTableName(dsParams['testQry'])
        
        # JDBCXAParams
        xaParams = jdbcResource.getJDBCXAParams()
        xaParams.setKeepXaConnTillTxComplete(1)
        
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
                jdbcSystemResource.addTarget(targetMBean)
                print '>>> (' + trg + ') ASIGNADO'
        
        print '------------------------------------------------------------------'
        
        
        # Levantamos el Bloqueo del Servidor
        save()
        activate()
        print '> Despliegue Finalizado Existosamente!'
        
    except Exception, e:
        print '> Creacion de DataSource con Errores!'
        print e
        undo('true','y')
        
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
    dsProps = Properties()
    dsProps.load(propInputStream)
    totalDs = int(dsProps.get("ds.total"))
    print '>> totalDs : ' + str(totalDs)
    listaDs = []
    i = 1
    while (i <= totalDs):
        recurso = {}
        recurso['dominio'] = mainParams['dominio']
        recurso['name'] = dsProps.get("ds.%s.name" %(str(i)))
        recurso['jndi'] = dsProps.get("ds.%s.jndiname" %(str(i)))
        recurso['drvr'] = dsProps.get("ds.%s.driver.class" %(str(i)))
        recurso['url'] = dsProps.get("ds.%s.url" %(str(i)))
        recurso['user'] = dsProps.get("ds.%s.username" %(str(i)))
        recurso['pswd'] = dsProps.get("ds.%s.password" %(str(i)))
        recurso['iniCap'] = dsProps.get("ds.%s.initialCapacity" %(str(i)))
        recurso['maxCap'] = dsProps.get("ds.%s.maxCapacity" %(str(i)))
        recurso['timeOut'] = dsProps.get("ds.%s.connection.reserved.timeout" %(str(i)))
        recurso['testQry'] = dsProps.get("ds.%s.test.query" %(str(i)))
        recurso['gblTrPr'] = dsProps.get("ds.%s.global.transaction.protocol" %(str(i)))
        recurso['type'] = mainParams['type']
        recurso['target'] = mainParams['target']
        recurso['shrink'] = None
        listaDs.append(recurso)
        print '>> [%s] item' %(str(i))
        i = i + 1
    
    return listaDs

def crearListaDataSources(wlparams,lista):
    try:
        cabecera(wlparams);
        connect (wlparams['user'], wlparams['pswd'], wlparams['url'])
        
        print '>> Iniciando Proceso de Creacion de DataSources'
        for recurso in lista:
            print '>> ' + str(recurso)
            crearDataSource(recurso);
        
    except Exception, e:
        print '>> Error durante la creacion de los DataSources!!!'
        print e
        
    return

print '*[INI]************************************'
general = obtenerParametrosGenerales();
print general
listaRecursos = obtenerListaDataSources(general);
print listaRecursos
crearListaDataSources(general,listaRecursos);
print '*[FIN]************************************'
