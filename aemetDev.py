# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 13:48:53 2019

@author: solis
"""
import sqlite3
from collections import OrderedDict
import logging
from xml.etree.ElementTree import Element as xmlElement

# fichero de parámetros del programa
FILEPARAM = 'aemetDev.xml'
FILE_INSERT_IF_NOT_EXISTS = 'estaciones.sql'

# Mensajes que aparecen más de una vez
MSG_NO_OPTION = 'Salir'
MSG_NO_VALID_OPTION = 'No es una selección válida'
MSGWRITE1OPTION = 'Sitúe el cursor al final de la línea ' + \
                  'y teclee un número entre los mostrados: '
MSG_END_OK = 'Proceso terminado correctamente'
MSGREVISARPARAM = f'-Puedes revisar ahora el contendo de {FILEPARAM}-'


def menuMain():
    """
    Selección desde el menú principal
    """
    headers = ('\nAEMET Utilidades. Menú principal',
               MSGREVISARPARAM)

    options = ('Unir tablas de estaciones aemet de idee en una sola',
               )

    selectedOption = selectOption(options, headers)

    if selectedOption == 0:
        return
    if selectedOption == 1:
        mergeTables()
    else:
        print('Tu selección no está implementada todavía')


def selectOption(options: (list, tuple), headers: (list, tuple)) -> int:
    """
    Función genérica para seleccionar una opción
    args
    options: strings que permiten identicar las opciones
    headers: : strings que explican las opciones
    """
    while True:
        for header in headers:
            print(header)
        extendedOptions = [MSG_NO_OPTION] + list(options)

        for i, option in enumerate(extendedOptions):
            print('{:d}.- {}'.format(i, option))
        selection = input(MSGWRITE1OPTION)
        try:
            selection = int(selection)
        except ValueError:
            print(MSG_NO_VALID_OPTION)
            continue
        if selection < 0 or selection > len(extendedOptions):
            print(MSG_NO_VALID_OPTION)
            continue
        else:
            return selection

def pathFromXML(element: xmlElement, sPath: str) -> str:
    """
    devuelve el nombre del directorio en el elemento xml element/text
    si el directorio no existe lanza una exception
    args:
        element: xml.etree.ElementTree.element
        sPath: nombre de un subelemento en element con el nombre de un direct.
    returns
        nombre del directorio
    """
    from os.path import isdir
    path = element.find(sPath).text.strip()
    if not isdir(path):
        raise ValueError('{} no existe'.format(sPath))
    return path


def filterColumns(columns: OrderedDict,
                  columnsNoCopy: list) -> OrderedDict:
    """
    copia las columnas en columns a un nuevo OrderedDict con la condición
        que la key no esté en columnsNoCopy
    """
    newColumns = [(k, v) for k, v in columns.items() if k not in columnsNoCopy]
    return OrderedDict(newColumns)


def createTableIfNotExists(element: xmlElement) -> str:
    """
    crea una tabla if not exists a partir de la información del elemento
        weatherStationsInIdee
    """
    import os.path

    path = pathFromXML(element, 'path')
    db = element.find('db').text.strip()
    db = os.path.join(path, db)

    columns = tableDefinitionGet(element)

    columnsNoCopy = [element1.text.strip()
                     for element1 in element.findall('columnNoCopy')]

    columns = filterColumns(columns, columnsNoCopy)

    columnDefinitions = [f'{k} {v}' for k, v in columns.items()]
    columnDefinitions = ','.join(columnDefinitions)

    primaryKeyColumns = [element1.text.strip() for element1 in
                         element.findall('primaryKeyColumn')]
    primaryKeyColumns = [columnName for columnName in primaryKeyColumns if \
                         columnName in columns.keys()]

    tableNew = element.find('tableNew').text.strip()

    if primaryKeyColumns:
        primaryKeyColumns = ','.join(primaryKeyColumns)
        stm1 = f'CREATE TABLE IF NOT EXISTS {tableNew} '+\
               f'({columnDefinitions}, '+\
               f'PRIMARY KEY({primaryKeyColumns}));'
    else:
        stm1 = f'CREATE TABLE IF NOT EXISTS {tableNew} ({columnDefinitions});'

    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.executescript(stm1)
    con.close()
    return stm1


def tableDefinitionGet(element: xmlElement, table: str = None) -> OrderedDict:
    """
    Crea un dicccionario en que las keys son los nombres de los campos
        y el valor su tipo
    """
    import os.path

    path = pathFromXML(element, 'path')
    db = element.find('db').text.strip()
    db = os.path.join(path, db)
    if table is None:
        table = element.find('table').text.strip()

    con = sqlite3.connect(db)
    cur = con.cursor()
    stm1 = f'PRAGMA TABLE_INFO({table});'
    cur.execute(stm1)
    columns = cur.fetchall()
    con.close()
    columns = [(column1[1], column1[2]) for column1 in columns]
    return OrderedDict(columns)


def insertIfNotExists(element):
    """
    inserta el contenido de la tabla sourceTable en la table destinationTable
        sujeto a los datos de las tablas de aemet que quiero combinar
    """
    import os.path

    path = pathFromXML(element, 'path')
    db = element.find('db').text.strip()
    db = os.path.join(path, db)
    originTables = [element1.text.strip()
                    for element1 in element.findall('table')]
    destinationTable = element.find('tableNew').text.strip()
    columns = tableDefinitionGet(element, destinationTable)
    columnNames = ','.join(columns.keys())
    writeScript = bool(element.find('writeScript').text.strip())

    if writeScript:
       f = open(os.path.join(path, FILE_INSERT_IF_NOT_EXISTS), 'w')

    for table in originTables:
        print(table)
        con = sqlite3.connect(db)
        cur = con.cursor()
        cur.execute(f'select {columnNames} from {table}')
        rows = [row for row in cur.fetchall()]
        con.close()
        stm1 = f'insert or ignore into {destinationTable} ({columnNames}) values '

        con = sqlite3.connect(db)
        cur = con.cursor()
        for row in rows:
            stm2 = stm1 + f'{tuple(row)}'
            try:
                cur.execute(stm2)
            except:
                logging.error(f'{stm2}')
                continue
            if writeScript:
                f.write(stm2 + '\n')

        con.commit()
        con.close()

    if writeScript:
        print(f'Se ha escrito el fichero {f.name}')
        f.close()


def mergeTables():
    """
    Crea una unica tabla con todas las estaciones de aemet en idee
    En idee.es aemet tiene clasificadas las estaciones en 4 shapefiles, de
        modo que la misma estación puede estar en varios shapefiles. Se
        pretende crear un fichero único sin estaciones repetidas
    """

    import xml.etree.ElementTree as ET
    tree = ET.parse(FILEPARAM)
    root = tree.getroot()
    element = root.find('weatherStationsInIdee')

    createTableIfNotExists(element)

    insertIfNotExists(element)
