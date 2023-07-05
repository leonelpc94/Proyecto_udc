from werkzeug.security import check_password_hash

class Usuario():

    _ID:int
    _nombre: str
    _clave:str
    _email: str
    _telefono: int


    def __init__(self,ID, nombre, clave, email,telefono):
        self._ID = ID
        self._nombre = nombre
        self._clave = clave
        self._email = email
        self._telefono = telefono

    @classmethod
    def verificacion_clave(self, cifrado_clave, clave):
        return check_password_hash(cifrado_clave,clave)


    def setNombre(self,nombre):
        self._nombre = nombre

    def setEmail(self,email):
        self._email = email

    def setTelefono(self,telefono):
        self._telefono = telefono

    def getClave(self):
        return self._clave

    def getNombre(self):
        return self._nombre

    def getID(self):
        return self._ID

    def getEmail(self):
        return self._email

    def getTelefono(self):
        return self._telefono