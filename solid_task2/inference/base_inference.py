from abc import ABC, abstractmethod
from typing import Any


class BaseInference(ABC):
    """
    Abstract base class for all inference engines.
    Any model (YOLO, future models) must follow this contract.
    """

    @abstractmethod
    def load_model(self) -> None:
        """Load the model into memory"""
        pass

    @abstractmethod
    def predict(self, input_source: Any) -> Any:
        """
        Run inference on input (image / video path)
        """
        pass
