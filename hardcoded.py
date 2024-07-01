interface = """INTERFACE= F
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

constant_block = """  IRNUMX= 10    ITCCOR= 40    IPRCOR= 0    IFILE= 13      IPE= 0
     KWS= 2     KSHAPE= 0        IRM= 353      INS= 0     ICST= 2
  INSREF= 0       KCOR= 2      KVREL= 0     KEXCOR= 2
 KHYPERF= 0    KHFIELD= 0       KEFG= 0
     KTE= 1       KPRE= 0      KVMAD= 0   KSCOEF= 0
 IPOTOUT= 1  IGREENFUN= 0        ICC= 0   ISHIFT= 0
  HFIELD= 0.0   VCONST= 0.0d0  KFORCE=0"""