DROP DATABASE IF EXISTS mr5;
CREATE DATABASE mr5 CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE mr5;

CREATE TABLE PROVEEDOR (
    id_proveedor INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    PRIMARY KEY (id_proveedor)
) ENGINE = InnoDB;

CREATE TABLE CATEGORIA (
    id_categoria INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    PRIMARY KEY (id_categoria),
    CONSTRAINT uq_categoria_nombre UNIQUE (nombre)
) ENGINE = InnoDB;

CREATE TABLE SUCURSAL (
    id_sucursal INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(255) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    PRIMARY KEY (id_sucursal)
) ENGINE = InnoDB;

CREATE TABLE CLIENTE (
    id_cliente INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    PRIMARY KEY (id_cliente)
) ENGINE = InnoDB;

CREATE TABLE PRODUCTO (
    id_producto INT NOT NULL AUTO_INCREMENT,
    id_proveedor INT NOT NULL,
    id_categoria INT NOT NULL,
    codigo_barras VARCHAR(50),
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id_producto),
    CONSTRAINT uq_producto_codigo UNIQUE (codigo_barras),
    CONSTRAINT ck_producto_precio CHECK (precio > 0),
    CONSTRAINT fk_producto_proveedor FOREIGN KEY (id_proveedor)
        REFERENCES PROVEEDOR (id_proveedor) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_producto_categoria FOREIGN KEY (id_categoria)
        REFERENCES CATEGORIA (id_categoria) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE TABLE EMPLEADO (
    id_empleado INT NOT NULL AUTO_INCREMENT,
    id_sucursal INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    cargo VARCHAR(50) NOT NULL,
    PRIMARY KEY (id_empleado),
    CONSTRAINT fk_empleado_sucursal FOREIGN KEY (id_sucursal)
        REFERENCES SUCURSAL (id_sucursal) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE TABLE INVENTARIO (
    id_sucursal INT NOT NULL,
    id_producto INT NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    PRIMARY KEY (id_sucursal, id_producto),
    CONSTRAINT ck_inventario_stock CHECK (stock >= 0),
    CONSTRAINT fk_inventario_sucursal FOREIGN KEY (id_sucursal)
        REFERENCES SUCURSAL (id_sucursal) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_inventario_producto FOREIGN KEY (id_producto)
        REFERENCES PRODUCTO (id_producto) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE TABLE VENTA (
    id_venta INT NOT NULL AUTO_INCREMENT,
    id_sucursal INT NOT NULL,
    id_empleado INT NOT NULL,
    id_cliente INT NOT NULL,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metodo_pago VARCHAR(20) NOT NULL,
    PRIMARY KEY (id_venta),
    CONSTRAINT ck_venta_pago CHECK (metodo_pago IN ('EFECTIVO', 'QR')),
    CONSTRAINT fk_venta_sucursal FOREIGN KEY (id_sucursal)
        REFERENCES SUCURSAL (id_sucursal) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_venta_empleado FOREIGN KEY (id_empleado)
        REFERENCES EMPLEADO (id_empleado) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_venta_cliente FOREIGN KEY (id_cliente)
        REFERENCES CLIENTE (id_cliente) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE TABLE DETALLE_VENTA (
    id_venta INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id_venta, id_producto),
    CONSTRAINT ck_detalle_cantidad CHECK (cantidad > 0),
    CONSTRAINT ck_detalle_precio CHECK (precio_unitario > 0),
    CONSTRAINT fk_detalle_venta FOREIGN KEY (id_venta)
        REFERENCES VENTA (id_venta) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_detalle_producto FOREIGN KEY (id_producto)
        REFERENCES PRODUCTO (id_producto) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE INDEX idx_producto_nombre ON PRODUCTO(nombre);
CREATE INDEX idx_venta_fecha ON VENTA(fecha_hora);
CREATE INDEX idx_venta_cliente ON VENTA(id_cliente);

START TRANSACTION;

INSERT INTO PROVEEDOR (id_proveedor, nombre, telefono) VALUES
    (1, 'Distribuidora Norte S.R.L.', '71011223'),
    (2, 'Importadora Escolar Papelbol', '72144556'),
    (3, 'Plásticos del Oriente S.A.', '33456789'),
    (4, 'Mayorista Novedades Cruz', '76099887');

INSERT INTO CATEGORIA (id_categoria, nombre, descripcion) VALUES
    (1, 'Limpieza', 'Artículos para el aseo y limpieza del hogar.'),
    (2, 'Útiles escolares', 'Cuadernos, mochilas, lápices y material escolar.'),
    (3, 'Artículos plásticos', 'Baldes, bañadores, tapers y organizadores.'),
    (4, 'Novedades y Bazar', 'Artículos variados de regalo y uso doméstico.');

INSERT INTO SUCURSAL (id_sucursal, nombre, direccion, telefono) VALUES
    (1, 'Sucursal Centro', 'Calle Libertad #245, Zona Central', '33311001'),
    (2, 'Sucursal Mercado', 'Av. Grigotá #890, Comercial Chiriguano', '33322002');

INSERT INTO CLIENTE (id_cliente, nombre) VALUES
    (1, 'Ana García'),
    (2, 'Carlos Mamani'),
    (3, 'María López'),
    (4, 'Pedro Rojas');

INSERT INTO PRODUCTO (id_producto, id_proveedor, id_categoria, codigo_barras, nombre, precio) VALUES
    (1, 1, 1, '7770001001', 'Escoba plástica modelo A', 15.00),
    (2, 2, 2, '7770002002', 'Cuaderno anillado 100 hojas', 8.00),
    (3, 2, 2, '7770003003', 'Mochila escolar impermeable azul', 100.00),
    (4, 3, 3, '7770004004', 'Balde plástico reforzado 20L', 25.00),
    (5, 3, 3, '7770005005', 'Caja organizadora transparente 40L', 65.00),
    (6, 4, 4, '7770006006', 'Termo acero inoxidable 1L', 85.00);

INSERT INTO EMPLEADO (id_empleado, id_sucursal, nombre, cargo) VALUES
    (1, 1, 'Luis Peñaranda', 'Atención de ventas'),
    (2, 2, 'Marta Soliz', 'Encargada de local'),
    (3, 1, 'Jorge Flores', 'Encargado de local'),
    (4, 2, 'Sofía Vargas', 'Atención de ventas');

INSERT INTO INVENTARIO (id_sucursal, id_producto, stock) VALUES
    (1, 1, 20), (1, 2, 50), (1, 3, 10), (1, 4, 15), (1, 5, 8),  (1, 6, 12),
    (2, 1, 14), (2, 2, 35), (2, 3, 6),  (2, 4, 22), (2, 5, 10), (2, 6, 5);

INSERT INTO VENTA (id_venta, id_sucursal, id_empleado, id_cliente, fecha_hora, metodo_pago) VALUES
    (1, 1, 1, 1, '2026-10-20 10:00:00', 'QR'),
    (2, 2, 2, 2, '2026-10-20 11:30:00', 'EFECTIVO'),
    (3, 1, 3, 1, '2026-10-22 15:45:00', 'EFECTIVO'),
    (4, 2, 4, 3, '2026-10-25 17:10:00', 'QR');

INSERT INTO DETALLE_VENTA (id_venta, id_producto, cantidad, precio_unitario) VALUES
    (1, 1, 2, 15.00),
    (1, 2, 3, 8.00),
    (2, 3, 1, 100.00),
    (3, 4, 2, 25.00),
    (3, 1, 1, 15.00),
    (4, 5, 2, 65.00);

COMMIT;

CREATE OR REPLACE VIEW V_INVENTARIO_DETALLADO AS
SELECT 
    s.nombre AS sucursal,
    p.codigo_barras,
    p.nombre AS producto,
    c.nombre AS categoria,
    pr.nombre AS proveedor,
    p.precio,
    i.stock,
    CASE 
        WHEN i.stock <= 6 THEN 'STOCK CRÍTICO'
        WHEN i.stock <= 15 THEN 'STOCK MEDIO'
        ELSE 'ABASTECIDO'
    END AS estado_alerta
FROM INVENTARIO i
INNER JOIN SUCURSAL s ON i.id_sucursal = s.id_sucursal
INNER JOIN PRODUCTO p ON i.id_producto = p.id_producto
INNER JOIN CATEGORIA c ON p.id_categoria = c.id_categoria
INNER JOIN PROVEEDOR pr ON p.id_proveedor = pr.id_proveedor;

CREATE OR REPLACE VIEW V_RESUMEN_VENTAS AS
SELECT 
    v.id_venta,
    v.fecha_hora,
    s.nombre AS sucursal,
    e.nombre AS empleado,
    cl.nombre AS cliente,
    v.metodo_pago,
    SUM(dv.cantidad * dv.precio_unitario) AS total_venta
FROM VENTA v
INNER JOIN SUCURSAL s ON v.id_sucursal = s.id_sucursal
INNER JOIN EMPLEADO e ON v.id_empleado = e.id_empleado
INNER JOIN CLIENTE cl ON v.id_cliente = cl.id_cliente
INNER JOIN DETALLE_VENTA dv ON v.id_venta = dv.id_venta
GROUP BY v.id_venta, v.fecha_hora, s.nombre, e.nombre, cl.nombre, v.metodo_pago;

SELECT 
    COUNT(*) AS total_productos,
    ROUND(AVG(precio), 2) AS precio_promedio,
    MIN(precio) AS producto_mas_barato,
    MAX(precio) AS producto_mas_caro
FROM PRODUCTO;

SELECT 
    v.id_venta,
    v.fecha_hora,
    cl.nombre AS cliente,
    s.nombre AS sucursal,
    p.nombre AS producto,
    dv.cantidad,
    dv.precio_unitario,
    (dv.cantidad * dv.precio_unitario) AS subtotal,
    v.metodo_pago
FROM VENTA v
INNER JOIN CLIENTE cl ON v.id_cliente = cl.id_cliente
INNER JOIN SUCURSAL s ON v.id_sucursal = s.id_sucursal
INNER JOIN DETALLE_VENTA dv ON v.id_venta = dv.id_venta
INNER JOIN PRODUCTO p ON dv.id_producto = p.id_producto
ORDER BY v.id_venta;

SELECT 
    p.id_producto,
    p.codigo_barras,
    p.nombre AS producto_sin_ventas,
    p.precio
FROM PRODUCTO p
LEFT JOIN DETALLE_VENTA dv ON p.id_producto = dv.id_producto
WHERE dv.id_venta IS NULL;

WITH totales_por_venta AS (
    SELECT 
        v.id_venta,
        v.id_cliente,
        cl.nombre AS cliente,
        v.fecha_hora,
        SUM(dv.cantidad * dv.precio_unitario) AS monto_venta
    FROM VENTA v
    INNER JOIN CLIENTE cl ON v.id_cliente = cl.id_cliente
    INNER JOIN DETALLE_VENTA dv ON v.id_venta = dv.id_venta
    GROUP BY v.id_venta, v.id_cliente, cl.nombre, v.fecha_hora
)
SELECT 
    id_venta,
    cliente,
    fecha_hora,
    monto_venta,
    SUM(monto_venta) OVER (
        PARTITION BY id_cliente 
        ORDER BY fecha_hora ASC
    ) AS acumulado_cliente,
    DENSE_RANK() OVER (
        ORDER BY monto_venta DESC
    ) AS ranking_mayor_venta
FROM totales_por_venta;


START TRANSACTION;

INSERT INTO VENTA (id_venta, id_sucursal, id_empleado, id_cliente, fecha_hora, metodo_pago)
VALUES (5, 1, 1, 4, NOW(), 'QR');

INSERT INTO DETALLE_VENTA (id_venta, id_producto, cantidad, precio_unitario)
VALUES (5, 2, 5, 8.00);

UPDATE INVENTARIO 
SET stock = stock - 5 
WHERE id_sucursal = 1 AND id_producto = 2;

COMMIT;

SELECT * FROM V_INVENTARIO_DETALLADO;
SELECT * FROM V_RESUMEN_VENTAS;