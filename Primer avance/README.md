# 🏢 Primer Avance: Requisitos y Modelo Conceptual

Aquí se documenta la recolección de requisitos obtenida de la tienda y el diseño inicial de la base de datos, siguiendo la estructura formal del proyecto.

## 1) Narración del cliente (requisitos en lenguaje natural)
"Soy el dueño de la tienda de novedades y plásticos 'Mr. 5'. Necesitamos un sistema para gestionar nuestra mercadería, proveedores y las ventas diarias. Aunque nuestros productos plásticos sí traen código de barras de fábrica, actualmente anotamos todo a mano en cuadernos, lo que hace que controlar el stock y los precios sea un caos y muy lento. Un proveedor nos surte varios productos, y registramos cada producto con un proveedor principal para saber a quién reclamarle cuando falta mercadería. Las ventas aquí son rápidas y al contado; una regla estricta es que **no se fía a nadie**. Un cliente se lleva varios productos en una compra. Como somos un comercio informal, no emitimos facturas, pero anotamos el Nombre y Carnet de Identidad (CI) de los clientes recurrentes que nos piden un recibito de control, junto con qué se llevaron, la cantidad y la fecha."

## 2) Suposiciones (decisiones para aclarar ambigüedades)
* Como el negocio es informal y no emite facturas con NIT, a los clientes que piden recibo los identificaremos por su Carnet de Identidad (`CI`).
* Aunque los productos tienen código de barras, el sistema generará un `id_producto` numérico interno para mayor velocidad en la base de datos, pero guardaremos el código de barras original como un dato extra.
* Se asume estrictamente que no existe el crédito o "fiado"; toda compra registrada se considera pagada al contado en el momento.
* Una compra incluye varios productos y un producto es comprado por varios clientes (N:M). Esta asociación guarda la cantidad vendida y la fecha.

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
│ CLIENTE     │
├─────────────┤
│ + ci_cliente: VARCHAR(15) PK (Carnet)
│ + nombre: VARCHAR(100) NOT NULL
└─────────────┘

┌──────────────────────┐
│ COMPRA (CLIENTE_PROD)│
├──────────────────────┤
│ + ci_cliente: VARCHAR(15) FK → CLIENTE(ci_cliente) PK parcial
│ + id_producto: INTEGER FK → PRODUCTO(id_producto) PK parcial
│ + fecha: DATE DEFAULT CURRENT_DATE PK parcial
│ + cantidad: INTEGER DEFAULT 1 CHECK (cantidad > 0)
└──────────────────────┘

## 4) Relaciones y cardinalidades (con justificación)
* **PROVEEDOR (1) — (N) PRODUCTO**
  *Justificación:* Un proveedor distribuye múltiples productos a la tienda, pero cada producto registrado en la base de datos se asocia a un único proveedor principal para mantener un canal claro de reclamos.
* **CLIENTE (N) — (M) PRODUCTO (mediante la tabla asociativa COMPRA)**
  *Justificación:* Un cliente puede comprar varios productos en una sola visita. A su vez, un producto del inventario es comprado por muchos clientes. La tabla asociativa almacena los detalles específicos del evento: la cantidad de artículos llevados y la fecha.

## 5) Reglas de negocio y restricciones importantes
* **Cero crédito (No se fía):** El sistema asume que el 100% de las transacciones registradas son pagadas al contado. No existen cuentas por cobrar.
* **Stock no negativo:** El inventario nunca puede ser menor a cero (`CHECK stock >= 0`). 
* **Relación estricta de proveedores:** No se puede ingresar un nuevo producto al catálogo si no se le asocia un proveedor existente (`FK NOT NULL`).

## 6) DER (Diagrama Entidad-Relación) — Notación Sirena

A continuación se presenta el modelo conceptual generado automáticamente, además del archivo original adjunto:

```mermaid
erDiagram
    CLIENTE ||--o{ COMPRA : "realiza"
    PRODUCTO ||--o{ COMPRA : "es incluido en"
    PROVEEDOR ||--|{ PRODUCTO : "surte"

    CLIENTE {
        VARCHAR ci_cliente PK
        VARCHAR nombre
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
    
    COMPRA {
        VARCHAR ci_cliente PK,FK
        INTEGER id_producto PK,FK
        DATE fecha PK
        INTEGER cantidad
    }



---

## 📎 Anexo: Modelo Conceptual Original

Aquí puedes ver y descargar el diagrama original elaborado en Draw.io con todos los detalles visuales de las entidades y relaciones:

[![Ver Diagrama](https://img.shields.io/badge/📥_CLIC_AQUÍ_PARA_VER_EL_DIAGRAMA-Draw.io_/_PDF-0052cc?style=for-the-badge)](./Diagrama.drawio.pdf)
