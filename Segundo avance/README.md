# FASE II — SEGUNDO AVANCE

## 9) Implementación Física en SQL (`script_mr5_completo.sql`)

El archivo [`script_mr5_completo.sql`](./script_mr5_completo.sql) implementa el 100% de los contenidos prácticos de las Unidades III y IV sobre **MySQL 8.4** usando el motor transaccional `InnoDB`:

1. **DDL y Restricciones Relacionales:**
   - Claves primarias simples (`AUTO_INCREMENT`) y compuestas en `INVENTARIO (id_sucursal, id_producto)` y `DETALLE_VENTA (id_venta, id_producto)`.
   - Restricciones de unicidad: `UNIQUE (nombre)` en `CATEGORIA` y `UNIQUE (codigo_barras)` en `PRODUCTO`.
   - Restricciones de dominio (`CHECK`): `precio > 0`, `stock >= 0`, `cantidad > 0`, `precio_unitario > 0` y `metodo_pago IN ('EFECTIVO', 'QR')`.
   - Integridad referencial (`FOREIGN KEY`): Reglas `ON DELETE RESTRICT ON UPDATE CASCADE` en las relaciones maestras para impedir borrar productos, clientes, empleados o sucursales con historial, y `ON DELETE CASCADE` en `DETALLE_VENTA -> VENTA` para limpiar el desglose si se anula una venta.
2. **Diseño Físico con Índices (Unidad 4.10):**
   - `idx_producto_nombre` sobre `PRODUCTO(nombre)`.
   - `idx_venta_fecha` sobre `VENTA(fecha_hora)`.
   - `idx_venta_cliente` sobre `VENTA(id_cliente)`.
3. **Vistas Almacenadas (Unidad 4.6):**
   - `V_INVENTARIO_DETALLADO`: Cruza 4 tablas (`INVENTARIO`, `SUCURSAL`, `PRODUCTO`, `CATEGORIA`, `PROVEEDOR`) y clasifica el stock mediante `CASE WHEN` en `STOCK CRÍTICO`, `STOCK MEDIO` y `ABASTECIDO`.
   - `V_RESUMEN_VENTAS`: Agrupa las ventas confirmadas con `GROUP BY` y calcula el `total_venta` con `SUM(cantidad * precio_unitario)`.
4. **Consultas Avanzadas (Unidad 4.5, 4.8 y 4.9):**
   - Estadísticas del catálogo con `COUNT(*)`, `ROUND(AVG(precio), 2)`, `MIN(precio)` y `MAX(precio)`.
   - Desglose de recibos con `INNER JOIN` de 4 tablas.
   - Detección de productos sin ventas registradas mediante `LEFT JOIN ... WHERE dv.id_venta IS NULL`.
   - Consulta analítica con **Expresión de Tabla Común (`WITH totales_por_venta AS (...)`)** y **Funciones de Ventana** (`SUM(monto_venta) OVER (PARTITION BY id_cliente ORDER BY fecha_hora ASC)` para el acumulado por cliente y `DENSE_RANK() OVER (ORDER BY monto_venta DESC)` para el ranking de ventas).
5. **Transacciones ACID (Unidad 4.3):**
   - Bloque `START TRANSACTION ... COMMIT` que inserta la venta, registra el detalle y descuenta el stock en `INVENTARIO`.

---

## 10) Aplicación Web Modular en Python (`app.py`, `index.html`, `styles.css`, `script.js`)

Para conectar la base de datos física con una interfaz gráfica de usuario, el proyecto incluye una aplicación web modular en Python que se comunica en tiempo real con MySQL 8.4:

```text
├── README.md                  # Documentación completa del proyecto (Avances 1 y 2)
├── miproyecto.drawio.pdf      # Diagrama Entidad-Relación en notación de Chen
├── script_mr5_completo.sql    # Script DDL, DML, Vistas, Índices, CTE y Transacciones
├── app.py                     # Servidor HTTP en Python y lógica transaccional MySQL
├── index.html                 # Interfaz de usuario dividida en 4 módulos operativos
├── styles.css                 # Hoja de estilos corporativa e impresión de recibos
└── script.js                  # Lógica de pestañas, modales de edición y recibo de venta
```

### Funcionalidades implementadas en la Interfaz Web:
- **Punto de Venta Transaccional (`START TRANSACTION`, `FOR UPDATE`, `COMMIT`, `ROLLBACK`):** Permite registrar ventas con uno o varios artículos validando el stock real en la sucursal elegida mediante bloqueo de fila (`FOR UPDATE`), congelando el precio unitario en `DETALLE_VENTA` y descontando automáticamente las existencias en `INVENTARIO`. Si el stock es insuficiente, ejecuta `ROLLBACK` y muestra la alerta en pantalla.
- **Anulación Transaccional de Ventas:** Permite anular una operación restituyendo automáticamente las unidades a `INVENTARIO` de esa sucursal y eliminando la cabecera en `VENTA` (aplicando `ON DELETE CASCADE` sobre `DETALLE_VENTA`).
- **Emisión e Impresión de Nota de Venta:** Genera el comprobante detallado de cada venta con su desglose de productos y subtotales.
- **CRUD Completo sobre las Entidades Maestras:** Permite crear, editar (`UPDATE` mediante ventana modal) y eliminar (`DELETE` validando `ON DELETE RESTRICT`) registros en `PRODUCTO`, `SUCURSAL`, `EMPLEADO`, `PROVEEDOR`, `CATEGORIA` y `CLIENTE`, además de reponer stock en `INVENTARIO`.
- **Panel de Reportes en Tiempo Real:** Visualiza las tarjetas KPI de agregación, los filtros dinámicos sobre `V_INVENTARIO_DETALLADO`, el ranking con `CTE + Funciones de Ventana` y los artículos sin ventas con `LEFT JOIN ... IS NULL`.

### Cómo ejecutar el proyecto localmente:

1. **Cargar la base de datos en MySQL 8.4:**
   Abrir `script_mr5_completo.sql` en **MySQL Workbench** y ejecutarlo con el botón **Run**, o desde la terminal:
   ```powershell
   cmd /c '"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -u root -p --default-character-set=utf8mb4 < script_mr5_completo.sql'
   ```
2. **Instalar el conector oficial de MySQL para Python:**
   ```powershell
   pip install mysql-connector-python
   ```
3. **Iniciar el servidor web:**
   ```powershell
   python app.py
   ```
4. **Abrir en el navegador:**
   Ingresar a `http://localhost:8080`
