from abc import ABC, abstractmethod
from fastapi import UploadFile
import numpy as np

class IPredictService(ABC):
    @abstractmethod
    def calculate_drift(self, image_numpy: np.ndarray, mask_numpy=None):
        pass
    
    @abstractmethod
    def extract_image_features(self, image_numpy: np.ndarray, mask_numpy=None):
        pass

