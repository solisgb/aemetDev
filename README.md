# aemetDev
Some utility programs related with aemet data.

Different options can be managed editing aemetDev.xml; elements have a self-explained name.

merge tables. Merge aemet's weather stations (wst) from different files downloaded from idee https://www.miteco.gob.es/es/cartografia-y-sig/ide/descargas/otros/default.aspx; each file has repeated wst with different values in gid column. Firstly I export previously downloaded shapefiles to a sqlite db; then I merge the tables to a new one with not repeated wst -column named indicativo-.


