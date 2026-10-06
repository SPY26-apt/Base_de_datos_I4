

## 📁 Proyecto: Sistema de Control de Inventario y Ventas ("Mr. 5")

### 1. Descripción de la Problemática
La tienda "Mr. 5" es un comercio minorista e informal de artículos plásticos, útiles escolares y novedades. Actualmente llevan el control de su inventario a mano en cuadernos, lo que genera caos en el stock, desfases entre sucursales y dificultades para hacer el cuadre de caja por turno. Como las ventas en mostrador son rápidas y al contado, necesitan un sistema ágil que descuente el stock al instante sin ralentizar la fila pidiendo datos personales a los compradores.

### 2. Diseño de la Solución y Suposiciones Clave
Para resolver este problema, el sistema se diseña bajo las siguientes reglas de negocio:
* **Venta rápida y anónima:** Para evitar cuellos de botella en caja, no se registra al cliente. La transacción es el foco central.
* **Manejo de Sucursales e Inventario:** El negocio cuenta con varias sucursales. Por lo tanto, el stock no es global, sino que se controla mediante un inventario específico por producto y sucursal.
* **Control de Caja y Empleados:** Cada venta registra qué empleado la realizó y en qué sucursal, permitiendo el cuadre de caja y la responsabilidad por faltantes.
* **Precio Histórico:** El precio de un producto puede variar con el tiempo, por lo que el detalle de la venta congela el `precio_unitario` al momento exacto de la transacción.

### 3. Diccionario de Entidades
1. **PROVEEDOR:** Registra a quién se le reclama la mercadería.
2. **CATEGORIA:** Clasifica los productos (ej. Plásticos, Útiles, Novedades) para reportes de ventas.
3. **PRODUCTO:** Catálogo central de artículos con su precio actual y código de barras.
4. **SUCURSAL:** Ubicaciones físicas del negocio.
5. **INVENTARIO:** Tabla asociativa que controla la cantidad exacta de stock de un producto en una sucursal específica.
6. **EMPLEADO:** Personal que trabaja en las sucursales y registra las ventas.
7. **VENTA:** El ticket generado, registrando fecha, hora, método de pago y quién atendió.
8. **DETALLE_VENTA:** Tabla asociativa que registra qué productos salieron en una venta, qué cantidad y a qué precio histórico.

## 4) Relaciones y cardinalidades (con justificación)

*   **PROVEEDOR (1) — (N) PRODUCTO:** Un proveedor surte múltiples productos al bazar, pero cada producto registrado se asocia a un único proveedor principal para mantener limpio el canal de reclamos y pedidos.
*   **CATEGORIA (1) — (N) PRODUCTO:** Una categoría (ej. Plásticos, Útiles) agrupa muchos artículos, y cada producto pertenece a una sola categoría para facilitar los reportes de qué área vende más.
*   **SUCURSAL (1) — (N) EMPLEADO:** Una sucursal física tiene asignados a varios empleados, y cada empleado está registrado en una sucursal base para el control del personal.
*   **SUCURSAL (1) — (N) VENTA:** Una sucursal genera múltiples ventas a lo largo del día. Cada ticket emitido pertenece obligatoriamente al lugar físico donde se hizo la transacción.
*   **EMPLEADO (1) — (N) VENTA:** Un trabajador (cajero/vendedor) atiende a muchos compradores en su turno, pero cada venta tiene un único responsable asociado para permitir el cuadre de caja ante faltantes.
*   **SUCURSAL (1) — (N) INVENTARIO (N) — (1) PRODUCTO:** Relación asociativa. Un producto no tiene un stock global, sino que su cantidad disponible depende directamente de en qué sucursal se encuentra almacenado.
*   **VENTA (1) — (N) DETALLE_VENTA (N) — (1) PRODUCTO:** Relación asociativa. Una transacción en el mostrador incluye varios productos diferentes en distintas cantidades. A su vez, un producto es despachado en muchas ventas a lo largo del tiempo. 

## 5) Reglas de negocio y restricciones importantes

1.  **Ventas rápidas y anónimas (Sin entidad CLIENTE):** Por la naturaleza del comercio informal "Mr. 5", pedir nombre y carnet a los compradores genera cuellos de botella. La prioridad operativa es descontar inventario, por lo que las ventas se asumen como "Consumidor Final".
2.  **Cero créditos:** No se fía a nadie. Se asume que el 100% de la mercadería despachada es pagada al instante en el mostrador (EFECTIVO o QR).
3.  **Restricciones de Stock:** El sistema no admite inventario negativo. La base de datos debe contemplar la regla `CHECK (stock >= 0)` en la tabla `INVENTARIO`, apoyada por una transacción lógica que impida la venta si no hay saldo disponible.
4.  **Precios y Cantidades válidas:** Las cantidades vendidas y los precios no pueden ser nulos ni negativos. Se aplican reglas `CHECK > 0` y `NOT NULL`.
5.  **Preservación del Precio Histórico:** El costo de un producto puede variar por inflación. Por ello, la tabla `DETALLE_VENTA` guarda el `precio_unitario` exacto del momento de la transacción, evitando que reportes de ventas pasadas se alteren si el `precio` en la tabla `PRODUCTO` sube en el futuro.
## 6) Modelo Conceptual: DER (Notación de Chen)

En esta fase diseñamos el modelo conceptual basándonos en los requerimientos del negocio, identificando las entidades principales, sus atributos y las relaciones entre ellas antes de pasar a la estructura de tablas.

<!-- BOTÓN PARA VER EL PDF -->
[![Ver Diagrama Conceptual en PDF](https://img.shields.io/badge/📄_Ver_Diagrama_Conceptual-PDF-red?style=for-the-badge)](./docs/Diagrama.drawio.pdf)
