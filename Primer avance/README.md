# 🏢 Primer Avance: Requisitos y Modelo Conceptual

Aquí se documenta la recolección de requisitos obtenida de la tienda y el diseño inicial de la base de datos, siguiendo la estructura formal del proyecto.

## 1) Narración del cliente (requisitos en lenguaje natural)
"Soy el encargado de la tienda 'Mr. 5'. Necesitamos un sistema para gestionar nuestra mercadería, nuestros proveedores y a los clientes formales. Actualmente, todo lo hacemos al ojo porque la mayoría de nuestros productos plásticos y novedades no traen código de barras de fábrica, lo que nos dificulta controlar el stock y los precios. Un proveedor nos surte de varios productos, pero para tener orden y saber a quién reclamar, registramos cada producto con un proveedor principal. Las ventas aquí son rápidas y al contado; un cliente normal se lleva varios productos distintos en una sola compra. Aunque muchos compran al paso, necesitamos anotar los datos exactos (NIT y Nombre) de los clientes que nos piden recibo o nota de venta, y registrar qué productos se llevaron, la cantidad y en qué fecha."

## 2) Suposiciones (decisiones para aclarar ambigüedades)
* Identificamos a los productos mediante un identificador interno (`id_producto` autoincrementable), asumiendo que el sistema lo generará para reemplazar la falta de códigos de barras.
* Se asume que no existe el crédito o "fiado"; toda compra registrada se considera pagada al contado en el momento.
* Registramos en el sistema únicamente a los clientes que requieren una nota o recibo formal, identificados por su NIT o carnet (`id_cliente`).
* Una compra incluye varios productos y un producto es comprado por varios clientes (N:M entre CLIENTE y PRODUCTO). Esta asociación guarda la cantidad vendida y la fecha exacta de la compra.

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
│ + nombre: VARCHAR(100) NOT NULL
│ + precio: DECIMAL(8,2) CHECK (precio > 0) NOT NULL
│ + stock: INTEGER CHECK (stock >= 0) DEFAULT 0
└─────────────┘

┌─────────────┐
│ CLIENTE     │
├─────────────┤
│ + id_cliente: VARCHAR(20) PK (NIT/CI)
│ + nombre: VARCHAR(100) NOT NULL
└─────────────┘

┌──────────────────────┐
│ COMPRA (CLIENTE_PROD)│
├──────────────────────┤
│ + id_cliente: VARCHAR(20) FK → CLIENTE(id_cliente) PK parcial
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
* **Stock no negativo:** El inventario de un producto nunca puede ser menor a cero (`CHECK stock >= 0`). 
* **Identificación obligatoria del producto:** No se pueden registrar productos sin nombre y sin precio asignado (`NOT NULL`).
* **Relación estricta de proveedores:** No se puede ingresar un nuevo producto al catálogo si no se le asocia un proveedor existente (`FK NOT NULL`).

## 6) DER (Diagrama Entidad-Relación) — Notación Sirena

A continuación se presenta el modelo conceptual generado automáticamente con Mermaid, además del archivo original adjunto:

```mermaid
erDiagram
    CLIENTE ||--o{ COMPRA : "realiza"
    PRODUCTO ||--o{ COMPRA : "es incluido en"
    PROVEEDOR ||--|{ PRODUCTO : "surte"

    CLIENTE {
        VARCHAR id_cliente PK
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
        VARCHAR nombre
        DECIMAL precio
        INTEGER stock
    }
    
    COMPRA {
        VARCHAR id_cliente PK,FK
        INTEGER id_producto PK,FK
        DATE fecha PK
        INTEGER cantidad
    }
