from flask import Flask, request, render_template, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, IntegerField, FloatField, SelectField
from wtforms.validators import InputRequired, Email, Length, Optional
from werkzeug.security import generate_password_hash, check_password_hash 
from werkzeug.utils import secure_filename  
import os

import views
# initializations
app = Flask(__name__)

app.config['SECRET_KEY']='estoessecretoXD!'

Bootstrap(app)
# PostreSQL Connection
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/postgres'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/postgres'
#para q no mande alertas cuando hagamos modificaciones (opcional)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False 
# MySQL Connection
#app.config['MYSQL_HOST'] = 'localhost' 
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = 'password'
#app.config['MYSQL_DB'] = 'flaskcontacts' 
#mysql = MySQL(app)

#ruta absoluta para guardar las imagenes en en pc de Daniel
app.config['IMAGE_UPLOADS'] = 'C:/Users/Daniel/Desktop/D-Juan-Market/Sprint_2/Sw2-Sprint_1/src/static/img/productos'

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

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'))
    #usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario_id = db.Column(db.Integer)
    nameProd = db.Column(db.String(40))
    cantidad = db.Column(db.Integer)
    precio_uni = db.Column(db.Float)
    precio_total = db.Column(db.Float)
    estado = db.Column(db.String(20))

    def __init__(self, producto_id, usuario_id, nameProd, cantidad, precio_uni, precio_total, estado):
        self.producto_id = producto_id
        self.usuario_id = usuario_id
        self.nameProd = nameProd
        self.cantidad = cantidad
        self.precio_uni = precio_uni
        self.precio_total = precio_total
        self.estado = estado

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

class PedidoSchema(ma.Schema):
    class Meta:
        fields = ("id", "producto_id", "usuario_id", "nameProd","cantidad", "precio_uni", "precio_total", "estado")
pedido_schema = PedidoSchema()
pedidos_schema = PedidoSchema(many=True)
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
def get_products_by_cat(cat="ALL"):
    products = Producto.query.all() #devuelve una lista
    p_filtrados = []  #lista vacia
    cat = request.args.get('cat')

    opciones=["LA","EN","CE","PL","FV"]

    if (cat in opciones):
        for p in products:
            if(cat == p.categoria):
                p_filtrados.append(p)
    else:
        p_filtrados = products
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
            nombreImg = ""
            if request.files:
                    f = request.files['image']
                    print(f)
                    #f.save('/static/img/productos/' + secure_filename(f.filename))
                    if f.filename:
                        f.save(os.path.join(app.config["IMAGE_UPLOADS"], f.filename))
                        nombreImg = f.filename
                    else:
                        #product.imagen=form.imagen.data
                        nombreImg = "algo.jpg"
                    print("Imagen subida: ",f.filename)

            nuevo_producto=Producto(nombreProd=form.nombreProd.data, precio=form.precio.data, cantidad=form.cantidad.data, categoria=form.categoria.data, descripcion=form.descripcion.data, imagen=nombreImg)
            db.session.add(nuevo_producto) #lo cargo a la BD
            db.session.commit() #termino la operacion
            #user=Usuario.query.filter_by(nombre=(session["user"])).first()
            #return render_template("Listarproductos.html")
            #print("LE TONGUEEEEE")
            return redirect(url_for("get_products_by_cat"))
    #return render_template('Registradoconexito.html')
    #print("GAAAAAA")
    return redirect(url_for("get_products_by_cat"))
    
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





@app.route("/eliminarProducto/<id>", methods=["POST"])
def delete_product(id):
    prod = Producto.query.get(id)
    db.session.delete(prod)
    db.session.commit()
    flash("Producto Eliminado Satisfactoriamente")
    return redirect(url_for("get_products_by_cat"))
    

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

#@app.route('/verProductos', methods=['GET']) 
#def see_products():
#    return render_template('Categorizacion.html')
@app.route("/verProductos/", methods=["GET"])
@app.route("/verProductos/<cat>", methods=["GET"])
def see_products(cat="ALL"):
    products = Producto.query.all() #devuelve una lista
    p_filtrados = []  #lista vacia
    cat = request.args.get('cat')

    opciones=["LA","EN","CE","PL","FV"]

    if (cat in opciones):
        for p in products:
            if(cat == p.categoria):
                p_filtrados.append(p)
    else:
        p_filtrados = products
    #res = productos_schema.dump(p_filtrados) #convierte la lista en un esquema de productos
    #return jsonify(res) #devuelve el esquema convertido a json
    return render_template('Categorizacion.html',listaProd = p_filtrados)

@app.route('/compraprocesada',methods=['GET'])
def process():
    return render_template('ProcesarCompra.html')

@app.route("/logout", methods=['GET','POST']) 
def logout():
    if "user" in session:
        session.pop("user")
    if "id_user" in session:
        session.pop("id_user")
    return render_template('index.html')

class RegisterForm(FlaskForm):#Crea el formulario de regisgtro del usuario
    email=StringField('Email',validators=[InputRequired(), Length(min=4,max=30)])
    nombre=StringField('Nombre',validators=[InputRequired(), Length(min=4,max=30)])
    contra= PasswordField('Contraseña',validators=[InputRequired(), Length(min=8,max=30)])
    telefono=StringField('Teléfono',validators=[InputRequired(), Length(min=4,max=30)])

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


@app.route("/actualizarProducto/<id>", methods=["GET","POST"])
def update_producto(id):
    form = ProductForm()
    #recupera al producto
    product = Producto.query.get(id)
    print("GAAAAAAAAA")
    if request.method == "GET":
        print("GEEET")
        return render_template('ActualizarProducto.html',id=product.id,nombre=product.nombreProd, precio=product.precio, cantidad=product.cantidad,categoria=product.categoria,descripcion=product.descripcion,imagen=product.imagen, form=form )
    else:
        if form.validate_on_submit():   
             
                product.nombreProd=form.nombreProd.data
                product.precio=form.precio.data
                product.cantidad=form.cantidad.data
                product.categoria=form.categoria.data
                product.descripcion=form.descripcion.data
                product.imagen=form.imagen.data

                if request.files:
                    print("TRUE")
                    f = request.files['image']
                    print(f)
                    #f.save('/static/img/productos/' + secure_filename(f.filename))
                    if f.filename:
                        f.save(os.path.join(app.config["IMAGE_UPLOADS"], f.filename))
                    else:
                        product.imagen=form.imagen.data
                    print("Imagen subida: ",f.filename)
                db.session.commit() #termino la operacion
                
                return redirect(url_for('get_products_by_cat'))
        return("ERROR")
        


#METODO AUXILIAR PARA COMPROBACION EN POSTMAN
@app.route("/pedidos",methods=["GET"])
def pedidos():
    #peds= Producto.query.all()
    peds= Pedido.query.all()
    #peds = db.session.query(Pedido,Producto).join(Producto).all()
    pedidos = pedidos_schema.dump(peds)
    return jsonify(pedidos)

@app.route("/verPedidos",methods=["GET"]) 
def ver_Pedidos():
    #all_pedidos = Pedido.query.all()
    all_pedidos=Pedido.query.filter_by(usuario_id=(session["id_user"]))
    aux=0
    for ped in all_pedidos:
        aux+=ped.precio_total
    print("PRECIO TOTALLLLLLL: ",aux)
    return render_template('AdministrarPedido.html', listaPed = all_pedidos, total_precio = aux)

@app.route("/añadirPedido/<id>",methods=["POST"])
def añadir_Pedido(id):
    prod = Producto.query.get(id)
    user_id = session["id_user"] 
    
    print("ID DEL PRODUCTO ", prod.id)
    print("ID DEL USUARIO ",user_id)
    print("PRECIO UNI DEL PRODUCTO",prod.precio)

    nuevo_pedido=Pedido(prod.id, user_id, prod.nombreProd, 1, prod.precio, prod.precio, "Deseado")
    db.session.add(nuevo_pedido) #lo cargo a la BD
    db.session.commit() #termino la operacion
    return redirect(url_for('ver_Pedidos'))

@app.route("/masPedido/<id>", methods=["POST"])
def aumentar_Pedido(id):
    ped = Pedido.query.get(id)
    prod_id = ped.producto_id
    prod = Producto.query.get(prod_id)
    prod_cant = prod.cantidad
    if ped.cantidad < prod_cant:
        ped.cantidad += 1
    ped.precio_total = ped.precio_uni * ped.cantidad 
    db.session.commit()
    
    return redirect(url_for("ver_Pedidos"))
#flash("Producto Actualizado Satisfactoriamente") 

@app.route("/menosPedido/<id>", methods=["POST"])
def disminuir_Pedido(id):
    ped = Pedido.query.get(id)
    if ped.cantidad>1:
        ped.cantidad -= 1
    ped.precio_total = ped.precio_uni * ped.cantidad 
    db.session.commit()
     
    return redirect(url_for("ver_Pedidos"))
#flash("Producto Actualizado Satisfactoriamente")

@app.route("/eliminarPedido/<id>", methods=["POST"])
def eliminar_Pedido(id):
    ped = Pedido.query.get(id)
    db.session.delete(ped)
    db.session.commit()
     
    return redirect(url_for("ver_Pedidos"))
#flash("Producto Eliminado Satisfactoriamente")

@app.route("/gabor",methods=["GET", "POST"])
def cargaImg():
    if request.method == "POST":

        if request.files:
            f = request.files['image']

            print(f)
            if f.filename:
                #f.save('/static/img/productos/' + secure_filename(f.filename))
                f.save(os.path.join(app.config["IMAGE_UPLOADS"], f.filename))
            else:
                f.save(os.path.join(app.config["IMAGE_UPLOADS"], "VACIO.jpg"))
            print("Imagen subida: ",f.filename)
            #Imagen subida:  old-man (1).png
            #guardar el filename 
    return render_template("GAA_CargarImagen.html")


@app.errorhandler(404)
def not_found(error=None):
    msg =jsonify({
        "holas": "c q es obvio pero... algo anda mal",
        "mensaje": "Recurso no encontrado: "+ request.url,
        "status": 404
    })
    return msg 

#main + TAB
if __name__ == "__main__":
    app.run(debug=True, port=8000)