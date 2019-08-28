# aemetDev
Some utility programs related with aemet data.

Different options can be managed editing aemetDev.xml; the name of the elements have a self-explained name.

merge tables. Merge aemet's weather stations (wst) downloaded from idee https://www.miteco.gob.es/es/cartografia-y-sig/ide/descargas/otros/default.aspx. Each file has repeated wst with different gid column. Firstly I export previously downloaded shapefiles to a sqlitedb; then I merge the tables to a new one with not repeated wst.


