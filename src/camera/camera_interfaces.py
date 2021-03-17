from abc import ABC, abstractmethod

class ICamera(ABC):
    @abstractmethod
    def take_photo(self):
        pass

class ICameraObserver(ABC):
    #will be called once new photo is taken
    #this is entry point for the ML team
    #TODO: transport OpenCV image here
    @abstractmethod
    def update(self, reason) -> None:
        pass

class ICameraObservable(ABC):
    #register yourself for new photo updates
    #your class should inherit from ICameraObserver 
    @abstractmethod
    def register(self, observer: ICameraObserver) -> None:
        pass

    #unregister yourself from updates
    @abstractmethod
    def unregister(self, observer: ICameraObserver) -> None:
        pass

    @abstractmethod
    def notify(self) -> None:
        pass



