
class Plan():

    _id:int
    _nombre:str
    _costo:int
    _descripcion:str
    _idPersona:int

    def __init__(self,id, nombre,costo,descricion,id_persona):
        self._id = id
        self._nombre = nombre
        self._costo = costo
        self._descripcion = descricion
        self._idPersona =id_persona

    def getNombre(self):
        return self._nombre

    def getID(self):
        return self._id

    def getIdpersona(self):
        return self._idPersona

    def getCosto(self):
        return self._costo

    def getDescripcion(self):
        return self._descripcion

    def setNombre(self,nombre):
        self._nombre = nombre

    def setCosto(self,costo):
        self._costo =costo

    def setDescripcion(self,descripcion):
        self._descripcion = descripcion