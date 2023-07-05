import mariadb
from src.paquete_persona.personaClases import Usuario
from src.paquete_plan.planClases import Plan
from decouple import config
class BaseDato(object):

    _instencia =None
    _conexion = mariadb.connect(user=config('MYSQL_USER'),
                               password=config('MYSQL_PWD'),
                               host=config('MYSQL_HOST'),
                               port=int(config('MYSQL_TCP_PORT')),
                               database= config('MYSQL_DB'))

    def __new__(cls):
        if BaseDato._instencia is None:
            BaseDato._instencia = object.__new__(cls)
        return BaseDato._instencia

    def registroPersona(self,nombre,clave,email,telefono):
        try:
            cur = self._conexion.cursor()
            cur.execute('INSERT INTO persona (nombre, clave, email, telefono) VALUES (%s,%s,%s,%s)',
                        (nombre,clave,email,telefono))
            self._conexion.commit()
            cur.execute('SELECT id,nombre,clave,email,telefono FROM persona WHERE email = %s',
                        (email,))
            cliente = cur.fetchall()
            objeto_usuario = Usuario(cliente[0][0],nombre,clave,email,telefono)
            return objeto_usuario
        except mariadb.Error as e:
            print(e)
            return None

    def registroPlan(self, nombre,costo,descricion,usuario):
        try:
            self._conexion.cursor().execute('INSERT INTO plan (nombre,costo,descripcion,idpersona) VALUES(%s,%s,%s,%s)',
                                            (nombre,costo,descricion,usuario))
            self._conexion.commit()
            return True
        except mariadb.Error as e:
            return False

    def login(self,email,clave):
        try:
            cur =self._conexion.cursor()
            cur.execute('SELECT id,nombre,clave,email,telefono FROM persona WHERE email = %s',
                                                      (email,))
            cliente = cur.fetchall()
            if cliente != None:
                objeto_usuario = Usuario(cliente[0][0], cliente[0][1], cliente[0][2], cliente[0][3], cliente[0][4])
                if Usuario.verificacion_clave(cliente[0][2],clave):
                    return objeto_usuario
            else:
                return None
        except mariadb.Error as e:
            raise Exception(e)


    def listaPlanes(self,idPersona):
        listaPlan = []
        try:
            cur = self._conexion.cursor()
            cur.execute('SELECT id,nombre,costo,descripcion,idpersona FROM plan WHERE idpersona = %s',
                        (idPersona,))
            planes = cur.fetchall()
            for id, nombre, costo, descripcion, idPersona in planes:
                plan = Plan(id, nombre, costo, descripcion, idPersona)
                listaPlan.append(plan)
            return listaPlan
        except mariadb.Error as e:
            print(e)

    def consultaPlan(self,id):
        try:
            cur = self._conexion.cursor()
            cur.execute('SELECT id,nombre,costo,descripcion,idpersona FROM plan WHERE id = %s',
                        (id,))
            cliente = cur.fetchall()
            plan = Plan(id, cliente[0][1], cliente[0][2], cliente[0][3], cliente[0][4])
            return plan
        except mariadb.Error as e:
            print(e)

    def listaUsuario(self,email):
        try:
            cur = self._conexion.cursor()
            cur.execute('SELECT id,email FROM persona WHERE email = %s',
                        (email,))
            cliente = cur.fetchall()
            return cliente
        except mariadb.Error as e:
            print(e)


    def eliminarUsuario(self,id,clave,clavehash):
        if Usuario.verificacion_clave(clavehash,clave):
            try:
                cur = self._conexion.cursor()
                cur.execute('DELETE FROM persona WHERE id = %s',
                            (id,))
                cur.execute('DELETE FROM plan WHERE idpersona = %s',
                            (id,))
                self._conexion.commit()
                return True
            except mariadb.Error:
                return False
        return False

    def todoPlanes(self):
        try:
            listaPlan = []
            cur = self._conexion.cursor()
            cur.execute('SELECT * FROM plan')
            planes = cur.fetchall()
            for id, nombre, costo, descripcion, idPersona in planes:
                plan = Plan(id, nombre, costo, descripcion, idPersona)
                listaPlan.append(plan)
            return listaPlan
        except mariadb.Error:
            return None


    def eliminarPlan(self,id):
        try:
            cur = self._conexion.cursor()
            cur.execute('DELETE FROM plan WHERE id = %s',
                        (id,))
            self._conexion.commit()
        except mariadb.Error as e:
            print(e)

    def listaDeseados(self,idCliente, idPlan):
        try:
            cur = self._conexion.cursor()
            cur.execute('SELECT idplan,idpersona FROM deseados WHERE idplan = %s AND idpersona = %s',(idPlan,idCliente))
            idPlanes = cur.fetchall()
            if idPlanes == []:
                cur.execute('INSERT INTO deseados (idplan,idpersona)  VALUES (%s,%s)',
                            (idPlan,idCliente))
                self._conexion.commit()
            return True
        except mariadb.Error as e:
            print(e)
            return False

    def favoritos(self,idCiente):
        try:
            listaPlan = []
            cur = self._conexion.cursor()
            cur.execute('SELECT * FROM deseados WHERE idpersona = %s',(idCiente,))
            idPlanes = cur.fetchall()
            if idPlanes != []:
                for idplan, idpersona in idPlanes:
                    cur.execute('SELECT * FROM plan WHERE id = %s', (idplan,))
                    idplanes = cur.fetchall()
                    print(idplanes)
                    if idplanes != []:
                        plan = Plan(idplanes[0][0], idplanes[0][1], idplanes[0][2], idplanes[0][3], idplanes[0][4])
                        listaPlan.append(plan)
            return listaPlan
        except mariadb.Error:
            return None

    def quitarPlanFavorito(self,idPlan):
        try:
            cur = self._conexion.cursor()
            cur.execute('DELETE FROM deseados WHERE idplan = %s',(idPlan,))
            self._conexion.commit()
        except mariadb.Error as e:
            print(e)

    def actualizar(self,id,nombre,email,telefono):
        try:
            cur = self._conexion.cursor()
            cur.execute('UPDATE persona SET nombre = %s,telefono = %s WHERE id = %s',
                        (nombre,telefono,id))
            self._conexion.commit()
            cur.execute('SELECT * FROM persona WHERE id = %s', (id,))
            cliente = cur.fetchall()
            usuario = Usuario(id, cliente[0][1], cliente[0][2], email, cliente[0][4])
            return usuario
        except mariadb.Error as e:
            print(e)
            return None

    def editarPlan(self,id,nombre,costo,descripcion):
        try:
            cur = self._conexion.cursor()
            cur.execute('UPDATE plan SET nombre = %s, costo = %s,descripcion = %s WHERE id = %s',
                        (nombre,costo,descripcion,id))
            self._conexion.commit()
            return True
        except mariadb.Error as e:
            print(e)
            return False

    def correoPersona(self,id):
        try:
            cur = self._conexion.cursor()
            cur.execute('SELECT * FROM persona WHERE id = %s',(id,))
            cliente = cur.fetchall()
            return cliente
        except mariadb.Error as e:
            print(e)
            return None

    def datosPlan(self,id):
        try:
            cur = self._conexion.cursor()
            cur.execute('SELECT * FROM plan WHERE id = %s',(id,))
            cliente = cur.fetchall()
            return cliente
        except mariadb.Error as e:
            print(e)
            return None

    def canbioClave(self,claveNueva,clavehash,clave,id):
        if Usuario.verificacion_clave(clavehash,clave):
            try:
                cur = self._conexion.cursor()
                cur.execute('UPDATE persona SET clave = %s WHERE id = %s',(claveNueva,id,))
                self._conexion.commit()
                return True
            except mariadb.Error as e:
                print(e)
                return False
        return False
