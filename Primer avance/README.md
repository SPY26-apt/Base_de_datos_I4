## 📁 Proyecto: Sistema de Control de Inventario y Ventas ("Mr. 5")

### 1. Descripción de la Problemática

La tienda "Mr. 5" es un comercio minorista dedicado a la venta de artículos plásticos, útiles escolares y novedades.

Actualmente, el control del inventario se realiza de forma manual mediante cuadernos y anotaciones, lo que genera diferencias entre el stock registrado y el stock real, dificultades para conocer las existencias disponibles en cada sucursal y poco control sobre las ventas realizadas diariamente.

Como las ventas en mostrador son rápidas y al contado, el negocio necesita un sistema ágil que permita registrar cada transacción y descontar automáticamente los productos vendidos del inventario de la sucursal correspondiente, sin ralentizar la atención solicitando datos personales innecesarios a los compradores.

Por este motivo, se propone desarrollar una base de datos que permita administrar proveedores, categorías, productos, sucursales, inventarios, empleados y ventas, manteniendo información actualizada y consistente.


### 2. Diseño de la Solución y Suposiciones Clave

Para resolver el problema identificado, el sistema se diseña bajo las siguientes reglas de negocio:

* **Venta rápida y anónima:**  
  Para evitar cuellos de botella durante la atención, no se registran datos personales del comprador. La transacción de `VENTA` constituye el elemento central del proceso comercial.

* **Cero créditos:**  
  No se realizan ventas fiadas o a crédito. Toda venta registrada se considera pagada completamente al momento de realizarse.

* **Manejo de sucursales e inventario:**  
  El negocio cuenta con varias sucursales. Por lo tanto, el stock no se administra como una cantidad global, sino mediante un inventario específico para cada combinación de producto y sucursal.

* **Control de ventas y empleados:**  
  Cada venta registra qué empleado realizó la operación y en qué sucursal ocurrió, permitiendo identificar al responsable de cada transacción y generar reportes por empleado y sucursal.

* **Precio histórico:**  
  El precio de venta de un producto puede variar con el tiempo. Por este motivo, `DETALLE_VENTA` almacena el `precio_unitario` aplicado en el momento exacto de cada transacción.

* **Control de stock:**  
  El inventario nunca podrá presentar cantidades negativas. Antes de confirmar una venta, deberá verificarse que exista stock suficiente del producto en la sucursal correspondiente.


## 3) Identificación de Entidades, Atributos, Tipos, PK y FK

```text
┌───────────────────────────────────────────────────────────┐
│ PROVEEDOR                                                 │
├───────────────────────────────────────────────────────────┤
│ + id_proveedor: INTEGER PK (AUTOINCREMENT)                │
│ + nombre: VARCHAR(100) NOT NULL                           │
│ + telefono: VARCHAR(20)                                   │
└───────────────────────────────────────────────────────────┘


┌───────────────────────────────────────────────────────────┐
│ CATEGORIA                                                 │
├───────────────────────────────────────────────────────────┤
│ + id_categoria: INTEGER PK (AUTOINCREMENT)                │
│ + nombre: VARCHAR(100) UNIQUE NOT NULL                    │
│ + descripcion: VARCHAR(255)                               │
└───────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│ PRODUCTO                                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ + id_producto: INTEGER PK (AUTOINCREMENT)                                    │
│ + id_proveedor: INTEGER FK → PROVEEDOR(id_proveedor) NOT NULL                │
│ + id_categoria: INTEGER FK → CATEGORIA(id_categoria) NOT NULL                │
│ + codigo_barras: VARCHAR(50) UNIQUE                                          │
│ + nombre: VARCHAR(100) NOT NULL                                              │
│ + precio: DECIMAL(10,2) NOT NULL CHECK (precio > 0)                         │
└──────────────────────────────────────────────────────────────────────────────┘


┌───────────────────────────────────────────────────────────┐
│ SUCURSAL                                                  │
├───────────────────────────────────────────────────────────┤
│ + id_sucursal: INTEGER PK (AUTOINCREMENT)                 │
│ + nombre: VARCHAR(100) NOT NULL                           │
│ + direccion: VARCHAR(255) NOT NULL                        │
│ + telefono: VARCHAR(20)                                   │
└───────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│ INVENTARIO                                                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│ + id_sucursal: INTEGER FK → SUCURSAL(id_sucursal)                            │
│ + id_producto: INTEGER FK → PRODUCTO(id_producto)                            │
│ + stock: INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)                       │
│                                                                              │
│ PK COMPUESTA: (id_sucursal, id_producto)                                     │
└──────────────────────────────────────────────────────────────────────────────┘


┌───────────────────────────────────────────────────────────┐
│ EMPLEADO                                                  │
├───────────────────────────────────────────────────────────┤
│ + id_empleado: INTEGER PK (AUTOINCREMENT)                 │
│ + nombre: VARCHAR(100) NOT NULL                           │
│ + cargo: VARCHAR(50) NOT NULL                             │
└───────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│ VENTA                                                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│ + id_venta: INTEGER PK (AUTOINCREMENT)                                       │
│ + id_sucursal: INTEGER FK → SUCURSAL(id_sucursal) NOT NULL                   │
│ + id_empleado: INTEGER FK → EMPLEADO(id_empleado) NOT NULL                   │
│ + fecha_hora: DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP                    │
│ + metodo_pago: VARCHAR(20) NOT NULL                                          │
│   CHECK (metodo_pago IN ('EFECTIVO', 'QR'))                                  │
└──────────────────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│ DETALLE_VENTA                                                                │
├──────────────────────────────────────────────────────────────────────────────┤
│ + id_venta: INTEGER FK → VENTA(id_venta)                                     │
│ + id_producto: INTEGER FK → PRODUCTO(id_producto)                            │
│ + cantidad: INTEGER NOT NULL DEFAULT 1 CHECK (cantidad > 0)                  │
│ + precio_unitario: DECIMAL(10,2) NOT NULL CHECK (precio_unitario > 0)        │
│                                                                              │
│ PK COMPUESTA: (id_venta, id_producto)                                        │
└──────────────────────────────────────────────────────────────────────────────┘
```


## 4) Relaciones y Cardinalidades

### PROVEEDOR — PRODUCTO

**PROVEEDOR (0..N) — PROVEE — (1..1) PRODUCTO**

Un proveedor puede suministrar cero o muchos productos registrados en el sistema, mientras que cada producto debe estar asociado obligatoriamente a un único proveedor principal.

Esta relación permite identificar rápidamente a qué proveedor debe realizarse un reclamo o pedido relacionado con un producto.


### CATEGORIA — PRODUCTO

**CATEGORIA (0..N) — CLASIFICA — (1..1) PRODUCTO**

Una categoría puede agrupar cero o muchos productos, mientras que cada producto pertenece obligatoriamente a una sola categoría.

Esto facilita la clasificación de los artículos y la generación de reportes por tipo de producto.


### SUCURSAL — VENTA

**SUCURSAL (0..N) — GENERA — (1..1) VENTA**

Una sucursal puede generar múltiples ventas a lo largo del tiempo.

Cada venta debe corresponder obligatoriamente a una sola sucursal, permitiendo conocer exactamente dónde ocurrió la transacción.


### EMPLEADO — VENTA

**EMPLEADO (0..N) — REGISTRA — (1..1) VENTA**

Un empleado puede registrar múltiples ventas durante su actividad laboral.

Cada venta debe tener un único empleado responsable de haber registrado la transacción.


### SUCURSAL — INVENTARIO

**SUCURSAL (0..N) — ALMACENA — (1..1) INVENTARIO**

Una sucursal puede poseer múltiples registros de inventario.

Cada registro de `INVENTARIO` pertenece obligatoriamente a una única sucursal.


### PRODUCTO — INVENTARIO

**PRODUCTO (0..N) — POSEE — (1..1) INVENTARIO**

Un producto puede encontrarse disponible en diferentes sucursales y, por lo tanto, puede participar en múltiples registros de inventario.

Cada registro de `INVENTARIO` corresponde a un único producto.

La entidad asociativa `INVENTARIO` permite resolver la relación entre `SUCURSAL` y `PRODUCTO`, almacenando el stock correspondiente a cada combinación.

La clave primaria compuesta será:

`(id_sucursal, id_producto)`


### VENTA — DETALLE_VENTA

**VENTA (1..N) — TIENE — (1..1) DETALLE_VENTA**

Una venta confirmada debe contener uno o varios registros de detalle.

Cada registro de `DETALLE_VENTA` pertenece obligatoriamente a una única venta.


### PRODUCTO — DETALLE_VENTA

**PRODUCTO (0..N) — CORRESPONDE A — (1..1) DETALLE_VENTA**

Un producto puede aparecer en múltiples ventas diferentes a lo largo del tiempo.

Cada registro de `DETALLE_VENTA` corresponde obligatoriamente a un único producto.

La entidad asociativa `DETALLE_VENTA` resuelve la relación muchos a muchos entre `VENTA` y `PRODUCTO`.

La clave primaria compuesta será:

`(id_venta, id_producto)`


## 5) Reglas de Negocio y Restricciones Importantes

* **Ventas rápidas y anónimas:**  
  No se implementa una entidad `CLIENTE`. Debido a la naturaleza rápida de las operaciones de "Mr. 5", solicitar nombre, carnet, teléfono u otros datos personales generaría retrasos innecesarios durante la atención. Las operaciones se consideran ventas a consumidor final.

* **Cero créditos:**  
  No se permite realizar ventas a crédito o fiadas. Toda venta registrada en el sistema se considera pagada completamente al momento de realizarse.

* **Métodos de pago:**  
  Los métodos de pago contemplados inicialmente son `EFECTIVO` y `QR`. Toda venta deberá registrar obligatoriamente uno de estos métodos.

* **Stock no negativo:**  
  El inventario no podrá almacenar cantidades negativas. Se aplicará la siguiente restricción:

  ```sql
  CHECK (stock >= 0)
UNIQUE
```


## 6) Modelo Conceptual: DER — Notación de Chen

En esta fase se diseña el Modelo Entidad-Relación a partir de los requerimientos del negocio, identificando las entidades principales, sus atributos, relaciones y cardinalidades antes de realizar la transformación al modelo relacional.

El modelo utiliza la notación tradicional de Chen:

* **Rectángulos:** representan las entidades.
* **Rombos:** representan las relaciones.
* **Óvalos:** representan los atributos.
* **Atributos subrayados:** representan los atributos identificadores.
* **Cardinalidades:** indican la cantidad de ocurrencias que pueden participar en cada relación.

Las entidades identificadas son:

1. `PROVEEDOR`
2. `CATEGORIA`
3. `PRODUCTO`
4. `SUCURSAL`
5. `INVENTARIO`
6. `EMPLEADO`
7. `VENTA`
8. `DETALLE_VENTA`

Las relaciones principales son:

* `PROVEEDOR` — **PROVEE** — `PRODUCTO`
* `CATEGORIA` — **CLASIFICA** — `PRODUCTO`
* `SUCURSAL` — **GENERA** — `VENTA`
* `EMPLEADO` — **REGISTRA** — `VENTA`
* `SUCURSAL` — **ALMACENA** — `INVENTARIO`
* `PRODUCTO` — **POSEE** — `INVENTARIO`
* `VENTA` — **TIENE** — `DETALLE_VENTA`
* `PRODUCTO` — **CORRESPONDE A** — `DETALLE_VENTA`

> **Nota:** En el modelo conceptual utilizando notación de Chen no es necesario representar las claves foráneas como atributos, debido a que las relaciones entre las entidades ya se encuentran expresadas mediante los rombos. Las claves foráneas aparecerán posteriormente durante la transformación al modelo relacional.

[📄 Haz clic aquí para abrir el Diagrama Conceptual en PDF](./Diagrama.drawio.pdf)
