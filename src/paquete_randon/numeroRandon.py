import random
from src.paquete_persona.personaClases import Usuario

class Numero():

    _numero:str
    _instencia = None
    _usuario = None
    _code:str

    def __new__(cls):
        if Numero._instencia is None:
            Numero._instencia = object.__new__(cls)
        return Numero._instencia


    def getUsuario(self):
        return self._usuario

    def setUser(self,id,nombre,clave, email, telefono):
        self._usuario = Usuario(id,nombre,clave,email,telefono)
    def randon(self):
        self._numero = str(random.randint(1000, 9999))
        return self._numero

    def getNumero(self):
        return self._numero

    def getCode(self):
        return self._code

    def setCode(self,code):
        self._code = code
