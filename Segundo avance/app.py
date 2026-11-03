import os
import json
import http.server
import socketserver
import urllib.parse
import html as html_lib
import mysql.connector

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "12722236",
    "database": "mr5"
}

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def obtener_conexion():
    return mysql.connector.connect(**DB_CONFIG)


def consultar_bd(query, params=None):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    filas = cursor.fetchall()
    cursor.close()
    conn.close()
    return filas


def ejecutar_dml(query, params=None):
    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        conn.start_transaction()
        cursor.execute(query, params or ())
        nuevo_id = cursor.lastrowid
        conn.commit()
        return nuevo_id
    except Exception as err:
        conn.rollback()
        raise err
    finally:
        cursor.close()
        conn.close()


def registrar_venta_transaccional(id_sucursal, id_empleado, id_cliente, metodo_pago, items_venta):
    if metodo_pago not in ("EFECTIVO", "QR"):
        raise ValueError("El metodo de pago debe ser EFECTIVO o QR.")

    productos_agrupados = {}
    for id_prod, cant in items_venta:
        if cant <= 0:
            raise ValueError("La cantidad vendida debe ser mayor a cero.")
        productos_agrupados[id_prod] = productos_agrupados.get(id_prod, 0) + cant

    if not productos_agrupados:
        raise ValueError("Seleccione al menos un producto para registrar la venta.")

    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)

    try:
        conn.start_transaction()
        lineas_confirmadas = []

        for id_prod, cant_solicitada in productos_agrupados.items():
            cursor.execute(
                """
                SELECT p.nombre, p.precio, i.stock
                FROM PRODUCTO p
                LEFT JOIN INVENTARIO i
                    ON p.id_producto = i.id_producto AND i.id_sucursal = %s
                WHERE p.id_producto = %s
                FOR UPDATE;
                """,
                (id_sucursal, id_prod)
            )
            prod = cursor.fetchone()
            if not prod:
                raise ValueError(f"El producto #{id_prod} no existe.")

            stock_disp = prod["stock"] if prod["stock"] is not None else 0
            if stock_disp < cant_solicitada:
                raise ValueError(
                    f"Stock insuficiente para '{prod['nombre']}' en esta sucursal "
                    f"(Disponible: {stock_disp} | Solicitado: {cant_solicitada})."
                )

            lineas_confirmadas.append({
                "id_producto": id_prod,
                "cantidad": cant_solicitada,
                "precio_unitario": prod["precio"]
            })

        cursor.execute(
            """
            INSERT INTO VENTA (id_sucursal, id_empleado, id_cliente, fecha_hora, metodo_pago)
            VALUES (%s, %s, %s, NOW(), %s);
            """,
            (id_sucursal, id_empleado, id_cliente, metodo_pago)
        )
        id_venta_nueva = cursor.lastrowid

        for item in lineas_confirmadas:
            cursor.execute(
                """
                INSERT INTO DETALLE_VENTA (id_venta, id_producto, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s);
                """,
                (id_venta_nueva, item["id_producto"], item["cantidad"], item["precio_unitario"])
            )
            cursor.execute(
                """
                UPDATE INVENTARIO
                SET stock = stock - %s
                WHERE id_sucursal = %s AND id_producto = %s;
                """,
                (item["cantidad"], id_sucursal, item["id_producto"])
            )

        conn.commit()
        return id_venta_nueva

    except Exception as err:
        conn.rollback()
        raise err
    finally:
        cursor.close()
        conn.close()


def anular_venta_transaccional(id_venta):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()
        cursor.execute("SELECT id_sucursal FROM VENTA WHERE id_venta = %s FOR UPDATE;", (id_venta,))
        venta = cursor.fetchone()
        if not venta:
            raise ValueError(f"La venta #{id_venta} no existe.")

        cursor.execute(
            "SELECT id_producto, cantidad FROM DETALLE_VENTA WHERE id_venta = %s;",
            (id_venta,)
        )
        detalles = cursor.fetchall()

        for item in detalles:
            cursor.execute(
                """
                INSERT INTO INVENTARIO (id_sucursal, id_producto, stock)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE stock = stock + VALUES(stock);
                """,
                (venta["id_sucursal"], item["id_producto"], item["cantidad"])
            )

        cursor.execute("DELETE FROM VENTA WHERE id_venta = %s;", (id_venta,))
        conn.commit()
    except Exception as err:
        conn.rollback()
        raise err
    finally:
        cursor.close()
        conn.close()


def crear_producto_con_inventario_inicial(id_proveedor, id_categoria, codigo_barras, nombre, precio):
    codigo_limpio = codigo_barras.strip() if codigo_barras and codigo_barras.strip() else None
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()
        cursor.execute(
            """
            INSERT INTO PRODUCTO (id_proveedor, id_categoria, codigo_barras, nombre, precio)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (id_proveedor, id_categoria, codigo_limpio, nombre.strip(), precio)
        )
        id_prod = cursor.lastrowid

        cursor.execute("SELECT id_sucursal FROM SUCURSAL;")
        for suc in cursor.fetchall():
            cursor.execute(
                "INSERT INTO INVENTARIO (id_sucursal, id_producto, stock) VALUES (%s, %s, 0);",
                (suc["id_sucursal"], id_prod)
            )
        conn.commit()
        return id_prod
    except Exception as err:
        conn.rollback()
        raise err
    finally:
        cursor.close()
        conn.close()


def eliminar_producto_transaccional(id_producto):
    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        conn.start_transaction()
        cursor.execute("SELECT COUNT(*) FROM DETALLE_VENTA WHERE id_producto = %s;", (id_producto,))
        if cursor.fetchone()[0] > 0:
            raise ValueError("No se puede eliminar el producto porque ya tiene ventas registradas.")
        cursor.execute("DELETE FROM INVENTARIO WHERE id_producto = %s;", (id_producto,))
        cursor.execute("DELETE FROM PRODUCTO WHERE id_producto = %s;", (id_producto,))
        conn.commit()
    except Exception as err:
        conn.rollback()
        raise err
    finally:
        cursor.close()
        conn.close()


def eliminar_sucursal_transaccional(id_sucursal):
    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        conn.start_transaction()
        cursor.execute("DELETE FROM INVENTARIO WHERE id_sucursal = %s AND stock = 0;", (id_sucursal,))
        cursor.execute("DELETE FROM SUCURSAL WHERE id_sucursal = %s;", (id_sucursal,))
        conn.commit()
    except Exception as err:
        conn.rollback()
        raise err
    finally:
        cursor.close()
        conn.close()


class Mr5Handler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        ruta = parsed_url.path

        if ruta == "/styles.css":
            self.servir_archivo_estatico("styles.css", "text/css; charset=utf-8")
            return

        if ruta == "/script.js":
            self.servir_archivo_estatico("script.js", "application/javascript; charset=utf-8")
            return

        query_params = urllib.parse.parse_qs(parsed_url.query)
        filtro_sucursal = query_params.get("sucursal", ["TODAS"])[0]
        filtro_alerta = query_params.get("alerta", ["TODAS"])[0]
        tab_activa = query_params.get("tab", ["pos"])[0]
        msg_exito = query_params.get("ok", [""])[0]
        msg_error = query_params.get("err", [""])[0]

        self.renderizar_index(filtro_sucursal, filtro_alerta, tab_activa, msg_exito, msg_error)

    def servir_archivo_estatico(self, nombre_archivo, content_type):
        ruta_completa = os.path.join(BASE_DIR, nombre_archivo)
        if not os.path.exists(ruta_completa):
            self.send_error(404, f"Archivo no encontrado: {nombre_archivo}")
            return
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()
        with open(ruta_completa, "rb") as f:
            self.wfile.write(f.read())

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length).decode("utf-8")
        form = urllib.parse.parse_qs(post_body)

        accion = form.get("accion", [""])[0]
        tab_retorno = form.get("tab_retorno", ["pos"])[0]
        msg_ok = ""
        msg_err = ""

        try:
            if accion == "registrar_venta":
                id_sucursal = int(form.get("id_sucursal", [0])[0])
                id_empleado = int(form.get("id_empleado", [0])[0])
                id_cliente = int(form.get("id_cliente", [0])[0])
                metodo_pago = form.get("metodo_pago", [""])[0]

                productos_ids = form.get("id_producto[]", [])
                cantidades = form.get("cantidad[]", [])
                items = [(int(p), int(c)) for p, c in zip(productos_ids, cantidades) if p and c]

                id_venta = registrar_venta_transaccional(
                    id_sucursal, id_empleado, id_cliente, metodo_pago, items
                )
                msg_ok = f"Venta #{id_venta} registrada correctamente ({metodo_pago})."

            elif accion == "eliminar_venta":
                id_venta = int(form.get("id_venta", [0])[0])
                anular_venta_transaccional(id_venta)
                msg_ok = f"Venta #{id_venta} anulada y stock devuelto al inventario."

            elif accion == "reponer_stock":
                id_sucursal = int(form.get("id_sucursal", [0])[0])
                id_producto = int(form.get("id_producto", [0])[0])
                cantidad = int(form.get("cantidad", [0])[0])
                if cantidad <= 0:
                    raise ValueError("La cantidad a reponer debe ser mayor a cero.")
                ejecutar_dml(
                    """
                    INSERT INTO INVENTARIO (id_sucursal, id_producto, stock)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE stock = stock + VALUES(stock);
                    """,
                    (id_sucursal, id_producto, cantidad)
                )
                msg_ok = f"Stock actualizado: se agregaron {cantidad} unidades."

            elif accion == "nuevo_producto":
                id_prov = int(form.get("id_proveedor", [0])[0])
                id_cat = int(form.get("id_categoria", [0])[0])
                codigo = form.get("codigo_barras", [""])[0]
                nombre = form.get("nombre", [""])[0]
                precio = float(form.get("precio", [0])[0])
                id_prod = crear_producto_con_inventario_inicial(id_prov, id_cat, codigo, nombre, precio)
                msg_ok = f"Producto '{nombre.strip()}' registrado con ID #{id_prod}."

            elif accion == "actualizar_precio":
                id_prod = int(form.get("id_producto", [0])[0])
                nuevo_precio = float(form.get("nuevo_precio", [0])[0])
                if nuevo_precio <= 0:
                    raise ValueError("El precio debe ser mayor a cero.")
                ejecutar_dml(
                    "UPDATE PRODUCTO SET precio = %s WHERE id_producto = %s;",
                    (nuevo_precio, id_prod)
                )
                msg_ok = f"Precio actualizado a Bs {nuevo_precio:.2f}."

            elif accion == "editar_producto":
                id_prod = int(form.get("id_producto", [0])[0])
                nombre = form.get("nombre", [""])[0].strip()
                codigo = form.get("codigo_barras", [""])[0].strip() or None
                precio = float(form.get("precio", [0])[0])
                id_cat = int(form.get("id_categoria", [0])[0])
                id_prov = int(form.get("id_proveedor", [0])[0])
                if not nombre or precio <= 0:
                    raise ValueError("Nombre y precio mayor a cero son obligatorios.")
                ejecutar_dml(
                    """
                    UPDATE PRODUCTO
                    SET nombre = %s, codigo_barras = %s, precio = %s, id_categoria = %s, id_proveedor = %s
                    WHERE id_producto = %s;
                    """,
                    (nombre, codigo, precio, id_cat, id_prov, id_prod)
                )
                msg_ok = f"Producto #{id_prod} actualizado correctamente."

            elif accion == "eliminar_producto":
                id_prod = int(form.get("id_producto", [0])[0])
                eliminar_producto_transaccional(id_prod)
                msg_ok = f"Producto #{id_prod} eliminado del catalogo."

            elif accion == "nuevo_cliente":
                nombre = form.get("nombre", [""])[0].strip()
                if not nombre:
                    raise ValueError("El nombre del cliente es obligatorio.")
                nuevo_id = ejecutar_dml("INSERT INTO CLIENTE (nombre) VALUES (%s);", (nombre,))
                msg_ok = f"Cliente '{nombre}' registrado con ID #{nuevo_id}."

            elif accion == "editar_cliente":
                id_cli = int(form.get("id_cliente", [0])[0])
                nombre = form.get("nombre", [""])[0].strip()
                if not nombre:
                    raise ValueError("El nombre del cliente es obligatorio.")
                ejecutar_dml("UPDATE CLIENTE SET nombre = %s WHERE id_cliente = %s;", (nombre, id_cli))
                msg_ok = f"Cliente #{id_cli} actualizado a '{nombre}'."

            elif accion == "eliminar_cliente":
                id_cli = int(form.get("id_cliente", [0])[0])
                ejecutar_dml("DELETE FROM CLIENTE WHERE id_cliente = %s;", (id_cli,))
                msg_ok = f"Cliente #{id_cli} eliminado."

            elif accion == "nueva_sucursal":
                nombre = form.get("nombre", [""])[0].strip()
                direccion = form.get("direccion", [""])[0].strip()
                telefono = form.get("telefono", [""])[0].strip()
                nuevo_id = ejecutar_dml(
                    "INSERT INTO SUCURSAL (nombre, direccion, telefono) VALUES (%s, %s, %s);",
                    (nombre, direccion, telefono)
                )
                msg_ok = f"Sucursal '{nombre}' registrada con ID #{nuevo_id}."

            elif accion == "editar_sucursal":
                id_suc = int(form.get("id_sucursal", [0])[0])
                nombre = form.get("nombre", [""])[0].strip()
                direccion = form.get("direccion", [""])[0].strip()
                telefono = form.get("telefono", [""])[0].strip()
                ejecutar_dml(
                    "UPDATE SUCURSAL SET nombre = %s, direccion = %s, telefono = %s WHERE id_sucursal = %s;",
                    (nombre, direccion, telefono, id_suc)
                )
                msg_ok = f"Sucursal #{id_suc} actualizada."

            elif accion == "eliminar_sucursal":
                id_suc = int(form.get("id_sucursal", [0])[0])
                eliminar_sucursal_transaccional(id_suc)
                msg_ok = f"Sucursal #{id_suc} eliminada."

            elif accion == "nuevo_empleado":
                id_suc = int(form.get("id_sucursal", [0])[0])
                nombre = form.get("nombre", [""])[0].strip()
                cargo = form.get("cargo", [""])[0].strip()
                nuevo_id = ejecutar_dml(
                    "INSERT INTO EMPLEADO (id_sucursal, nombre, cargo) VALUES (%s, %s, %s);",
                    (id_suc, nombre, cargo)
                )
                msg_ok = f"Empleado '{nombre}' registrado con ID #{nuevo_id}."

            elif accion == "editar_empleado":
                id_emp = int(form.get("id_empleado", [0])[0])
                id_suc = int(form.get("id_sucursal", [0])[0])
                nombre = form.get("nombre", [""])[0].strip()
                cargo = form.get("cargo", [""])[0].strip()
                ejecutar_dml(
                    "UPDATE EMPLEADO SET nombre = %s, cargo = %s, id_sucursal = %s WHERE id_empleado = %s;",
                    (nombre, cargo, id_suc, id_emp)
                )
                msg_ok = f"Empleado #{id_emp} actualizado."

            elif accion == "eliminar_empleado":
                id_emp = int(form.get("id_empleado", [0])[0])
                ejecutar_dml("DELETE FROM EMPLEADO WHERE id_empleado = %s;", (id_emp,))
                msg_ok = f"Empleado #{id_emp} eliminado."

            elif accion == "nuevo_proveedor":
                nombre = form.get("nombre", [""])[0].strip()
                telefono = form.get("telefono", [""])[0].strip()
                nuevo_id = ejecutar_dml(
                    "INSERT INTO PROVEEDOR (nombre, telefono) VALUES (%s, %s);",
                    (nombre, telefono)
                )
                msg_ok = f"Proveedor '{nombre}' registrado con ID #{nuevo_id}."

            elif accion == "editar_proveedor":
                id_prov = int(form.get("id_proveedor", [0])[0])
                nombre = form.get("nombre", [""])[0].strip()
                telefono = form.get("telefono", [""])[0].strip()
                ejecutar_dml(
                    "UPDATE PROVEEDOR SET nombre = %s, telefono = %s WHERE id_proveedor = %s;",
                    (nombre, telefono, id_prov)
                )
                msg_ok = f"Proveedor #{id_prov} actualizado."

            elif accion == "eliminar_proveedor":
                id_prov = int(form.get("id_proveedor", [0])[0])
                ejecutar_dml("DELETE FROM PROVEEDOR WHERE id_proveedor = %s;", (id_prov,))
                msg_ok = f"Proveedor #{id_prov} eliminado."

            elif accion == "nueva_categoria":
                nombre = form.get("nombre", [""])[0].strip()
                descripcion = form.get("descripcion", [""])[0].strip()
                nuevo_id = ejecutar_dml(
                    "INSERT INTO CATEGORIA (nombre, descripcion) VALUES (%s, %s);",
                    (nombre, descripcion)
                )
                msg_ok = f"Categoria '{nombre}' registrada con ID #{nuevo_id}."

            elif accion == "editar_categoria":
                id_cat = int(form.get("id_categoria", [0])[0])
                nombre = form.get("nombre", [""])[0].strip()
                descripcion = form.get("descripcion", [""])[0].strip()
                ejecutar_dml(
                    "UPDATE CATEGORIA SET nombre = %s, descripcion = %s WHERE id_categoria = %s;",
                    (nombre, descripcion, id_cat)
                )
                msg_ok = f"Categoria #{id_cat} actualizada."

            elif accion == "eliminar_categoria":
                id_cat = int(form.get("id_categoria", [0])[0])
                ejecutar_dml("DELETE FROM CATEGORIA WHERE id_categoria = %s;", (id_cat,))
                msg_ok = f"Categoria #{id_cat} eliminada."

        except Exception as e:
            msg_err = f"No se pudo completar la operacion: {e}"

        params_redirect = {"tab": tab_retorno}
        if msg_ok:
            params_redirect["ok"] = msg_ok
        if msg_err:
            params_redirect["err"] = msg_err

        self.send_response(303)
        self.send_header("Location", "/?" + urllib.parse.urlencode(params_redirect))
        self.end_headers()

    def renderizar_index(self, filtro_sucursal, filtro_alerta, tab_activa, msg_exito, msg_error):
        ruta_html = os.path.join(BASE_DIR, "index.html")
        if not os.path.exists(ruta_html):
            self.send_error(500, "No se encontro el archivo index.html")
            return

        with open(ruta_html, "r", encoding="utf-8") as f:
            plantilla = f.read()

        try:
            sucursales = consultar_bd("SELECT * FROM SUCURSAL ORDER BY id_sucursal;")
            proveedores = consultar_bd("SELECT * FROM PROVEEDOR ORDER BY id_proveedor;")
            categorias = consultar_bd("SELECT * FROM CATEGORIA ORDER BY id_categoria;")
            clientes = consultar_bd("SELECT * FROM CLIENTE ORDER BY id_cliente DESC;")
            empleados = consultar_bd(
                """
                SELECT e.id_empleado, e.id_sucursal, e.nombre, e.cargo, s.nombre AS sucursal_nombre
                FROM EMPLEADO e
                INNER JOIN SUCURSAL s ON e.id_sucursal = s.id_sucursal
                ORDER BY e.id_empleado;
                """
            )
            productos = consultar_bd(
                """
                SELECT p.*, c.nombre AS categoria_nombre, pr.nombre AS proveedor_nombre
                FROM PRODUCTO p
                INNER JOIN CATEGORIA c ON p.id_categoria = c.id_categoria
                INNER JOIN PROVEEDOR pr ON p.id_proveedor = pr.id_proveedor
                ORDER BY p.id_producto;
                """
            )

            stats_prod = consultar_bd(
                """
                SELECT COUNT(*) AS total_productos,
                       COALESCE(ROUND(AVG(precio), 2), 0) AS precio_promedio,
                       COALESCE(MIN(precio), 0) AS producto_mas_barato,
                       COALESCE(MAX(precio), 0) AS producto_mas_caro
                FROM PRODUCTO;
                """
            )[0]

            stats_ven = consultar_bd(
                """
                SELECT COUNT(DISTINCT v.id_venta) AS total_ventas,
                       COALESCE(SUM(dv.cantidad * dv.precio_unitario), 0) AS ingresos_totales
                FROM VENTA v
                INNER JOIN DETALLE_VENTA dv ON v.id_venta = dv.id_venta;
                """
            )[0]

            sql_inv = "SELECT * FROM V_INVENTARIO_DETALLADO WHERE 1=1"
            params_inv = []
            if filtro_sucursal != "TODAS":
                sql_inv += " AND sucursal = %s"
                params_inv.append(filtro_sucursal)
            if filtro_alerta != "TODAS":
                sql_inv += " AND estado_alerta = %s"
                params_inv.append(filtro_alerta)
            sql_inv += " ORDER BY sucursal, producto;"
            inventario = consultar_bd(sql_inv, params_inv)

            ventas = consultar_bd("SELECT * FROM V_RESUMEN_VENTAS ORDER BY id_venta DESC;")

            detalles_recibos = consultar_bd(
                """
                SELECT v.id_venta, v.fecha_hora, cl.nombre AS cliente,
                       s.nombre AS sucursal, e.nombre AS empleado,
                       p.nombre AS producto, dv.cantidad, dv.precio_unitario,
                       (dv.cantidad * dv.precio_unitario) AS subtotal, v.metodo_pago
                FROM VENTA v
                INNER JOIN CLIENTE cl ON v.id_cliente = cl.id_cliente
                INNER JOIN SUCURSAL s ON v.id_sucursal = s.id_sucursal
                INNER JOIN EMPLEADO e ON v.id_empleado = e.id_empleado
                INNER JOIN DETALLE_VENTA dv ON v.id_venta = dv.id_venta
                INNER JOIN PRODUCTO p ON dv.id_producto = p.id_producto
                ORDER BY v.id_venta DESC, p.nombre ASC;
                """
            )

            sin_venta = consultar_bd(
                """
                SELECT p.id_producto, p.codigo_barras, p.nombre, p.precio
                FROM PRODUCTO p
                LEFT JOIN DETALLE_VENTA dv ON p.id_producto = dv.id_producto
                WHERE dv.id_venta IS NULL;
                """
            )

            ranking_cte = consultar_bd(
                """
                WITH totales_por_venta AS (
                    SELECT v.id_venta, v.id_cliente, cl.nombre AS cliente,
                           v.fecha_hora, SUM(dv.cantidad * dv.precio_unitario) AS monto_venta
                    FROM VENTA v
                    INNER JOIN CLIENTE cl ON v.id_cliente = cl.id_cliente
                    INNER JOIN DETALLE_VENTA dv ON v.id_venta = dv.id_venta
                    GROUP BY v.id_venta, v.id_cliente, cl.nombre, v.fecha_hora
                )
                SELECT id_venta, cliente, fecha_hora, monto_venta,
                       SUM(monto_venta) OVER (PARTITION BY id_cliente ORDER BY fecha_hora ASC) AS acumulado_cliente,
                       DENSE_RANK() OVER (ORDER BY monto_venta DESC) AS ranking_mayor_venta
                FROM totales_por_venta
                ORDER BY ranking_mayor_venta ASC, fecha_hora DESC;
                """
            )
            error_bd_html = ""
        except Exception as e:
            sucursales, proveedores, categorias, clientes, empleados, productos = [], [], [], [], [], []
            inventario, ventas, detalles_recibos, sin_venta, ranking_cte = [], [], [], [], []
            stats_prod = {"total_productos": 0, "precio_promedio": 0, "producto_mas_barato": 0, "producto_mas_caro": 0}
            stats_ven = {"total_ventas": 0, "ingresos_totales": 0}
            error_bd_html = f'<div class="alert alert-error"><strong>Error de base de datos:</strong> {html_lib.escape(str(e))}</div>'

        notificaciones = error_bd_html
        if msg_exito:
            notificaciones += f'<div class="alert alert-success">{html_lib.escape(msg_exito)}</div>'
        if msg_error:
            notificaciones += f'<div class="alert alert-error">{html_lib.escape(msg_error)}</div>'

        op_sucursal = "".join([
            f'<option value="{s["id_sucursal"]}">{html_lib.escape(s["nombre"])} ({html_lib.escape(s["direccion"])})</option>'
            for s in sucursales
        ])
        op_empleado = "".join([
            f'<option value="{e["id_empleado"]}">{html_lib.escape(e["nombre"])} - {html_lib.escape(e["cargo"])} ({html_lib.escape(e["sucursal_nombre"])})</option>'
            for e in empleados
        ])
        op_cliente = "".join([
            f'<option value="{c["id_cliente"]}">#{c["id_cliente"]} - {html_lib.escape(c["nombre"])}</option>'
            for c in clientes
        ])
        op_producto = "".join([
            f'<option value="{p["id_producto"]}" data-precio="{p["precio"]}">{html_lib.escape(p["nombre"])} (Bs {p["precio"]})</option>'
            for p in productos
        ])
        op_proveedor = "".join([
            f'<option value="{pr["id_proveedor"]}">{html_lib.escape(pr["nombre"])}</option>'
            for pr in proveedores
        ])
        op_categoria = "".join([
            f'<option value="{cat["id_categoria"]}">{html_lib.escape(cat["nombre"])}</option>'
            for cat in categorias
        ])

        op_filtro_suc = '<option value="TODAS">Todas las sucursales</option>' + "".join([
            f'<option value="{html_lib.escape(s["nombre"])}" {"selected" if filtro_sucursal == s["nombre"] else ""}>{html_lib.escape(s["nombre"])}</option>'
            for s in sucursales
        ])
        estados = ["TODAS", "STOCK CRÍTICO", "STOCK MEDIO", "ABASTECIDO"]
        op_filtro_alerta = "".join([
            f'<option value="{est}" {"selected" if filtro_alerta == est else ""}>{"Todos los estados" if est == "TODAS" else est}</option>'
            for est in estados
        ])

        recibos_por_venta = {}
        for d in detalles_recibos:
            vid = d["id_venta"]
            if vid not in recibos_por_venta:
                recibos_por_venta[vid] = {
                    "id_venta": vid,
                    "fecha_hora": str(d["fecha_hora"]),
                    "sucursal": d["sucursal"],
                    "empleado": d["empleado"],
                    "cliente": d["cliente"],
                    "metodo_pago": d["metodo_pago"],
                    "items": [],
                    "total": 0.0
                }
            recibos_por_venta[vid]["items"].append({
                "producto": d["producto"],
                "cantidad": int(d["cantidad"]),
                "precio_unitario": float(d["precio_unitario"]),
                "subtotal": float(d["subtotal"])
            })
            recibos_por_venta[vid]["total"] += float(d["subtotal"])

        def badge_stock(estado):
            if estado == "STOCK CRÍTICO":
                return '<span class="badge badge-danger">STOCK CRITICO</span>'
            if estado == "STOCK MEDIO":
                return '<span class="badge badge-warning">STOCK MEDIO</span>'
            return '<span class="badge badge-success">ABASTECIDO</span>'

        filas_inv = "".join([
            f"<tr><td><b>{html_lib.escape(r['sucursal'])}</b></td>"
            f"<td><code>{html_lib.escape(str(r['codigo_barras'] or 'S/C'))}</code></td>"
            f"<td><b>{html_lib.escape(r['producto'])}</b></td>"
            f"<td>{html_lib.escape(r['categoria'])}</td>"
            f"<td>{html_lib.escape(r['proveedor'])}</td>"
            f"<td>Bs {r['precio']}</td>"
            f"<td><b>{r['stock']} u.</b></td>"
            f"<td>{badge_stock(r['estado_alerta'])}</td></tr>"
            for r in inventario
        ]) or "<tr><td colspan='8' class='empty-row'>Sin registros para este filtro.</td></tr>"

        filas_catalogo_prod = "".join([
            f"<tr><td>#{p['id_producto']}</td>"
            f"<td><code>{html_lib.escape(str(p['codigo_barras'] or 'S/C'))}</code></td>"
            f"<td><b>{html_lib.escape(p['nombre'])}</b></td>"
            f"<td>{html_lib.escape(p['categoria_nombre'])}</td>"
            f"<td>{html_lib.escape(p['proveedor_nombre'])}</td>"
            f"<td><b>Bs {p['precio']}</b></td>"
            f"<td class='actions-cell'>"
            f"<button type='button' class='btn btn-sm btn-secondary' "
            f"data-id='{p['id_producto']}' "
            f"data-nombre='{html_lib.escape(p['nombre'], quote=True)}' "
            f"data-codigo='{html_lib.escape(str(p['codigo_barras'] or ''), quote=True)}' "
            f"data-precio='{p['precio']}' "
            f"data-cat='{p['id_categoria']}' "
            f"data-prov='{p['id_proveedor']}' "
            f"onclick='abrirModalProducto(this)'>Editar</button>"
            f"<form method='POST' action='/' class='inline-form'>"
            f"<input type='hidden' name='accion' value='eliminar_producto'>"
            f"<input type='hidden' name='tab_retorno' value='inventario'>"
            f"<input type='hidden' name='id_producto' value='{p['id_producto']}'>"
            f"<button type='submit' class='btn btn-sm btn-danger'>Eliminar</button>"
            f"</form></td></tr>"
            for p in productos
        ])

        filas_ven = "".join([
            f"<tr><td><b>#{r['id_venta']}</b></td>"
            f"<td>{r['fecha_hora']}</td>"
            f"<td>{html_lib.escape(r['sucursal'])}</td>"
            f"<td>{html_lib.escape(r['empleado'])}</td>"
            f"<td>{html_lib.escape(r['cliente'])}</td>"
            f"<td><span class='badge badge-pay'>{html_lib.escape(r['metodo_pago'])}</span></td>"
            f"<td><b>Bs {r['total_venta']}</b></td>"
            f"<td class='actions-cell'>"
            f"<button type='button' class='btn btn-sm' onclick='verNotaVenta({r['id_venta']})'>Ver Recibo</button>"
            f"<form method='POST' action='/' class='inline-form'>"
            f"<input type='hidden' name='accion' value='eliminar_venta'>"
            f"<input type='hidden' name='tab_retorno' value='pos'>"
            f"<input type='hidden' name='id_venta' value='{r['id_venta']}'>"
            f"<button type='submit' class='btn btn-sm btn-danger'>Anular</button>"
            f"</form></td></tr>"
            for r in ventas
        ])

        filas_recibos = "".join([
            f"<tr><td><b>#{r['id_venta']}</b></td>"
            f"<td>{r['fecha_hora']}</td>"
            f"<td>{html_lib.escape(r['sucursal'])}</td>"
            f"<td>{html_lib.escape(r['cliente'])}</td>"
            f"<td><b>{html_lib.escape(r['producto'])}</b></td>"
            f"<td>{r['cantidad']}</td>"
            f"<td>Bs {r['precio_unitario']}</td>"
            f"<td><b>Bs {r['subtotal']}</b></td>"
            f"<td>{html_lib.escape(r['metodo_pago'])}</td></tr>"
            for r in detalles_recibos
        ])

        filas_sin = "".join([
            f"<tr><td>#{r['id_producto']}</td>"
            f"<td><code>{html_lib.escape(str(r['codigo_barras'] or 'S/C'))}</code></td>"
            f"<td><b>{html_lib.escape(r['nombre'])}</b></td>"
            f"<td>Bs {r['precio']}</td></tr>"
            for r in sin_venta
        ]) or "<tr><td colspan='4' class='empty-row'>Todos los productos tienen ventas registradas.</td></tr>"

        filas_cte = "".join([
            f"<tr><td><span class='badge badge-rank'>#{r['ranking_mayor_venta']}</span></td>"
            f"<td><b>Venta #{r['id_venta']}</b></td>"
            f"<td>{html_lib.escape(r['cliente'])}</td>"
            f"<td>{r['fecha_hora']}</td>"
            f"<td><b>Bs {r['monto_venta']}</b></td>"
            f"<td class='text-primary'><b>Bs {r['acumulado_cliente']}</b></td></tr>"
            for r in ranking_cte
        ])

        filas_sucursales = "".join([
            f"<tr><td>#{s['id_sucursal']}</td><td><b>{html_lib.escape(s['nombre'])}</b></td>"
            f"<td>{html_lib.escape(s['direccion'])}</td><td>{html_lib.escape(s['telefono'])}</td>"
            f"<td class='actions-cell'>"
            f"<button type='button' class='btn btn-sm btn-secondary' "
            f"data-id='{s['id_sucursal']}' "
            f"data-nombre='{html_lib.escape(s['nombre'], quote=True)}' "
            f"data-direccion='{html_lib.escape(s['direccion'], quote=True)}' "
            f"data-telefono='{html_lib.escape(s['telefono'], quote=True)}' "
            f"onclick='abrirModalSucursal(this)'>Editar</button>"
            f"<form method='POST' action='/' class='inline-form'>"
            f"<input type='hidden' name='accion' value='eliminar_sucursal'>"
            f"<input type='hidden' name='tab_retorno' value='entidades'>"
            f"<input type='hidden' name='id_sucursal' value='{s['id_sucursal']}'>"
            f"<button type='submit' class='btn btn-sm btn-danger'>Eliminar</button>"
            f"</form></td></tr>"
            for s in sucursales
        ])

        filas_empleados = "".join([
            f"<tr><td>#{e['id_empleado']}</td><td><b>{html_lib.escape(e['nombre'])}</b></td>"
            f"<td>{html_lib.escape(e['cargo'])}</td><td>{html_lib.escape(e['sucursal_nombre'])}</td>"
            f"<td class='actions-cell'>"
            f"<button type='button' class='btn btn-sm btn-secondary' "
            f"data-id='{e['id_empleado']}' "
            f"data-nombre='{html_lib.escape(e['nombre'], quote=True)}' "
            f"data-cargo='{html_lib.escape(e['cargo'], quote=True)}' "
            f"data-sucursal='{e['id_sucursal']}' "
            f"onclick='abrirModalEmpleado(this)'>Editar</button>"
            f"<form method='POST' action='/' class='inline-form'>"
            f"<input type='hidden' name='accion' value='eliminar_empleado'>"
            f"<input type='hidden' name='tab_retorno' value='entidades'>"
            f"<input type='hidden' name='id_empleado' value='{e['id_empleado']}'>"
            f"<button type='submit' class='btn btn-sm btn-danger'>Eliminar</button>"
            f"</form></td></tr>"
            for e in empleados
        ])

        filas_clientes = "".join([
            f"<tr><td>#{c['id_cliente']}</td><td><b>{html_lib.escape(c['nombre'])}</b></td>"
            f"<td class='actions-cell'>"
            f"<button type='button' class='btn btn-sm btn-secondary' "
            f"data-id='{c['id_cliente']}' "
            f"data-nombre='{html_lib.escape(c['nombre'], quote=True)}' "
            f"onclick='abrirModalCliente(this)'>Editar</button>"
            f"<form method='POST' action='/' class='inline-form'>"
            f"<input type='hidden' name='accion' value='eliminar_cliente'>"
            f"<input type='hidden' name='tab_retorno' value='entidades'>"
            f"<input type='hidden' name='id_cliente' value='{c['id_cliente']}'>"
            f"<button type='submit' class='btn btn-sm btn-danger'>Eliminar</button>"
            f"</form></td></tr>"
            for c in clientes
        ])

        filas_proveedores = "".join([
            f"<tr><td>#{pr['id_proveedor']}</td><td><b>{html_lib.escape(pr['nombre'])}</b></td>"
            f"<td>{html_lib.escape(pr['telefono'])}</td>"
            f"<td class='actions-cell'>"
            f"<button type='button' class='btn btn-sm btn-secondary' "
            f"data-id='{pr['id_proveedor']}' "
            f"data-nombre='{html_lib.escape(pr['nombre'], quote=True)}' "
            f"data-telefono='{html_lib.escape(pr['telefono'], quote=True)}' "
            f"onclick='abrirModalProveedor(this)'>Editar</button>"
            f"<form method='POST' action='/' class='inline-form'>"
            f"<input type='hidden' name='accion' value='eliminar_proveedor'>"
            f"<input type='hidden' name='tab_retorno' value='entidades'>"
            f"<input type='hidden' name='id_proveedor' value='{pr['id_proveedor']}'>"
            f"<button type='submit' class='btn btn-sm btn-danger'>Eliminar</button>"
            f"</form></td></tr>"
            for pr in proveedores
        ])

        filas_categorias = "".join([
            f"<tr><td>#{cat['id_categoria']}</td><td><b>{html_lib.escape(cat['nombre'])}</b></td>"
            f"<td>{html_lib.escape(cat['descripcion'])}</td>"
            f"<td class='actions-cell'>"
            f"<button type='button' class='btn btn-sm btn-secondary' "
            f"data-id='{cat['id_categoria']}' "
            f"data-nombre='{html_lib.escape(cat['nombre'], quote=True)}' "
            f"data-descripcion='{html_lib.escape(cat['descripcion'], quote=True)}' "
            f"onclick='abrirModalCategoria(this)'>Editar</button>"
            f"<form method='POST' action='/' class='inline-form'>"
            f"<input type='hidden' name='accion' value='eliminar_categoria'>"
            f"<input type='hidden' name='tab_retorno' value='entidades'>"
            f"<input type='hidden' name='id_categoria' value='{cat['id_categoria']}'>"
            f"<button type='submit' class='btn btn-sm btn-danger'>Eliminar</button>"
            f"</form></td></tr>"
            for cat in categorias
        ])

        reemplazos = {
            "{{NOTIFICACIONES}}": notificaciones,
            "{{TAB_ACTIVA}}": html_lib.escape(tab_activa),
            "{{KPI_TOTAL_PROD}}": str(stats_prod["total_productos"]),
            "{{KPI_PRECIO_PROM}}": str(stats_prod["precio_promedio"]),
            "{{KPI_PRECIO_MIN}}": str(stats_prod["producto_mas_barato"]),
            "{{KPI_PRECIO_MAX}}": str(stats_prod["producto_mas_caro"]),
            "{{KPI_TOTAL_VENTAS}}": str(stats_ven["total_ventas"]),
            "{{KPI_INGRESOS_TOTALES}}": str(stats_ven["ingresos_totales"]),
            "{{OPCIONES_SUCURSAL}}": op_sucursal,
            "{{OPCIONES_EMPLEADO}}": op_empleado,
            "{{OPCIONES_CLIENTE}}": op_cliente,
            "{{OPCIONES_PRODUCTO}}": op_producto,
            "{{OPCIONES_PROVEEDOR}}": op_proveedor,
            "{{OPCIONES_CATEGORIA}}": op_categoria,
            "{{OPCIONES_FILTRO_SUC}}": op_filtro_suc,
            "{{OPCIONES_FILTRO_ALERTA}}": op_filtro_alerta,
            "{{FILAS_INVENTARIO}}": filas_inv,
            "{{FILAS_CATALOGO_PROD}}": filas_catalogo_prod,
            "{{FILAS_VENTAS}}": filas_ven,
            "{{FILAS_RECIBOS}}": filas_recibos,
            "{{FILAS_SIN_VENTA}}": filas_sin,
            "{{FILAS_CTE}}": filas_cte,
            "{{FILAS_SUCURSALES}}": filas_sucursales,
            "{{FILAS_EMPLEADOS}}": filas_empleados,
            "{{FILAS_CLIENTES}}": filas_clientes,
            "{{FILAS_PROVEEDORES}}": filas_proveedores,
            "{{FILAS_CATEGORIAS}}": filas_categorias,
            "{{JSON_RECIBOS}}": json.dumps(recibos_por_venta, ensure_ascii=False)
        }

        for clave, valor in reemplazos.items():
            plantilla = plantilla.replace(clave, valor)

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(plantilla.encode("utf-8"))


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Mr5Handler) as httpd:
        print(f"Servidor activo en http://localhost:{PORT}")
        httpd.serve_forever()