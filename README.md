# 🗄️ Bases de Datos I - Grupo I4

Repositorio educativo para la materia de **Bases de Datos I** (UAGRM). Este espacio documenta el desarrollo de modelos conceptuales, lógicos y físicos a lo largo del semestre.

---

## 📂 Estructura del Repositorio

* **`/docs`**: Contiene los diagramas Entidad-Relación y documentos de análisis.
* **`/sql`**: Contendrá los scripts de creación de tablas y consultas futuras.

---

## 🚀 Proyecto Actual: Tienda Comercial / Bazar

### 📝 Descripción de la Problemática o Requisitos
La tienda "Mr. 5" es un negocio muy surtido que ofrece productos plásticos, útiles y artículos variados. Actualmente, no cuentan con ningún sistema digital para el registro de su mercadería; el control de inventario se hace de forma manual y visual. La mayoría de los productos no tienen código de barras, lo que dificulta saber con exactitud los precios y el stock disponible. Además, tienen problemas para llevar un registro ordenado de las empresas que les surten los productos y de los clientes frecuentes, ya que todo se anota en cuadernos que son difíciles de consultar.

### 🛠️ Diseño de la Solución
Para automatizar las operaciones, se definieron las siguientes reglas de negocio:

1. A la tienda le distribuyen **productos** que son proveídos por uno o varios **proveedores**. Del proveedor se conoce su: ID_PROVEEDOR, NOMBRE y TELEFONO.
2. Un proveedor provee muchos productos a la tienda, y un producto es proveído por un único proveedor principal para saber a quién reclamar si falta stock.
3. El negocio necesita registrar sus **productos**. Como no tienen códigos de fábrica, el sistema creará un ID interno. Del producto se tiene su: ID_PRODUCTO, NOMBRE, PRECIO y STOCK.
4. Se registrará la información de los **clientes** (especialmente aquellos recurrentes o que requieren recibo). Del cliente se guardará su: ID_CLIENTE y NOMBRE.
5. Un producto es comprado por muchos clientes, y un cliente compra uno o muchos productos.

---

## 📖 Información del Curso

* **Materia:** Bases de Datos I
* **Grupo:** I4
* **Universidad:** UAGRM (Universidad Autónoma Gabriel René Moreno)
* **Estudiante:** Saúl Pedraza
