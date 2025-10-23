from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3

app = Flask(__name__, static_folder='static')
CORS(app)  # Habilitar CORS para permitir peticiones desde el frontend

DB_PATH = 'productos.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            descripcion TEXT,
            stock INTEGER NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

init_db()

# Endpoint para obtener todos los productos
@app.route('/productos', methods=['GET'])
def get_productos():
    try:
        conn = get_db_connection()
        productos = conn.execute('SELECT * FROM productos').fetchall()
        conn.close()

        lista_productos = []
        for producto in productos:
            lista_productos.append({
                'id': producto['id'],
                'nombre': producto['nombre'],
                'precio': producto['precio'],
                'descripcion': producto['descripcion'],
                'stock': producto['stock'],
                'fecha_creacion': producto['fecha_creacion']
            })
        return jsonify({
            'success': True,
            'productos': lista_productos
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
# Endpoint para crear un nuevo producto
@app.route('/productos', methods=['POST'])
def create_producto():
    try:
        data = request.get_json()
        nombre = data['nombre']
        precio = data['precio']
        descripcion = data.get('descripcion', '')
        stock = data['stock']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO productos (nombre, precio, descripcion, stock)
            VALUES (?, ?, ?, ?)
        ''', (nombre, precio, descripcion, stock))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()

        return jsonify({
            'success': True,
            'producto': {
                'id': new_id,
                'nombre': nombre,
                'precio': precio,
                'descripcion': descripcion,
                'stock': stock
            }
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
# Endpoint para actualizar un producto existente
@app.route('/productos/<int:producto_id>', methods=['PUT'])
def update_producto(producto_id):
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No se proporcionaron datos para actualizar'}), 400

        conn = get_db_connection()
        producto = conn.execute('SELECT * FROM productos WHERE id = ?', (producto_id,)).fetchone()
        if producto is None:
            conn.close()
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

        nombre = data.get('nombre')
        precio = data.get('precio')
        descripcion = data.get('descripcion')
        stock = data.get('stock')

        conn.execute('''
            UPDATE productos
            SET nombre = ?, precio = ?, descripcion = ?, stock = ?
            WHERE id = ?
        ''', (
            nombre if nombre is not None else producto['nombre'],
            precio if precio is not None else producto['precio'],
            descripcion if descripcion is not None else producto['descripcion'],
            stock if stock is not None else producto['stock'],
            producto_id
        ))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Producto actualizado correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
# Endpoint para eliminar un producto
@app.route('/productos/<int:producto_id>', methods=['DELETE'])
def delete_producto(producto_id):
    try:
        conn = get_db_connection()
        producto = conn.execute('SELECT * FROM productos WHERE id = ?', (producto_id,)).fetchone()
        if producto is None:
            conn.close()
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

        conn.execute('DELETE FROM productos WHERE id = ?', (producto_id,))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Producto eliminado correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Ruta para servir la interfaz gráfica
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=4000)