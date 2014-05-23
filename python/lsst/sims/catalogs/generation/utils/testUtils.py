import sqlite3
from numpy.random import random, seed
from sqlite3 import dbapi2 as sqlite
import numpy

from lsst.sims.catalogs.generation.db import DBObject, ObservationMetaData

def writeResult(result, fname):
    fh = open(fname, 'w')
    first = True
    for chunk in result:
        if first:
            fh.write(",".join([str(el) for el in chunk.dtype.names])+"\n")
            first = False
        for i in xrange(len(chunk)):
            fh.write(",".join([str(chunk[name][i]) for name in chunk.dtype.names])+"\n")
    fh.close()

def sampleSphere(size):
    #From Shao 1996: "Spherical Sampling by Archimedes' Theorem"
    ra = random(size)*2.*numpy.pi
    z = random(size)*2. - 1.
    dec = numpy.arccos(z) - numpy.pi/2.
    return ra, dec


class myTestGals(DBObject):
    objid = 'testgals'
    tableid = 'galaxies'
    idColKey = 'id'
    #Make this implausibly large?  
    appendint = 1022
    dbAddress = 'sqlite:///testDatabase.db'
    raColName = 'ra'
    decColName = 'decl'
    spatialModel = 'SERSIC2D'
    columns = [('id', None, int),
               ('raJ2000', 'ra*%f'%(numpy.pi/180.)),
               ('decJ2000', 'decl*%f'%(numpy.pi/180.)),
               ('umag', None),
               ('gmag', None),
               ('rmag', None),
               ('imag', None),
               ('zmag', None),
               ('ymag', None),
               ('mag_norm_agn', None),
               ('mag_norm_disk', None),
               ('mag_norm_bulge', None),
               ('redshift', None),
               ('a_disk', None),
               ('b_disk', None),
               ('a_bulge', None),
               ('b_bulge', None),]

def makeGalTestDB(size=1000, seedVal=None):
    """
    Make a test database to serve information to the myTestStars objec
    @param size: Number of rows in the database
    @param seedVal: Random seed to use
    """
    conn = sqlite3.connect('testDatabase.db')
    c = conn.cursor()
    try:
        c.execute('''CREATE TABLE galaxies
                     (id int, ra real, decl real, umag real, gmag real, rmag real, 
                     imag real, zmag real, ymag real, 
                     mag_norm_agn real, mag_norm_bulge real, mag_norm_disk real,
                     redshift real, a_disk real, b_disk real, a_bulge real, b_bulge real)''')
        conn.commit()
    except:
        raise RuntimeError("Error creating database.")
    if seedVal:
        seed(seedVal)
    ra, dec = sampleSphere(size)
    #Typical colors for main sequece stars
    umg = 1.5
    gmr = 0.65
    rmi = 1.0
    imz = 0.45
    zmy = 0.3
    mag_norm_disk = random(size)*6. + 18.
    mag_norm_bulge = random(size)*6. + 18.
    mag_norm_agn = random(size)*6. + 19.
    redshift = random(size)*3.

    a_disk = random(size)*2.
    flatness = random(size)*0.8 # To prevent linear galaxies
    b_disk = a_disk*(1 - flatness)

    a_bulge = random(size)*1.5
    flatness = random(size)*0.5
    b_bulge = a_bulge*(1 - flatness)

    #assume mag norm is g-band (which is close to true)
    mag_norm = -2.5*numpy.log10(numpy.power(10, mag_norm_disk/-2.5) + numpy.power(10, mag_norm_bulge/-2.5) +
                                numpy.power(10, mag_norm_agn/-2.5))
    umag = mag_norm + umg
    gmag = mag_norm
    rmag = gmag - gmr
    imag = rmag - rmi
    zmag = imag - imz
    ymag = zmag - zmy
    for i in xrange(size):
        c.execute('''INSERT INTO galaxies VALUES (%i, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f)'''%\
                  (i, numpy.degrees(ra[i]), numpy.degrees(dec[i]), umag[i], gmag[i], rmag[i], imag[i],
                   zmag[i], ymag[i], mag_norm_agn[i], mag_norm_bulge[i], mag_norm_disk[i], redshift[i], 
                   a_disk[i], b_disk[i], a_bulge[i], a_bulge[i]))
    c.execute('''CREATE INDEX gal_ra_idx ON galaxies (ra)''')
    c.execute('''CREATE INDEX gal_dec_idx ON galaxies (decl)''')
    conn.commit()
    conn.close()

class myTestStars(DBObject):
    objid = 'teststars'
    tableid = 'stars'
    idColKey = 'id'
    #Make this implausibly large?  
    appendint = 1023
    dbAddress = 'sqlite:///testDatabase.db'
    raColName = 'ra'
    decColName = 'decl'
    spatialModel = 'POINT'
    columns = [('id', None, int),
               ('raJ2000', 'ra*%f'%(numpy.pi/180.)),
               ('decJ2000', 'decl*%f'%(numpy.pi/180.)),
               ('umag', None),
               ('gmag', None),
               ('rmag', None),
               ('imag', None),
               ('zmag', None),
               ('ymag', None),
               ('mag_norm', None)]

def makeStarTestDB(size=1000, seedVal=None):
    """
    Make a test database to serve information to the myTestStars objec
    @param size: Number of rows in the database
    @param seedVal: Random seed to use
    """
    conn = sqlite3.connect('testDatabase.db')
    c = conn.cursor()
    try:
        c.execute('''CREATE TABLE stars
                     (id int, ra real, decl real, umag real, gmag real, rmag real, 
                     imag real, zmag real, ymag real, mag_norm real)''')
        conn.commit()
    except:
        raise RuntimeError("Error creating database.")
    if seedVal:
        seed(seedVal)
    ra, dec = sampleSphere(size)
    #Typical colors
    umg = 1.5
    gmr = 0.65
    rmi = 1.0
    imz = 0.45
    zmy = 0.3
    mag_norm = random(size)*6. + 18.
    #assume mag norm is g-band (which is close to true)
    umag = mag_norm + umg
    gmag = mag_norm
    rmag = gmag - gmr
    imag = rmag - rmi
    zmag = imag - imz
    ymag = zmag - zmy
    for i in xrange(size):
        c.execute('''INSERT INTO stars VALUES (%i, %f, %f, %f, %f, %f, %f, %f, %f, %f)'''%\
                  (i, numpy.degrees(ra[i]), numpy.degrees(dec[i]), umag[i], gmag[i], rmag[i], imag[i], zmag[i], ymag[i], mag_norm[i]))
    c.execute('''CREATE INDEX star_ra_idx ON stars (ra)''')
    c.execute('''CREATE INDEX star_dec_idx ON stars (decl)''')
    conn.commit()
    conn.close()
