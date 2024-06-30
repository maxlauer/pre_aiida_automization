interface = """INTERFACE = F
NRIGHTHO= 10    NLBASIS= 1
NLEFTHOS= 10    NRBASIS= 1
LEFTASIS    X         Y         Z       REFPOT
        0.500000  0.500000  0.500000      1
RIGHTBASIS
        0.500000  0.500000  0.500000      1"""

zperiodl = """ZPERIODL= 0.50000000   0.50000000  -0.50000000
ZPERIODR= 0.50000000   0.50000000   0.50000000"""

linpol = """LINIPOL= f      LRHOSYM= f    LCOMPLEX= f
Center of inversion :      NZ=1     LCENTER= t
 LOGINV= f      INIPOL= 0     IXIPOL= 0
 CENTROFIN=   0.0     0.0     0.0"""

mmin = """MMIN= 1    MMAX=6
SRINOUT=   0   0   0  00"""

decimation = """This is used for decimation, put vacuum in the file to have vacuum
DECIFILES
codeci.fp1                              left (up) host
codeci.fp2                              right (down) host"""

ewald = """Parameters for ewald sums
RMAX=7.0d       GMAX=65.0d0     (fcc 7  65)"""