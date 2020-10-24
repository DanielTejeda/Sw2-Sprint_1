from flask import Flask, request, render_template, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, IntegerField, FloatField, SelectField
from wtforms.validators import InputRequired, Email, Length, Optional
from werkzeug.security import generate_password_hash, check_password_hash
import views    

# initializations
app = Flask(__name__)
app.config['SECRET_KEY']='estoessecretoXD!'

Bootstrap(app)
# PostreSQL Connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/postgres'
#para q no mande alertas cuando hagamos modificaciones (opcional)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False 
# MySQL Connection
#app.config['MYSQL_HOST'] = 'localhost' 
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = 'password'
#app.config['MYSQL_DB'] = 'flaskcontacts' 
#mysql = MySQL(app)

#instancia de la bd postrge
db = SQLAlchemy(app) #para usar la bd en otra aplicaciones colocar () sin mas
#instancia de marshmallow
ma = Marshmallow(app)

class Usuario(db.Model):
    #El orm requere una columna id obligatoriamente
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(40), unique=True)
    contra = db.Column(db.String(1000))
    email = db.Column(db.String(100), unique=True)
    telefono = db.Column(db.String(9))

    #Constructor q se ejecuta por cada instancia de la clase
    def __init__(self, nombre, contra, email, telefono):
        self.nombre = nombre
        self.contra = contra
        self.email = email
        self.telefono = telefono

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nombreProd = db.Column(db.String(40))
    precio = db.Column(db.Float)
    cantidad = db.Column(db.Integer)
    categoria = db.Column(db.String(20))
    descripcion = db.Column(db.String(100))
    imagen = db.Column(db.String(50))

    def __init__(self, nombreProd, precio, cantidad, categoria, descripcion, imagen):
        self.nombreProd = nombreProd
        self.precio = precio
        self.cantidad = cantidad
        self.categoria = categoria
        self.descripcion = descripcion
        self.imagen = imagen 
#sentencia para crear todas las tablas
db.create_all()

#creacion de esquema para Usuario
class UsuarioSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nombre', 'contra', 'email', 'telefono')#señalo campos que quiero cada vez que interactue con el esquema
usuario_schema = UsuarioSchema() #permite interactuar con un usuario a la vez
usuarios_schema = UsuarioSchema(many=True) #con varios

class ProductoSchema(ma.Schema):
    class Meta:
        fields = ("id", "nombreProd", "precio", "cantidad", "categoria", "descripcion", "imagen")
producto_schema = ProductoSchema()
productos_schema = ProductoSchema(many=True)
#HASTA AQUI TERMINA LA DEFINICION DE LA BASE DE DATOS

@app.route('/')
def Index():
    return render_template("index.html")

#///////////////////////////////////////
#   OPERACIONES CON USUARIO - INCIO
#///////////////////////////////////////
#URL para crear Usuarios
@app.route('/crearUsuario', methods=['POST'])
def create_user():
    #print(request.json)
    #return 'received'
    nombre = request.json['nombre']
    contra = request.json['contra']
    email = request.json['email']
    telefono = request.json['telefono']
    contra_cifrada = generate_password_hash(contra)
    #check_password_hash(pwhash, password)
    contra_noCifrada = check_password_hash(contra_cifrada, contra)
    print(contra_noCifrada)
    new_user = Usuario(nombre, contra_cifrada, email, telefono) #Creo un Usuario
    db.session.add(new_user) #lo cargo a la BD
    db.session.commit() #termino la operacion

    return usuario_schema.jsonify(new_user) #devuelvwe el usuario creado al front

#URL para listar Usuarios
@app.route("/listarUsuarios", methods=["GET"])
def get_users():
    all_users = Usuario.query.all() #devuelve todos los usuarios
    #print("ALL_USERS: ",type(all_users))
    #result = usuarios_schema.dump(all_users) #graba la lista de usuario recuperados
    #print("RESULT: ",type(result))
    #print(result) 
    #return jsonify(result) #devulve el resultado al cliente en formato JSON
    return render_template('ListarUsuariosAdmin.html',lista = all_users)


#URL para buscar un Usuario específico
@app.route("/listarUsuarios/<id>", methods=["GET"])
def get_user(id):
    user = Usuario.query.get_or_404(id) #si no funciona quitar _or_404
    #return usuario_schema.jsonify(user)
    return "Usuario: %s / Email: %s / Telefono: %s" % (user.nombre, user.email, user.telefono)

#URL para actualizar usuario por id      tbm funcion con metodo POST x si hay error en el front
@app.route("/actualizarUsuario", methods=["GET","POST"])
def update_user():
    form = RegisterForm()
    id = session["id_user"]
    #recupera al usuario
    user = Usuario.query.get(id)
    print("GAAAAAAAAA")
    if request.method == "GET":
        print("GEEET")
        return render_template('ActualizarDatos.html', nombre=user.nombre, email=user.email, telefono=user.telefono, form=form)
    else:
        if form.validate_on_submit():   
            if user: 
                contrase=form.contra.data
                contra_cifrada=generate_password_hash(contrase)

                user.nombre = form.nombre.data
                user.contra = contra_cifrada
                user.email = form.email.data
                user.telefono = form.telefono.data
                
                session["user"] = form.nombre.data
                print(contra_cifrada)
                db.session.commit() #termino la operacion
    
                return render_template('GestionarCuenta.html', nombre=user.nombre, email=user.email, telefono=user.telefono)
        return("ERROR")
        '''
        #recupera los campos del request
        nombre = request.json["nombre"]
        contra = request.json["contra"]
        email = request.json["email"]
        telefono = request.json["telefono"]
        contra_cifrada = generate_password_hash(contra)
        #actualiza los campos
        user.nombre = nombre
        user.contra = contra
        user.email = email
        user.telefono = telefono
        #guarda los cambios
        db.session.commit()
        return usuario_schema.jsonify(user)'''

@app.route("/eliminarUsuario", methods=["POST"])
def delete_user():
    id = session["id_user"]
    user = Usuario.query.get(id) #busca al usuario
    print(user)
    db.session.delete(user) #lo elimina
    db.session.commit() #guarda cambios
    #if "user" in session:
    session.pop("user")
    session.pop("id_user")
    return render_template('index.html')

    #return usuario_schema.jsonify(user) #devuelve el usuario eliminado
#///////////////////////////////////////
#   OPERACIONES CON USUARIO - FIN
#///////////////////////////////////////




#-----------------------------------------------------------------------------------------------------------------

 


#///////////////////////////////////////
#   OPERACIONES DE PRODUCTO - INCIO
#///////////////////////////////////////
class ProductForm(FlaskForm):#Crea el formulario de regisgtro de productos
    nombreProd=StringField('nombreProd',validators=[InputRequired(), Length(min=1,max=30)])
    precio = FloatField('precio',validators=[InputRequired()])
    cantidad = IntegerField('cantidad',validators=[InputRequired()])
    categoria=SelectField('categoria', validators=[InputRequired()], choices=[("LA","Lácteos"),("EN","Enlatados"),("CE","Carnes y embutidos"),("PL","Productos de limpieza"),("FV","Frutas y Verduras")])
    descripcion=TextAreaField('descripcion',validators=[Optional(), Length(min=2,max=100)])
    imagen=StringField('imagen',validators=[Optional(), Length(min=2,max=50)])


#@app.route("/admin",methods=["GET"])
#def indexAdmin():
#    return render_template("Listarproductos.html") 

#LISTAR PRODUCTOS POR CATEGORIA (LISTA TODOS POR DEFAULT)
@app.route("/admin/", methods=["GET"])
@app.route("/admin/<cat>", methods=["GET"])
def get_products_by_cat(cat="HOLU"):
    products = Producto.query.all() #devuelve una lista
    p_filtrados = []  #lista vacia
    cat = request.args.get('cat')

    opciones=["LA","EN","CE","PL","FV"]

    if cat == "ALL":
        p_filtrados = products
    elif (cat in opciones): 
        for p in products:
            if(cat == p.categoria):
                p_filtrados.append(p)
    else:
        p_filtrados="EMPTY"
    #res = productos_schema.dump(p_filtrados) #convierte la lista en un esquema de productos
    #return jsonify(res) #devuelve el esquema convertido a json
    return render_template('Listarproductos.html',listaProd = p_filtrados)


@app.route('/crearProducto', methods=['GET','POST'])
def create_product():
    form = ProductForm()
    if request.method == "GET":
        return render_template("AgregarProducto.html",form=form)
    else:
        if form.validate_on_submit():
            nuevo_producto=Producto(nombreProd=form.nombreProd.data, precio=form.precio.data, cantidad=form.cantidad.data, categoria=form.categoria.data, descripcion=form.descripcion.data, imagen=form.imagen.data)

            db.session.add(nuevo_producto) #lo cargo a la BD
            db.session.commit() #termino la operacion
            #user=Usuario.query.filter_by(nombre=(session["user"])).first()
            return render_template("Listarproductos.html")
    return render_template('Registradoconexito.html')
    
    '''
    nombreProd = request.json['nombreProd']
    precio = request.json['precio']
    cantidad = request.json['cantidad']
    categoria = request.json["categoria"]
    descripcion = request.json["descripcion"]
    imagen = request.json["imagen"]

    new_prod = Producto(nombreProd, precio, cantidad, categoria, descripcion, imagen)
    db.session.add(new_prod)
    db.session.commit()
    return producto_schema.jsonify(new_prod)'''

@app.route("/listarProductos", methods=["GET"])
def get_products():
    all_prods = Producto.query.all() 
    result = productos_schema.dump(all_prods)
    #print(result)
    return jsonify(result)



@app.route("/actualizarProducto/<id>", methods=["PUT"])
def update_product(id):
    #recupera al producto
    prod = Producto.query.get(id)
    #recupera los campos del request
    nombreProd = request.json['nombreProd']
    precio = request.json['precio']
    cantidad = request.json['cantidad']
    categoria = request.json["categoria"]
    descripcion = request.json["descripcion"]
    imagen = request.json["imagen"]
    #actualiza los campos
    prod.nombreProd = nombreProd
    prod.precio = precio
    prod.cantidad = cantidad
    prod.categoria = categoria
    prod.descripcion = descripcion
    prod.imagen = imagen 
    #guarda los cambios
    db.session.commit()
    return producto_schema.jsonify(prod)

@app.route("/eliminarProducto/<id>", methods=["DELETE"])
def delete_product(id):
    prod = Producto.query.get(id)
    db.session.delete(prod)
    db.session.commit()

    return producto_schema.jsonify(prod)
    

#///////////////////////////////////////
#   OPERACIONES DE PRODUCTO - FIN
#///////////////////////////////////////
#-----------------------------------------------------------------------------------------------------------------













#///////////////////////////////////////
#       LOGIN - Inicio (operaciones con el usuario)
#///////////////////////////////////////
#-----------------------------------------------------------------------------------------------------------------
class LoginForm(FlaskForm):
    email= StringField('Email',validators=[InputRequired(), Length(min=4,max=30)])
    contra= PasswordField('Contraseña',validators=[InputRequired(), Length(min=4,max=30)])


@app.route("/login", methods=['GET','POST'])
def login():
    form = LoginForm()
    #if "user" in session:
    #        print("segundo" +session["user"])
    #        return render_template('index.html')
    #        print("GAAAAAA")
    if form.validate_on_submit():
        #print("primer" + session["user"]) 
        user=Usuario.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.contra,form.contra.data):
                session["user"] = user.nombre
                session["id_user"]= user.id
                print(session["user"] )  
                print(session["id_user"])
                #success_message = 'Bienvenido {}'.format(user.nombre)
                #flash(success_message)
                print("LOGGGEADOOOOO")
                #return render_template('Categorizacion.html')
                return redirect(url_for('see_products')) #va el nombre de la funcion, no de la ruta
                

        error_message = "Usuario o contraseña incorrectos"
        flash(error_message)
        return render_template('signin.html', form=form)
    return render_template('signin.html', form=form)

@app.route('/verProductos', methods=['GET']) 
def see_products():
    return render_template('Categorizacion.html')

@app.route("/logout", methods=['GET','POST']) 
def logout():
    if "user" in session:
        session.pop("user")
    if "id_user" in session:
        session.pop("id_user")
    return render_template('index.html')

class RegisterForm(FlaskForm):#Crea el formulario de regisgtro del usuario
    email=StringField('email',validators=[InputRequired(), Length(min=4,max=30)])
    nombre=StringField('nombre',validators=[InputRequired(), Length(min=4,max=30)])
    contra= PasswordField('contra',validators=[InputRequired(), Length(min=8,max=30)])
    telefono=StringField('telefono',validators=[InputRequired(), Length(min=4,max=30)])

@app.route("/registrarse", methods=['GET','POST'])
def registro():
    form = RegisterForm()

    if form.validate_on_submit():    
        contrase=form.contra.data
        contra_cifrada=generate_password_hash(contrase)
        nuevo_usuario=Usuario(nombre=form.nombre.data, contra=contra_cifrada, email=form.email.data, telefono=form.telefono.data)
        session["user"] = form.nombre.data
        print(contra_cifrada)
        db.session.add(nuevo_usuario) #lo cargo a la BD
        db.session.commit() #termino la operacion
        user=Usuario.query.filter_by(nombre=(session["user"])).first()
        session["id_user"]= user.id
        return render_template('Registradoconexito.html')

#nombre contra email telf------> Atributos del Usuario
    return render_template('Registrate.html', form=form)


@app.route("/miCuenta", methods=['GET','POST'])
def revisarMiCuenta():
    id = session["id_user"] 
    user = Usuario.query.get(id)
    print(user.email)
    print(user.id)
    return render_template('GestionarCuenta.html', nombre=user.nombre, email=user.email, telefono=user.telefono)
















@app.errorhandler(404)
def not_found(error=None):
    msg =jsonify({
        "holi": "c q es obvio pero... algo anda mal",
        "mensaje": "Recurso no encontrado: "+ request.url,
        "status": 404
    })
    #response.status_code = 404
    #return response
    return msg 

#main + TAB
if __name__ == "__main__":
    app.run(debug=True, port=8000)