# 用来识别验证码

#import pytesseract
from PIL import ImageEnhance
from PIL import Image

import numpy as np

def CodeRecognizer(img):
    return HardCoder(img).img_string()

class Coder:
    def __init__(self, img):
        self.__img = img
        pass

    def img_string(self):
        return self._process()

    def _process(self):
        pass

    @property
    def img(self):
        return self.__img

class OcrCoder(Coder):
    def __init__(self, img):
        super(self)

    def _process(self):
        import pytesseract
        return pytesseract.image_to_string(self.__img, lang="eng")

class HardCoder(Coder):
    def __init__(self, img):
        # Get the codes image array, from 1 to 10
        self.__codes = [np.asarray(Image.open("codes/%s.png" % i), dtype=np.int8) for i in range(0, 10)]

        # The strong features, to match the code by counting the zeros every column. Numbers' horizational shift.
        self.__zeros = [[np.count_nonzero(self.__codes[i][j]) for j in range(17)] for i in range(10)]

        super(HardCoder, self).__init__(img)
    
    def _process(self):
        img = np.asarray([np.count_nonzero(np.asarray(self.img, dtype=np.int8)[j]) for j in range(17)])
        # Count difference with training dataset number image
        diffs = np.zeros((10, 1))
        for n, z in enumerate(self.__zeros):
            diffs[n] = np.abs(img - z).sum()
        
        # Return the least loss result
        return str(np.argmin(diffs))
