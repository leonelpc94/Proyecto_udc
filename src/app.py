from paquete_randon.numeroRandon import Numero
from flask import Flask,render_template,request,redirect,url_for,session,make_response,flash
from werkzeug.security import generate_password_hash
from flask_mail import Mail,Message
from decouple import config
from paquete_db.DBClases import BaseDato
import json
import os

app = Flask(__name__)
app.secret_key = 'holamundo'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = config('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = config('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

_DB = BaseDato()
code = Numero()
_mail = Mail(app)

@app.route('/')
def index():
    lista1 = _DB.todoPlanes()
    if 'usuario' in session:
        lista = []
        jPersona = session['usuario']
        objeto_persona = json.loads(jPersona)
        for index in lista1:
            if objeto_persona['_ID'] != index.getIdpersona():
                lista.append(index)
        return render_template('planes.html', lista=lista, login=True, persona=objeto_persona,boton = 'menu')
    return render_template('planes.html', lista=lista1, login=False,boton = 'menu')

@app.route('/registroPersona/<verificar>',methods=['GET','POST'])
def registroPersona(verificar):
    if verificar == 'mail':
        return render_template('email.html', login=False)
    elif verificar == 'code':
        mail = request.form['email']
        verificar = _DB.listaUsuario(mail)
        if verificar == []:
            msg = Message(code.randon(), sender=config('MAIL_USERNAME'), recipients=[mail])
            msg.body = 'ingerse el codigo en la aplicacion para verificar el registro'
            _mail.send(msg)
            response = make_response(render_template('code.html', login=False, ruta = 'registroPersona'))
            response.set_cookie('mail', mail)
            return response
        else:
            return 'correo registrado'
    if verificar == 'verificar':
        code.setCode(request.form['code'])
        if code.getCode() == code.getNumero():
            return render_template('registro.html', login=False)
        else:
            return render_template('email.html', login=False)
    if verificar == 'registro':
        try:
            if code.getCode() == code.getNumero():
                file = request.files['archivo']
                nombre = request.form['nombre']
                clave = generate_password_hash(request.form['clave'])
                email = request.cookies.get('mail')
                telefono = int(request.form['telefono'])
                usuario = _DB.registroPersona(nombre, clave, email, telefono)
                if usuario != []:
                    basep = os.path.dirname(__file__)
                    nuevoNombreFile = str(usuario.getID()) + '.jpg'
                    upload_path = os.path.join(basep, 'static/img/perfiles', nuevoNombreFile)
                    file.save(upload_path)
                    session['usuario'] = json.dumps(usuario.__dict__)
                    return redirect('/')
                else:
                    return render_template('registro.html', login=False)
        except Exception:
            return render_template('registro.html', login=False)

@app.route('/publicacion/<idp>/<id>',methods=['GET','POST'])
def publicacion(idp,id):
    if 'usuario' in session:
        jPersona = session['usuario']
        objeto_persona = json.loads(jPersona)
        verdedor = _DB.correoPersona(int(idp))
        plan = _DB.datosPlan(id)
        msg1 = Message('Peticion de plan', sender=config('MAIL_USERNAME'), recipients=[verdedor[0][3]])
        msg1.body = 'El cliente {} desea una contratar el plan {}, con un costo de {} y ofrece: {}, correo: {} y telefono: {}'.format(
            objeto_persona['_nombre'],plan[0][1],plan[0][2],plan[0][3],objeto_persona['_email'], objeto_persona['_telefono']
        )
        msg2 = Message('notificacion al vendedor', sender=config('MAIL_USERNAME'), recipients=[objeto_persona['_email']])
        msg2.body = 'El vendedor {} fue notificado de su pedido, telefono: {} y correo: {}'.format(
            verdedor[0][1],verdedor[0][4],verdedor[0][3]
        )
        _mail.send(msg2)
        _mail.send(msg1)
        flash('El mensaje fue enviado con exito')
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/formulario',methods = ['GET','POST'])
def plan():
    if 'usuario' in session:
        if request.method == 'POST':
            try:
                file = request.files['archivo']
                nombre = request.form['nombre']
                costo = int(request.form['costo'])
                descripcion = request.form['descipcion']
                usuario = session['usuario']
                objeto_persona = json.loads(usuario)
                plan = _DB.registroPlan(nombre, costo, descripcion, objeto_persona['_ID'])
                if plan:
                    basep = os.path.dirname(__file__)
                    nuevoNombreFile = nombre + '.jpg'
                    upload_path = os.path.join(basep, 'static/img/planes', nuevoNombreFile)
                    file.save(upload_path)
                    flash('El plan se guardo con exito')
                    redirect(url_for('plan'))
                else:
                    flash('Error en los datos')
                    redirect(url_for('plan'))
            except Exception:
                flash('Error en los datos')
                return redirect(url_for('plan'))
        else:
            usuario = session['usuario']
            objeto_persona = json.loads(usuario)
            return render_template('registroPlan.html',persona = objeto_persona, login = True)
    return redirect('/')

@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            clave = request.form['clave']
            usuario = _DB.login(email, clave)
            if usuario != []:
                session['usuario'] = json.dumps(usuario.__dict__)
                return redirect('/')
            else:
                flash('usuario o contraseña incorrecto')
                return redirect(url_for('login'))
        except Exception:
            flash('Error en los datos')
            return redirect(url_for('login'))
    else:
        return render_template('login.html',login = False)

#ruta protegida
@app.route('/fin')
def cerrar():
    #proteger ruta
    if 'usuario' in session:
        session.clear()
        return redirect(url_for('index'))
    return redirect('/')

@app.route('/lista')
def listaPlanes():
    if 'usuario' in session:
        jPersona = session['usuario']
        #loads sirbe para convertir un strin gen json
        objeto_persona = json.loads(jPersona)
        lista = _DB.listaPlanes(objeto_persona['_ID'])
        return render_template('planes.html',lista = lista,persona = objeto_persona,login = True, boton = 'lista')
    return redirect('/')

@app.route('/e_plan/<name>')
def eliminarPlan(name):
    if 'usuario' in session:
        plan = _DB.datosPlan(name)
        _DB.eliminarPlan(name)
        basep = os.path.dirname(__file__)
        nuevoNombreFile = plan[0][1] + '.jpg'
        upload_path = os.path.join(basep, 'static/img/planes', nuevoNombreFile)
        os.remove(upload_path)
        return redirect(url_for('listaPlanes'))
    return redirect('/')

@app.route('/e_persona',methods = ['GET','POST'])
def eliminarPersona():
    if 'usuario' in session:
        jPersona = session['usuario']
        objeto_persona = json.loads(jPersona)
        if request.method == 'POST':
            if _DB.eliminarUsuario(objeto_persona['_ID'],request.form['clave'],objeto_persona['_clave']):
                session.pop('usuario')
                basep = os.path.dirname(__file__)
                nuevoNombreFile = str(objeto_persona['_ID']) + '.jpg'
                upload_path = os.path.join(basep, 'static/img/perfiles', nuevoNombreFile)
                os.remove(upload_path)
                return redirect(url_for('index'))
            else:
                flash('No se pudo eliminar')
                return redirect(url_for('eliminarPersona'))
        return render_template('eliminarCuenta.html')
    return redirect('/')

@app.route('/deseados/<id>')
def agregarDeseados(id):
    if 'usuario' in session:
        jPersona = session['usuario']
        objeto_persona = json.loads(jPersona)
        _DB.listaDeseados(objeto_persona['_ID'],id)
        return redirect('/')
    return redirect('/login')

@app.route('/favoritos')
def favoritos():
    if 'usuario' in session:
        jPersona = session['usuario']
        objeto_persona = json.loads(jPersona)
        lista = _DB.favoritos(objeto_persona['_ID'])
        #print(lista)
        return render_template('planes.html',lista = lista,persona = objeto_persona, login = True, boton = 'favoritos')
    return redirect('/')

@app.route('/quitar/<id>')
def quitar(id):
    if 'usuario' in session:
        _DB.quitarPlanFavorito(id)
        return redirect(url_for('favoritos'))
    return redirect('/')

@app.route('/actualizar',methods = ['GET','POST'])
def actualizarDatos():
    if 'usuario' in session:
        jPersona = session['usuario']
        objeto_persona = json.loads(jPersona)
        if request.method == 'POST':
            try:
                objPersona = _DB.actualizar(objeto_persona['_ID'],request.form['nombre'],
                                             objeto_persona['_email'],int(request.form['telefono']))
                if objPersona != []:
                    session['usuario'] = json.dumps(objPersona.__dict__)
                    objeto_persona = json.loads(session['usuario'])
                    file = request.files['archivo']
                    basep = os.path.dirname(__file__)
                    nuevoNombreFile = str(objeto_persona['_ID']) + '.jpg'
                    upload_path = os.path.join(basep, 'static/img/perfiles', nuevoNombreFile)
                    file.save(upload_path)
                    flash('Datos actualizados')
                    return redirect(url_for('actualizarDatos'))
                else:
                    flash('Error de actualizacion')
                    return redirect(url_for('actualizarDatos'))
            except Exception:
                flash('Error en los datos')
                return redirect(url_for('actualizarDatos'))
        else:
            return render_template('actualizar.html',persona =objeto_persona,login = True)
    return redirect(url_for('login'))

@app.route('/editarPlan/<id>',methods = ['GET','POST'])
def editarPlan(id):
    if 'usuario' in session:
        jPersona = session['usuario']
        objeto_persona = json.loads(jPersona)
        if request.method == 'POST':
            plan = _DB.editarPlan(id,request.form['nombre'],request.form['costo'],request.form['descipcion'])
            if plan:
                return redirect(url_for('listaPlanes'))
            else:
                flash('Error en los datos')
                return redirect(url_for('editarPlan'))
        else:
            consultaPlan = _DB.consultaPlan(id)
            return render_template('editarPlan.html',plan=consultaPlan,persona =objeto_persona, login = True)
    return redirect(url_for('login'))

@app.route('/actualizarClave',methods =['GET','POST'])
def actualizarClave():
    if 'usuario' in session:
        jPersona = session['usuario']
        objeto_persona = json.loads(jPersona)
        if request.method == 'POST':
            claveNueva = generate_password_hash(request.form['claveNueva'])
            if _DB.canbioClave(claveNueva,objeto_persona['_clave'],request.form['clave'],objeto_persona['_ID']):
                flash('La contraseña fue actualizada con exito')
                return redirect(url_for('actualizarDatos'))
            flash('Error al guadar datos')
            return redirect(url_for('ctualizarClave'))
        return render_template('cambioClave.html',persona =objeto_persona, login = True)
    return redirect(url_for('login'))

if __name__ == '__main__':
    _mail.init_app(app)
    app.run(port=8080, debug =True)