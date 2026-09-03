# 🏢 Primer Avance: Requisitos y Modelo Conceptual

Aquí se documenta la recolección de requisitos obtenida de la tienda y el diseño inicial de la base de datos, siguiendo la estructura formal del proyecto.

## 1) Narración del cliente (requisitos en lenguaje natural)
"Soy el dueño de la tienda de novedades y plásticos 'Mr. 5'. Tenemos varias sucursales y necesitamos un sistema para gestionar nuestra mercadería, proveedores y las salidas diarias. Aunque nuestros productos sí traen código de barras de fábrica, actualmente anotamos el inventario a mano, lo que hace que controlar el stock y los precios sea un caos. Un proveedor nos surte varios productos, y registramos cada producto con un proveedor principal para saber a quién reclamarle cuando falta mercadería. Las ventas aquí son rápidas y al contado; una regla estricta es que **no se fía a nadie**. Como somos un comercio informal y de paso, la gente compra de forma anónima y rápida, no les pedimos datos personales. Lo que sí necesitamos con urgencia es que el sistema registre cada "Venta" o transacción que ocurre en el mostrador de forma automática, anotando la fecha, qué artículos exactos se llevaron en ese momento y la cantidad, para así poder descontarlos del inventario correctamente."

## 2) Suposiciones (decisiones para aclarar ambigüedades)
* Como el negocio es de ventas rápidas y anónimas, no existirá la entidad "Cliente". En su lugar, el modelo se centrará en registrar el evento de la `VENTA` (como si fuera un ticket virtual interno).
* Aunque la mayoría de productos tienen código de barras, el sistema generará un `id_producto` numérico interno. Esto es porque a veces llegan artículos plásticos sueltos sin etiqueta. El código de barras original se guardará como un dato opcional.
* Se asume estrictamente que no existe el crédito o "fiado"; toda transacción de venta registrada se considera pagada al contado en el momento.
* Una Venta (ticket) puede incluir varios productos distintos, y un mismo producto se vende en muchas ventas diferentes (N:M). Esta asociación guardará la cantidad de artículos salientes.

## 3) Identificación de Entidades, Atributos, Tipos y PK
Usamos notación UML simplificada de tres compartimentos para cada entidad:

┌─────────────┐
│ PROVEEDOR   │
├─────────────┤
│ + id_proveedor: INTEGER PK (AUTOINCREMENT)
│ + nombre: VARCHAR(100) NOT NULL
│ + telefono: VARCHAR(20)
└─────────────┘

┌─────────────┐
│ PRODUCTO    │
├─────────────┤
│ + id_producto: INTEGER PK (AUTOINCREMENT)
│ + id_proveedor: INTEGER FK → PROVEEDOR(id_proveedor) NOT NULL
│ + codigo_barras: VARCHAR(50) UNIQUE
│ + nombre: VARCHAR(100) NOT NULL
│ + precio: DECIMAL(8,2) CHECK (precio > 0) NOT NULL
│ + stock: INTEGER CHECK (stock >= 0) DEFAULT 0
└─────────────┘

┌─────────────┐
│ VENTA       │
├─────────────┤
│ + id_venta: INTEGER PK (AUTOINCREMENT)
│ + fecha: DATE DEFAULT CURRENT_DATE
└─────────────┘

┌──────────────────────┐
│ DETALLE_VENTA        │
├──────────────────────┤
│ + id_venta: INTEGER FK → VENTA(id_venta) PK parcial
│ + id_producto: INTEGER FK → PRODUCTO(id_producto) PK parcial
│ + cantidad: INTEGER DEFAULT 1 CHECK (cantidad > 0)
└──────────────────────┘

## 4) Relaciones y cardinalidades (con justificación)
* **PROVEEDOR (1) — (N) PRODUCTO**
  *Justificación:* Un proveedor distribuye múltiples productos a la tienda, pero cada producto registrado se asocia a un único proveedor principal para mantener el canal de reclamos ordenado.
* **VENTA (N) — (M) PRODUCTO (mediante la tabla asociativa DETALLE_VENTA)**
  *Justificación:* Una transacción de venta en el mostrador puede incluir varios productos diferentes en un mismo momento. A su vez, un producto específico del inventario es despachado en muchas ventas a lo largo del tiempo. La tabla asociativa almacena la cantidad exacta de artículos llevados en ese ticket.

## 5) Reglas de negocio y restricciones importantes
* **Cero crédito (No se fía):** El sistema asume que el 100% de las ventas son pagadas al contado en el mostrador. 
* **Stock no negativo:** El inventario nunca puede ser menor a cero (`CHECK stock >= 0`). El sistema deberá impedir una venta si la cantidad solicitada supera al stock.
* **Relación estricta de proveedores:** No se puede ingresar un nuevo producto al catálogo si no se le asocia un proveedor existente (`FK NOT NULL`).

## 6) DER (Diagrama Entidad-Relación) — Notación Sirena

A continuación se presenta el modelo conceptual generado automáticamente, además del archivo original adjunto:

```mermaid
erDiagram
    VENTA ||--o{ DETALLE_VENTA : "contiene"
    PRODUCTO ||--o{ DETALLE_VENTA : "es despachado en"
    PROVEEDOR ||--|{ PRODUCTO : "surte"

    VENTA {
        INTEGER id_venta PK
        DATE fecha
    }
    
    PROVEEDOR {
        INTEGER id_proveedor PK
        VARCHAR nombre
        VARCHAR telefono
    }
    
    PRODUCTO {
        INTEGER id_producto PK
        INTEGER id_proveedor FK
        VARCHAR codigo_barras
        VARCHAR nombre
        DECIMAL precio
        INTEGER stock
    }
    
    DETALLE_VENTA {
        INTEGER id_venta PK,FK
        INTEGER id_producto PK,FK
        INTEGER cantidad
    }
