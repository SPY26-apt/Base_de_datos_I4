# 📁 Proyecto: Sistema de Control de Inventario y Ventas «Mr. 5»

**Universidad:** UAGRM (Universidad Autónoma Gabriel René Moreno)  
**Materia:** INF112 - Base de Datos I  
**Motor de Base de Datos:** MySQL 8.4 (InnoDB)  

---

# FASE I — PRIMER AVANCE: DISEÑO CONCEPTUAL Y REQUERIMIENTOS

## 1) Narración del cliente

Mr. 5 es un negocio dedicado a la venta de artículos plásticos, útiles escolares, productos de limpieza y otras novedades. Cuenta con dos sucursales, donde la atención está a cargo de personas que trabajan en el negocio, incluidos familiares.

Actualmente, las existencias y las ventas se controlan mediante cuadernos y anotaciones. Esto dificulta saber cuántas unidades de cada producto quedan en cada local y puede generar diferencias entre lo anotado y lo que realmente está disponible.

El negocio necesita registrar sus productos, clasificarlos por categorías e identificar al proveedor principal de cada uno. También necesita conocer las existencias por sucursal, registrar las ventas y saber qué persona atendió cada operación.

Cuando un cliente compra, se deben registrar los productos que lleva, sus cantidades, el precio aplicado y la forma de pago. Antes de confirmar la venta, debe comprobarse que existen suficientes unidades en esa sucursal. Una vez confirmada, las cantidades vendidas deben descontarse del inventario correspondiente.

Para identificar a los compradores sin solicitar demasiados datos, se propone registrar un identificador de cliente y su nombre. No se contempla solicitar carnet, teléfono ni dirección.

Con esta base de datos se busca mantener información organizada y consultar qué productos se venden, cuánto se vende y en qué sucursal se realiza cada operación.

---

### 1.1 Entrevista de Levantamiento de Información — Negocio «Mr. 5»

**Pregunta 1. ¿A qué se dedica principalmente el negocio «Mr. 5» y qué artículos comercializa?**  
**Respuesta:** Es un comercio minorista dedicado a la venta de artículos plásticos (baldes, cajas organizadoras), útiles escolares (cuadernos, mochilas), productos de limpieza (escobas) y novedades de bazar.

**Pregunta 2. ¿En cuántos locales opera actualmente el negocio y quiénes atienden?**  
**Respuesta:** Opera en dos locales físicos: la **Sucursal Centro** y la **Sucursal Mercado**. La atención en mostrador y el encargado de cada local están a cargo de trabajadores contratados y familiares del propietario.

**Pregunta 3. ¿Cómo controlan actualmente el inventario y las ventas diarias?**  
**Respuesta:** Todo se anota manualmente en cuadernos de apuntes en cada sucursal. No se cuenta con un sistema informático ni base de datos.

**Pregunta 4. ¿Qué problemas les ocasiona llevar el control en cuadernos manuales?**  
**Respuesta:** Genera tres problemas críticos en la operación diaria:
- No se sabe con exactitud cuántas unidades quedan realmente en la Sucursal Centro frente a la Sucursal Mercado, provocando ventas fallidas o quiebres de stock.
- Al cambiar el precio de un producto por inflación o nuevo lote, se confunde a qué precio se vendieron las unidades de días anteriores.
- Es lento sumar los cuadernos para saber cuánto dinero ingresó por Efectivo o por QR y qué empleado registró cada operación.

**Pregunta 5. ¿Cómo necesitan organizar su catálogo de productos y proveedores?**  
**Respuesta:** Cada producto debe pertenecer a una única categoría bien definida (`Limpieza`, `Útiles escolares`, `Artículos plásticos`, `Novedades y Bazar`) y tener identificado a su proveedor principal junto con su teléfono para realizar pedidos de reposición. Algunos artículos tienen código de barras y otros no, por lo que el código de barras debe ser opcional pero irrepetible.

**Pregunta 6. ¿Qué datos se solicitan al cliente al momento de realizar una compra?**  
**Respuesta:** Para no frenar la fila en mostrador, únicamente se registra el nombre del comprador y el sistema le asigna un número identificador interno (`id_cliente`). No se solicita carnet de identidad, NIT, teléfono ni dirección.

**Pregunta 7. ¿Cómo se manejan los pagos y qué ocurre cuando un cliente lleva varios artículos?**  
**Respuesta:** Todas las ventas son estrictamente al contado (no existen ventas al fiado ni a crédito) y se cancelan mediante un único método de pago: `EFECTIVO` o `QR`. Cuando un comprador lleva varios productos distintos en la misma compra, se emite un solo recibo general (`VENTA`) que desglosa cada artículo llevado, su cantidad y el precio aplicado (`DETALLE_VENTA`).

**Pregunta 8. ¿Qué controles debe aplicar el sistema sobre el stock al confirmar o anular una venta?**  
**Respuesta:** Antes de confirmar la venta, el sistema debe verificar que la sucursal donde se realiza la operación tenga stock suficiente de cada artículo solicitado. Al confirmarse, debe descontar automáticamente esas unidades del inventario de esa sucursal. Si una venta se anula por error o devolución, las unidades deben restituirse al inventario de la sucursal correspondiente sin dejar registros huérfanos.

---

### 1.2 Justificación del Diseño: ¿Por qué se creó cada entidad y qué problema resuelve?

| Entidad en el DER | Por qué se creó en el modelo | Problema real del negocio que resuelve |
| :--- | :--- | :--- |
| **`PROVEEDOR`** | Para almacenar los datos de contacto de los distribuidores mayoristas por separado de los artículos. | Evita repetir el nombre y teléfono del distribuidor en cada producto y permite saber a quién llamar cuando un artículo entra en stock crítico. |
| **`CATEGORIA`** | Para agrupar el catálogo en rubros únicos y estandarizados. | Elimina errores de escritura manual en los cuadernos y permite filtrar inventarios y reportes por rubro comercial. |
| **`PRODUCTO`** | Representa la definición de cada artículo o presentación comercializada con su precio oficial vigente. | Separa la información general del artículo (nombre, código de barras, precio actual) de las cantidades físicas almacenadas en cada tienda. |
| **`SUCURSAL`** | Identifica a cada local físico del negocio (`Sucursal Centro` y `Sucursal Mercado`). | Permite descentralizar las existencias, ubicar al personal y auditar en qué tienda exacta ocurrió cada venta. |
| **`INVENTARIO`** | Entidad asociativa que une `SUCURSAL` con `PRODUCTO` mediante clave compuesta `(id_sucursal, id_producto)`. | Resuelve el problema principal del negocio: controlar el stock exacto de un mismo artículo de forma independiente en cada local sin permitir cantidades negativas. |
| **`EMPLEADO`** | Registra al personal y familiares que atienden en las sucursales. | Permite saber qué trabajador está asignado a cada local y quién fue el responsable de registrar cada cobro en caja. |
| **`CLIENTE`** | Registra el identificador interno y el nombre del comprador. | Permite asociar las ventas a cada comprador y calcular su historial acumulado sin pedir datos sensibles que demoren la atención. |
| **`VENTA`** | Representa la cabecera de la operación comercial (fecha, hora, sucursal, empleado, cliente y método de pago). | Centraliza los datos generales del recibo una sola vez por compra y garantiza que el pago sea únicamente `EFECTIVO` o `QR`. |
| **`DETALLE_VENTA`** | Entidad asociativa que une `VENTA` con `PRODUCTO` mediante clave compuesta `(id_venta, id_producto)`. | Permite incluir múltiples productos en una sola venta y congela el `precio_unitario` histórico cobrado en ese momento, protegiendo los reportes pasados ante futuros cambios de precio en `PRODUCTO`. |

---

## 2) Suposiciones (decisiones para aclarar ambigüedades)

Las siguientes decisiones delimitan el alcance del proyecto. Las que no hayan sido confirmadas con el negocio deberán validarse antes de la implementación definitiva.

### Identificación del producto

Cada producto representa un tipo o presentación de artículo, no una unidad física individual.

Por ejemplo, diez escobas del mismo modelo comparten el mismo identificador de producto. La cantidad disponible se registra en INVENTARIO. Una escoba de otro modelo o presentación puede registrarse como un producto diferente.

### Clasificación por categoría

Cada producto pertenece a una sola categoría. Una categoría puede reunir varios productos.

Por ejemplo, la categoría «Útiles escolares» puede incluir lápices, cuadernos y borradores. Su identificador corresponde a la categoría, no a cada producto.

El nombre permite reconocer la categoría y la descripción explica qué clase de artículos agrupa. La asignación del producto a una categoría se realiza de manera explícita; no se deduce automáticamente de su nombre.

### Proveedor principal

Se registra un único proveedor principal por producto. Un mismo proveedor puede suministrar varios productos.

En esta etapa no se contempla registrar todos los proveedores alternativos de un producto ni gestionar órdenes de compra.

### Identificación del cliente

Se registra un cliente mediante un identificador propio y su nombre. El nombre no será único, porque distintas personas pueden llamarse igual.

El identificador distingue los registros dentro del sistema. Para asociar una nueva venta a un cliente existente, debe seleccionarse su registro; no se asumirá que dos compradores son la misma persona solamente porque tienen el mismo nombre.

### Ventas al contado

No se contemplan ventas fiadas ni a crédito. Una venta confirmada se considera pagada completamente.

Se utilizará un solo método de pago por venta: efectivo o QR. Los pagos combinados quedan fuera del alcance inicial.

### Existencias por sucursal

El stock se administra por cada combinación de producto y sucursal.

Por ejemplo, un producto puede tener doce unidades en una sucursal y cinco en la otra. Son dos registros de inventario diferentes, aunque se trate del mismo producto.

### Personal y sucursales

La entidad EMPLEADO representa a las personas que atienden y registran ventas, aunque sean familiares del propietario.

Para mantener el alcance del DER actual, se supone que cada empleado tiene una sucursal asignada a la vez. Esta decisión queda pendiente de validación con el negocio.

La sucursal asignada al empleado representa su ubicación actual. La sucursal registrada en una venta representa dónde ocurrió esa operación y se conserva aunque posteriormente cambie la asignación del empleado.

### Detalle de una venta

Cada producto aparece una sola vez dentro de una misma venta. Si el cliente lleva varias unidades del mismo producto, se registra una línea con la cantidad total.

El precio unitario guardado en esa línea corresponde al precio aplicado en el momento de la venta.

### Alcance del inventario

Se parte de una cantidad inicial verificada para cada producto y sucursal. Las ventas confirmadas disminuyen esa cantidad.

El stock no puede obtenerse únicamente a partir de las ventas: también necesita un valor inicial y un mecanismo de actualización por reposición o corrección. El DER actual almacena las existencias, pero no incluye un historial detallado de compras, traslados o ajustes.

---

## 3) Identificación de Entidades, Atributos, Tipos y PK

Los siguientes recuadros muestran la estructura propuesta para pasar del DER a las tablas. Se incluyen también las claves foráneas para indicar cómo se implementarán las relaciones.

Los tipos son orientativos y se ajustarán al gestor de base de datos elegido. «Autogenerado» indica que el sistema asignará el identificador; todavía no representa una instrucción SQL específica.

- **PK:** clave primaria.
- **FK:** clave foránea.
- **NOT NULL:** dato obligatorio.
- **UNIQUE:** valor que no puede repetirse.
- **CHECK:** condición que deben cumplir los datos.

### PROVEEDOR

Registra al proveedor principal de los productos.

```text
┌──────────────────────────────────────────────────────────────┐
│ PROVEEDOR                                                    │
├──────────────────────────────────────────────────────────────┤
│ id_proveedor: INTEGER PK, autogenerado                       │
│ nombre: VARCHAR(100) NOT NULL                                │
│ telefono: VARCHAR(20)                                        │
└──────────────────────────────────────────────────────────────┘
```

### CATEGORIA

Agrupa productos de una misma clase. La descripción permite aclarar qué artículos pertenecen a esa categoría.

```text
┌──────────────────────────────────────────────────────────────┐
│ CATEGORIA                                                    │
├──────────────────────────────────────────────────────────────┤
│ id_categoria: INTEGER PK, autogenerado                       │
│ nombre: VARCHAR(100) UNIQUE NOT NULL                         │
│ descripcion: VARCHAR(255)                                    │
└──────────────────────────────────────────────────────────────┘
```

### PRODUCTO

Registra cada tipo o presentación de artículo que vende el negocio. Su precio corresponde al precio de venta actual.

```text
┌──────────────────────────────────────────────────────────────┐
│ PRODUCTO                                                     │
├──────────────────────────────────────────────────────────────┤
│ id_producto: INTEGER PK, autogenerado                        │
│ id_proveedor: INTEGER NOT NULL                               │
│   FK → PROVEEDOR(id_proveedor)                               │
│ id_categoria: INTEGER NOT NULL                               │
│   FK → CATEGORIA(id_categoria)                               │
│ codigo_barras: VARCHAR(50) UNIQUE, opcional                  │
│ nombre: VARCHAR(100) NOT NULL                                │
│ precio: DECIMAL(10,2) NOT NULL CHECK (precio > 0)            │
└──────────────────────────────────────────────────────────────┘
```

### SUCURSAL

Identifica cada local del negocio. El nombre corresponde al local, no a la persona encargada.

```text
┌──────────────────────────────────────────────────────────────┐
│ SUCURSAL                                                     │
├──────────────────────────────────────────────────────────────┤
│ id_sucursal: INTEGER PK, autogenerado                        │
│ nombre: VARCHAR(100) NOT NULL                                │
│ direccion: VARCHAR(255) NOT NULL                             │
│ telefono: VARCHAR(20)                                        │
└──────────────────────────────────────────────────────────────┘
```

### INVENTARIO

Registra cuántas unidades de un producto hay en una sucursal. El atributo stock representa esa cantidad disponible.

```text
┌──────────────────────────────────────────────────────────────┐
│ INVENTARIO                                                   │
├──────────────────────────────────────────────────────────────┤
│ id_sucursal: INTEGER NOT NULL                                │
│   FK → SUCURSAL(id_sucursal)                                 │
│ id_producto: INTEGER NOT NULL                                │
│   FK → PRODUCTO(id_producto)                                 │
│ stock: INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)         │
│                                                              │
│ PK COMPUESTA: (id_sucursal, id_producto)                     │
└──────────────────────────────────────────────────────────────┘
```

La clave compuesta impide que se registren dos inventarios separados para el mismo producto en la misma sucursal.

### EMPLEADO

Identifica a la persona que atiende y registra las ventas. El cargo describe su función en el negocio, por ejemplo, atención de ventas o encargado.

```text
┌──────────────────────────────────────────────────────────────┐
│ EMPLEADO                                                     │
├──────────────────────────────────────────────────────────────┤
│ id_empleado: INTEGER PK, autogenerado                        │
│ id_sucursal: INTEGER NOT NULL                                │
│   FK → SUCURSAL(id_sucursal)                                 │
│ nombre: VARCHAR(100) NOT NULL                                │
│ cargo: VARCHAR(50) NOT NULL                                  │
└──────────────────────────────────────────────────────────────┘
```

Aquí, `id_sucursal` representa la sucursal actualmente asignada al empleado.

### CLIENTE

Identifica al comprador asociado a una venta, solicitando únicamente su nombre.

```text
┌──────────────────────────────────────────────────────────────┐
│ CLIENTE                                                      │
├──────────────────────────────────────────────────────────────┤
│ id_cliente: INTEGER PK, autogenerado                         │
│ nombre: VARCHAR(100) NOT NULL                                │
└──────────────────────────────────────────────────────────────┘
```

### VENTA

Registra los datos generales de la operación: cuándo ocurrió, dónde se realizó, quién la registró, a qué cliente corresponde y cómo se pagó.

```text
┌──────────────────────────────────────────────────────────────┐
│ VENTA                                                        │
├──────────────────────────────────────────────────────────────┤
│ id_venta: INTEGER PK, autogenerado                           │
│ id_sucursal: INTEGER NOT NULL                                │
│   FK → SUCURSAL(id_sucursal)                                 │
│ id_empleado: INTEGER NOT NULL                                │
│   FK → EMPLEADO(id_empleado)                                 │
│ id_cliente: INTEGER NOT NULL                                 │
│   FK → CLIENTE(id_cliente)                                   │
│ fecha_hora: DATETIME NOT NULL                                │
│ metodo_pago: VARCHAR(20) NOT NULL                            │
│   CHECK (metodo_pago IN ('EFECTIVO', 'QR'))                  │
└──────────────────────────────────────────────────────────────┘
```

### DETALLE_VENTA

Registra cada producto incluido en una venta, con su cantidad y el precio unitario aplicado.

```text
┌──────────────────────────────────────────────────────────────┐
│ DETALLE_VENTA                                                │
├──────────────────────────────────────────────────────────────┤
│ id_venta: INTEGER NOT NULL                                   │
│   FK → VENTA(id_venta)                                       │
│ id_producto: INTEGER NOT NULL                                │
│   FK → PRODUCTO(id_producto)                                 │
│ cantidad: INTEGER NOT NULL CHECK (cantidad > 0)              │
│ precio_unitario: DECIMAL(10,2) NOT NULL                      │
│   CHECK (precio_unitario > 0)                                │
│                                                              │
│ PK COMPUESTA: (id_venta, id_producto)                        │
└──────────────────────────────────────────────────────────────┘
```

El subtotal de cada línea se obtiene multiplicando `cantidad × precio_unitario`. El total de la venta se obtiene sumando sus subtotales. En esta propuesta no se almacenan como atributos adicionales.

---

## 4) Relaciones y cardinalidades (con justificación)

Se utiliza `1:N` para expresar una relación de uno a muchos. La participación mínima se aclara en la explicación de cada relación.

### PROVEEDOR — PROVEE — PRODUCTO

**Cardinalidad: 1:N.**

Un proveedor puede suministrar varios productos y cada producto tiene un único proveedor principal.

Se permite registrar un proveedor antes de asociarle productos. Por eso puede existir temporalmente un proveedor sin productos registrados.

Esta relación permite conocer al proveedor principal de cada artículo.

### CATEGORIA — CLASIFICA — PRODUCTO

**Cardinalidad: 1:N.**

Una categoría puede agrupar varios productos y cada producto pertenece a una sola categoría.

Una categoría puede registrarse antes de incorporar sus productos. Esta relación permite organizar y consultar los artículos por su clasificación.

### PRODUCTO — POSEE — INVENTARIO

**Cardinalidad: 1:N.**

Un producto puede tener varios registros de inventario, uno por cada sucursal donde se controlen sus existencias. Cada registro de inventario corresponde a un solo producto.

Un producto recién registrado puede no tener todavía registros de inventario.

### SUCURSAL — ALMACENA — INVENTARIO

**Cardinalidad: 1:N.**

Una sucursal puede tener varios registros de inventario, correspondientes a distintos productos. Cada registro pertenece a una sola sucursal.

Una sucursal puede registrarse antes de cargar sus existencias.

INVENTARIO vincula un producto con una sucursal y almacena la cantidad disponible de esa combinación.

### EMPLEADO — TRABAJA EN — SUCURSAL

**Cardinalidad: N:1, equivalente a SUCURSAL 1:N EMPLEADO.**

Varios empleados pueden estar asignados a una sucursal y cada empleado tiene una sola sucursal asignada a la vez, según la suposición adoptada.

Se permite registrar una sucursal antes de asignarle personal. Esto no significa que pueda funcionar sin personas que la atiendan.

### SUCURSAL — REALIZA — VENTA

**Cardinalidad: 1:N.**

Una sucursal puede realizar muchas ventas y cada venta ocurre en una sola sucursal.

Una sucursal puede no tener ventas registradas todavía. Esta relación permite consultar las ventas de cada local y determinar de qué inventario deben descontarse los productos.

### EMPLEADO — REGISTRA — VENTA

**Cardinalidad: 1:N.**

Un empleado puede registrar muchas ventas y cada venta tiene un único empleado responsable de su registro.

Un empleado puede existir en el sistema sin haber registrado ventas todavía.

### CLIENTE — REALIZA — VENTA

**Cardinalidad: 1:N.**

Un cliente puede realizar varias compras y cada venta se asocia a un solo cliente.

Un cliente puede registrarse antes de completar su primera compra. Se utiliza el nombre VENTA porque el modelo representa la operación desde el punto de vista del negocio.

### VENTA — TIENE — DETALLE_VENTA

**Cardinalidad: 1:N.**

Una venta confirmada debe tener al menos un detalle y puede incluir varios. Cada detalle pertenece a una sola venta.

Esta relación permite representar una venta que contiene distintos productos.

### DETALLE_VENTA — CORRESPONDE A — PRODUCTO

**Cardinalidad: N:1, equivalente a PRODUCTO 1:N DETALLE_VENTA.**

Cada detalle corresponde a un solo producto. Un producto puede aparecer en muchos detalles de ventas diferentes o no haber sido vendido todavía.

DETALLE_VENTA vincula los productos con las ventas y registra la cantidad y el precio aplicado en cada operación.

---

## 5) Reglas de negocio y restricciones importantes

### Identificación de los registros

Las claves primarias no pueden repetirse ni quedar vacías.

INVENTARIO se identifica mediante la combinación de sucursal y producto. DETALLE_VENTA se identifica mediante la combinación de venta y producto.

### Registro del cliente

Cada venta debe asociarse a un cliente registrado. Se solicita únicamente su nombre y el sistema genera su identificador.

No se exige que los nombres sean únicos ni se utilizan como sustituto del identificador.

### Ventas al contado y forma de pago

No se permiten ventas fiadas ni a crédito. Toda venta confirmada se considera completamente pagada.

Cada venta debe registrar un único método de pago: EFECTIVO o QR.

### Venta con productos

No se puede confirmar una venta sin productos. Debe existir al menos un registro de DETALLE_VENTA asociado.

### Cantidades válidas

La cantidad vendida debe ser un número entero mayor que cero.

```sql
CHECK (cantidad > 0)
```

No se permiten líneas de venta con cantidad cero o negativa.

### Stock no negativo

Las existencias deben ser un número entero mayor que cero.

```sql
CHECK (stock >=} 0)
```

Tener stock cero significa que el producto no tiene unidades disponibles en esa sucursal; no significa que deba eliminarse su registro.

### Verificación antes de vender

Antes de confirmar una venta, se debe comprobar que exista un registro de inventario y stock suficiente para cada producto en la sucursal de la operación.

Si no hay unidades suficientes, la venta no debe confirmarse en esas condiciones.

### Actualización del inventario

Al confirmar una venta, se descuenta del inventario correspondiente la cantidad de cada producto vendido:

```text
Nuevo stock = stock anterior − cantidad vendida
```

La actualización debe considerar el producto y la sucursal. Una venta realizada en un local no debe descontar las existencias del otro.

El registro de la venta, sus detalles y el descuento de inventario deben completarse como una sola operación: si alguna parte falla, no deben quedar cambios incompletos.

### Precios válidos e históricos

El precio actual del producto y el precio unitario aplicado en una venta deben ser mayores que cero.

```sql
CHECK (precio > 0)
CHECK (precio_unitario > 0)
```

Cambiar el precio de PRODUCTO no debe modificar los precios guardados en las ventas anteriores.

### Código de barras

El código de barras es opcional, porque algunos artículos pueden no tenerlo.

Cuando se registre, debe ser único dentro del catálogo. El identificador interno del producto sigue siendo `id_producto`.

### Integridad de las relaciones

No se pueden registrar ventas, inventarios o detalles que hagan referencia a clientes, empleados, sucursales o productos inexistentes.

Tampoco deben eliminarse registros referenciados si con ello se pierde la información necesaria para interpretar las ventas anteriores.

### Asignación del personal

Cada empleado tiene una sucursal asignada a la vez, de acuerdo con la suposición del proyecto.

Un cambio posterior de asignación no debe modificar la sucursal guardada en las ventas que esa persona registró anteriormente.

---

## 6) DER (diagrama) — notación Mermaid (para pegar en Markdown)

> **Aclaración sobre la notación:** se conserva el encabezado de la estructura de la práctica. El DER de este proyecto está elaborado en Draw.io con notación de Chen, no en Mermaid. Se adjunta el diagrama utilizado para la exposición.

El diagrama representa las entidades del negocio, sus atributos y las relaciones entre ellas.

Se utiliza la siguiente simbología:

- **Rectángulos:** entidades.
- **Óvalos:** atributos.
- **Atributos subrayados:** identificadores.
- **Rombos:** relaciones.
- **1 y N:** cardinalidades de uno a muchos.

Las entidades representadas son:

- PROVEEDOR.
- CATEGORIA.
- PRODUCTO.
- SUCURSAL.
- INVENTARIO.
- EMPLEADO.
- CLIENTE.
- VENTA.
- DETALLE_VENTA.

PRODUCTO es una entidad central del modelo porque representa los artículos que se clasifican, se controlan por sucursal y se venden.

INVENTARIO es una entidad asociativa que vincula PRODUCTO con SUCURSAL. Se identifica mediante la combinación de ambos.

DETALLE_VENTA es una entidad asociativa que vincula VENTA con PRODUCTO. Se identifica mediante la combinación de ambos, bajo la regla de una línea por producto en cada venta.

En el DER conceptual, las relaciones se representan mediante rombos. Las claves foráneas del apartado 3 documentan cómo se trasladarán esas relaciones al modelo de tablas; no es necesario repetirlas como óvalos en este diagrama.

[📄 Ver el diagrama entidad-relación de Mr. 5](./miproyecto.drawio.pdf)

---

## 7) Esquema Relacional Lógico (Mapeo de las 9 Entidades)

Siguiendo las reglas de transformación del modelo conceptual al modelo relacional (Unidad III), las 9 entidades y sus 10 relaciones se traducen en el siguiente esquema relacional formal:

- **PROVEEDOR** (<ins>id_proveedor</ins>, nombre, telefono)
- **CATEGORIA** (<ins>id_categoria</ins>, nombre, descripcion)
- **SUCURSAL** (<ins>id_sucursal</ins>, nombre, direccion, telefono)
- **CLIENTE** (<ins>id_cliente</ins>, nombre)
- **PRODUCTO** (<ins>id_producto</ins>, id_proveedor → PROVEEDOR, id_categoria → CATEGORIA, codigo_barras, nombre, precio)
- **EMPLEADO** (<ins>id_empleado</ins>, id_sucursal → SUCURSAL, nombre, cargo)
- **INVENTARIO** (<ins>id_sucursal</ins> → SUCURSAL, <ins>id_producto</ins> → PRODUCTO, stock)
- **VENTA** (<ins>id_venta</ins>, id_sucursal → SUCURSAL, id_empleado → EMPLEADO, id_cliente → CLIENTE, fecha_hora, metodo_pago)
- **DETALLE_VENTA** (<ins>id_venta</ins> → VENTA, <ins>id_producto</ins> → PRODUCTO, cantidad, precio_unitario)

---

## 8) Normalización y Dependencias Funcionales (1FN, 2FN y 3FN) Aplicadas a «Mr. 5»

La **normalización** es el proceso formal mediante el cual se evalúan y descomponen las relaciones para eliminar la redundancia de datos y evitar las **anomalías de inserción, borrado y modificación** (Unidad V).

A continuación, se demuestra paso a paso cómo se aplicaron la **Primera (1FN)**, **Segunda (2FN)** y **Tercera Forma Normal (3FN)** en las tablas del proyecto «Mr. 5», comparando el diseño incorrecto frente al diseño normalizado implementado en MySQL.

---

### 8.1 Primera Forma Normal (1FN): Atomicidad y Clave Primaria

- **Concepto teórico:** Una relación se encuentra en **1FN** si y solo si todos sus atributos contienen únicamente **valores atómicos (indivisibles)** —es decir, no existen grupos repetitivos ni listas de varios valores dentro de una misma celda— y cada tupla se identifica mediante una clave primaria (`PK`).

#### ❌ Ejemplo MAL HECHO (Violación de 1FN en el cuaderno de ventas)
Si intentáramos guardar una venta metiendo todos los productos comprados, sus cantidades y sus precios dentro de una misma celda de texto:

| id_venta | fecha_hora | cliente | productos_comprados | cantidades | precios | total_venta |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 2026-10-20 10:00 | Ana García | Escoba plástica, Cuaderno 100h | 2, 3 | 15.00, 8.00 | 54.00 |

- **Por qué está mal:** Las columnas `productos_comprados`, `cantidades` y `precios` son **multivaluadas** (tienen varios datos separados por comas en una sola fila). No se puede consultar con `SUM()` cuántas escobas se vendieron ni descontar stock automáticamente por producto, además de almacenar un campo calculado (`total_venta`).

#### ✅ Ejemplo BIEN HECHO en «Mr. 5» (Cumple 1FN)
Se divide la cabecera en la tabla `VENTA` y se desglosa cada artículo vendido en una fila atómica dentro de la tabla asociativa `DETALLE_VENTA` con clave primaria compuesta `(id_venta, id_producto)`:

**Tabla `VENTA`:**
| id_venta (PK) | id_sucursal (FK) | id_empleado (FK) | id_cliente (FK) | fecha_hora | metodo_pago |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 1 | 1 | 1 | 2026-10-20 10:00:00 | QR |

**Tabla `DETALLE_VENTA`:**
| id_venta (PK, FK) | id_producto (PK, FK) | cantidad | precio_unitario |
| :--- | :--- | :--- | :--- |
| 1 | 1 | 2 | 15.00 |
| 1 | 2 | 3 | 8.00 |

---

### 8.2 Segunda Forma Normal (2FN): Dependencia Funcional Completa

- **Concepto teórico:** Una relación está en **2FN** si está en 1FN y todo atributo que no forma parte de la clave primaria depende de manera **funcionalmente completa** de toda la clave primaria, y no solo de una parte de ella (elimina las **dependencias parciales** en tablas con clave primaria compuesta).

#### ❌ Ejemplo MAL HECHO (Violación de 2FN en `INVENTARIO` y `DETALLE_VENTA`)
Supongamos que en la tabla `INVENTARIO`, cuya clave primaria compuesta es `(id_sucursal, id_producto)`, guardamos también el nombre del producto, su precio y la dirección de la sucursal:

| id_sucursal (PK) | id_producto (PK) | nombre_producto | precio_actual | direccion_sucursal | stock |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 1 | Escoba plástica modelo A | 15.00 | Calle Libertad #245 | 20 |
| 2 | 1 | Escoba plástica modelo A | 15.00 | Av. Grigotá #890 | 14 |

- **Por qué está mal (Dependencias Parciales):**
  - `{id_sucursal, id_producto} → stock` *(Dependencia completa: correcta, el stock depende del local y del producto juntos).*
  - `id_producto → nombre_producto, precio_actual` *(**Dependencia parcial ❌**: el nombre y el precio del catálogo dependen solo de `id_producto`, no de la sucursal).*
  - `id_sucursal → direccion_sucursal` *(**Dependencia parcial ❌**: la dirección depende solo de `id_sucursal`, no del producto).*
  - **Anomalías generadas:** Si la escoba cambia de nombre o de precio, habría que actualizarla en todas las sucursales; si una sucursal nueva aún no tiene productos en stock, no podríamos registrar su dirección.

#### ✅ Ejemplo BIEN HECHO en «Mr. 5» (Cumple 2FN)
Se extraen los atributos que dependen parcialmente a sus propias tablas maestras (`PRODUCTO` y `SUCURSAL`), dejando en `INVENTARIO` y en `DETALLE_VENTA` exclusivamente los atributos que dependen de la llave compuesta completa:

- En **`INVENTARIO`**: `({id_sucursal, id_producto} → stock)`
- En **`DETALLE_VENTA`**: `({id_venta, id_producto} → cantidad, precio_unitario)` *(Nota: `precio_unitario` sí depende de la clave compuesta completa porque representa el precio histórico aplicado a ese producto en esa venta específica).*

| id_sucursal (PK, FK) | id_producto (PK, FK) | stock |
| :--- | :--- | :--- |
| 1 | 1 | 20 |
| 2 | 1 | 14 |

---

### 8.3 Tercera Forma Normal (3FN): Eliminación de Dependencias Transitivas

- **Concepto teórico:** Una relación está en **3FN** si está en 2FN y ningún atributo no-clave depende **transitivamente** de la clave primaria a través de otro atributo no-clave (es decir, no existe `PK → Atributo_A → Atributo_B`).

#### ❌ Ejemplo MAL HECHO (Violación de 3FN en `PRODUCTO`)
Si dentro de la tabla `PRODUCTO` almacenáramos directamente el nombre y el teléfono del proveedor junto con la descripción de la categoría:

| id_producto (PK) | nombre | precio | id_proveedor | nombre_proveedor | telefono_proveedor | id_categoria | descripcion_categoria |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Escoba modelo A | 15.00 | 1 | Distribuidora Norte | 71011223 | 1 | Aseo del hogar |
| 4 | Balde 20L | 25.00 | 3 | Plásticos Oriente | 33456789 | 3 | Baldes y tapers |
| 5 | Caja 40L | 65.00 | 3 | Plásticos Oriente | 33456789 | 3 | Baldes y tapers |

- **Por qué está mal (Dependencias Transitivas):**
  - `id_producto → id_proveedor → nombre_proveedor, telefono_proveedor` *(**Dependencia transitiva ❌**: el teléfono pertenece al proveedor, no al producto).*
  - `id_producto → id_categoria → descripcion_categoria` *(**Dependencia transitiva ❌**: la descripción pertenece a la categoría, no al producto).*
  - **Anomalías generadas:**
    - *Inserción:* No puedo registrar un proveedor nuevo hasta que me venda al menos un producto.
    - *Borrado:* Si elimino el único producto que me vende `Distribuidora Norte`, pierdo el nombre y el teléfono del proveedor.
    - *Modificación:* Si `Plásticos Oriente` cambia de teléfono, debo modificar todas las filas de productos que provee.

#### ✅ Ejemplo BIEN HECHO en «Mr. 5» (Cumple 3FN)
Se descomponen las dependencias transitivas en las tablas independientes `PROVEEDOR` y `CATEGORIA`, dejando en `PRODUCTO` únicamente las claves foráneas `id_proveedor` e `id_categoria`:

**Tabla `PROVEEDOR`:** `id_proveedor (PK) → nombre, telefono`  
**Tabla `CATEGORIA`:** `id_categoria (PK) → nombre, descripcion`  
**Tabla `PRODUCTO`:** `id_producto (PK) → id_proveedor (FK), id_categoria (FK), codigo_barras, nombre, precio`

#### Justificación Técnica de 3FN entre `EMPLEADO`, `SUCURSAL` y `VENTA`
En nuestro modelo relacional:
- `EMPLEADO` posee `id_sucursal` (representa la **sucursal donde el trabajador está asignado actualmente**).
- `VENTA` posee `id_empleado` e `id_sucursal` (representa **en qué local físico ocurrió la venta en ese momento**).
- **¿Por qué NO existe dependencia transitiva (`id_venta → id_empleado → id_sucursal`)?** Porque un empleado o familiar puede cambiar de sucursal asignada el próximo mes (se actualiza `EMPLEADO.id_sucursal`), pero las ventas que registró el mes pasado deben seguir perteneciendo históricamente a la sucursal donde se efectuaron y de cuyo inventario salió la mercadería (`VENTA.id_sucursal`). Por tanto, ambos atributos representan hechos independientes en el tiempo y cumplen rigurosamente la **3FN**.
