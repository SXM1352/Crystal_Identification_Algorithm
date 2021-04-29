import cython
cimport numpy as np
import numpy as np
from libc.math cimport round

cdef class Positioning:
    """
    Provides functionalities to determine the relation of pixels and dies.
    Remark: Here, pixels and channels are synonyms.
    """
    def __cinit__(self):
        pass

    cdef int C_posIndextoCol(self, int posIndexPixel):
        return posIndexPixel % 12 + 1

    def posIndextoCol(self, posIndexPixel):
        """
        Calculates the column of the given pixel.

        @param posIndexPixel: number of pixel
        @type posIndexPixel:  number
        @return: column of the pixel
        @rtype: int
        """
        return self.C_posIndextoCol(posIndexPixel)

    cdef int C_posIndextoRow(self, int posIndexPixel):
        return posIndexPixel / 12 + 1

    def posIndextoRow(self, posIndexPixel):
        """
        Calculates the row of the given pixel.

        @param posIndexPixel: number of pixel
        @type posIndexPixel: number
        @return: row of pixel
        @rtype: int
        """
        return self.C_posIndextoRow(posIndexPixel)

    cdef float C_posIndexPixeltoDie(self, int posIndexPixel):
        cdef double mainDieCol = round(self.C_posIndextoCol(posIndexPixel)/2.)
        cdef double mainDieRow = round(self.C_posIndextoRow(posIndexPixel)/2.)
        cdef double die = mainDieCol + 6*mainDieRow - 7
        return die

    def posIndexPixeltoDie(self, posIndexPixel):
        """
        Caluclates the die number of the given pixel.

        @param posIndexPixel: number of pixel
        @type posIndexPixel:  number
        @return: number of die
        @rtype: float
        """
        return self.C_posIndexPixeltoDie(int(posIndexPixel))

    def allPosIndexPixelofDie(self, int posIndexDie):
        """
        Calculates all numbers of the pixels in a given die.

        @param posIndexDie: number of die
        @type posIndePixel: int
        @return: pixels in the given die
        @rtype: python list, len = 4
        """
        pixels = []
        pixels.append(0 + 2 * posIndexDie) #first pixel - index 0...
        pixels.append(1 + 2 * posIndexDie)
        pixels.append(8 + 2 * posIndexDie)
        pixels.append(9 + 2 * posIndexDie)
        if posIndexDie >3:
            for i in range(0,4):
                pixels[i]+=8
        if posIndexDie >7:
            for i in range(0,4):
                pixels[i]+=8
        if posIndexDie >11:
            for i in range(0,4):
                pixels[i]+=8
        return pixels

    def pixsAreNeighbors(self, int posIndexPixel1, int posIndexPixel2):
        """
        Checks if the given pixels are neighbors.

        @param posIndexPixel1: number of pixel 1
        @type posIndexPixel1: number
        @param posIndexPixel2: number of pixel 2
        @type posIndexPixel2: number
        @return: True/False
        @rtype: bool
        """
        if posIndexPixel1 == posIndexPixel2:
            return False
        if abs(self.C_posIndextoCol(posIndexPixel1) - self.C_posIndextoCol(posIndexPixel2)) <= 1 and abs(self.C_posIndextoRow(posIndexPixel1) - self.C_posIndextoRow(posIndexPixel2)) <= 1:
            return True
        else:
            return False

    cdef bint C_pixsAreDirectNeighbors(self, int posIndexPixel1, int posIndexPixel2):
        cdef int colPix1 = self.C_posIndextoCol(posIndexPixel1)
        cdef int rowPix1 = self.C_posIndextoRow(posIndexPixel1)
        cdef int colPix2 = self.C_posIndextoCol(posIndexPixel2)
        cdef int rowPix2 = self.C_posIndextoRow(posIndexPixel2)
        if posIndexPixel1 == posIndexPixel2:
            return False
        else:
            if abs(colPix1 - colPix2) == 1 and rowPix1 == rowPix2:
                return True
            elif colPix1 == colPix2 and abs(rowPix1 - rowPix2) == 1:
                return True
            else:
                return False

    def pixsAreDirectNeighbors(self, posIndexPixel1, posIndexPixel2):
        """
        Checks if given pixels are direct neighbors.
        @param posIndexPixel1: number of pixel 1
        @type posIndexPixel1: number
        @param posIndexPixel2: number of pixel 2
        @type posIndexPixel2: number
        @return: True/False
        @rtype: bool
        """
        return self.C_pixsAreDirectNeighbors(int(posIndexPixel1), int(posIndexPixel2))

    cdef bint C_pixsAreDiagonalNeighbors(self, int pixel1, int pixel2):
        if pixel1 == pixel2:
            return False
        elif abs(self.C_posIndextoCol(pixel1) - self.C_posIndextoCol(pixel2)) == 1 and abs(self.C_posIndextoRow(pixel1) - self.C_posIndextoRow(pixel2)) == 1:
            return True
        else:
            return False

    def pixsAreDiagonalNeighbors(self, posIndexPixel1, posIndexPixel2):
        """
        Checks if pixels are diagonal neighbors.

        @param posIndexPixel1: number of pixel 1
        @type posIndexPixel1: number
        @param posIndexPixel2: number of pixel 2
        @type posIndexPixel2: number
        @return: True/False
        @rtype: bool
        """
        return self.C_pixsAreDiagonalNeighbors(int(posIndexPixel1), int(posIndexPixel2))

    cdef bint C_diesAreNeighbors(self, int posIndexDie1, int posIndexDie2):
        if posIndexDie1 == posIndexDie2:
            return False
        cdef int col1 = posIndexDie1 % 4
        cdef int row1 = posIndexDie1 / 4
        cdef int col2 = posIndexDie2 % 4
        cdef int row2 = posIndexDie2 / 4
        if abs(col1 - col2) <= 1 and abs(row1 - row2) <= 1:
            return True
        else:
            return False

    def diesAreNeighbors(self, posIndexDie1, posIndexDie2):
        """
        Checks if dies are neighbors.

        @param posIndexDie1: number of die 1
        @type posIndexDie1: number
        @param posIndexDie2: number if die 2
        @type posIndexDie2: number
        @return: True/False
        @rtype: bool
        """
        return self.C_diesAreNeighbors(int(posIndexDie1), int(posIndexDie2))

    def diesAreDirectNeighbors(self, int posIndexDie1, int posIndexDie2):
        if posIndexDie1 == posIndexDie2:
            return False
        cdef int col1 = posIndexDie1 % 4
        cdef int row1 = posIndexDie1 / 4
        cdef int col2 = posIndexDie2 % 4
        cdef int row2 = posIndexDie2 / 4
        if abs(col1-col2)==1 and abs(row1-row2) == 0:
            return True
        elif abs(col1 - col2) == 0 and abs(row1 - row2) == 1:
            return True
        else:
            return False

    def diesAreDiagonalNeighbors(self, int posIndexDie1, int posIndexDie2):
        if posIndexDie1 == posIndexDie2:
            return False
        cdef int col1 = posIndexDie1 % 4
        cdef int row1 = posIndexDie1 / 4
        cdef int col2 = posIndexDie2 % 4
        cdef int row2 = posIndexDie2 / 4
        if abs(col1 - col2) == 1 and abs(row1 - row2) == 1:
            return True
        else:
            return False

class PositioningVal(Positioning):
    """
    Provides functions to calculate the physical position of pixels.
    Remark: Here pixels and channels are synonyms.
    """
    cython.declare(pos_xy = np.ndarray, _tile_length = cython.float, _pix_size = cython.float)

    def __init__(self):
        self._tile_length= 32.6
        self._pix_size= self._tile_length/8.
        self.pos_xy = np.empty([64,2])

    def posIndexPixelto_xy(self):
        """
        Calculates a LUT of all pixel positions and saves to class' public pos_xy variable.

        @return: None
        @rtype:
        """
        cdef int i
        for i in range(0,64):
            self.pos_xy[i][0]= -self._tile_length/2 + self._pix_size/2 + (self.posIndextoCol(i)-1)*self._pix_size
            self.pos_xy[i][1]= -self._tile_length/2 + self._pix_size/2 + (self.posIndextoRow(i)-1)*self._pix_size

    def posIndexPixelto_x(self, pixel):
        """
        Calculates the x position of a given pixel.

        @param pixel: number of pixel
        @type pixel: number
        @return: x-coordinate on tile
        @rtype: float
        """
        return -self._tile_length/2 + self._pix_size/2 + (self.posIndextoCol(pixel)-1)*self._pix_size

    def posIndexPixelto_y(self, pixel):
        """
        Calculates the y position of a given pixel.

        @param pixel: number of pixel
        @type pixel: number
        @return: y coordinate of pixel
        @rtype: float
        """
        return -self._tile_length/2 + self._pix_size/2 + (self.posIndextoRow(pixel)-1)*self._pix_size



