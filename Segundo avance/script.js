let DATOS_RECIBOS = {};
try {
    const elJson = document.getElementById('datos-recibos-json');
    if (elJson && elJson.textContent.trim().startsWith('{')) {
        DATOS_RECIBOS = JSON.parse(elJson.textContent);
    }
} catch (err) {
    DATOS_RECIBOS = {};
}

function cambiarTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(sec => sec.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

    const seccion = document.getElementById('tab-' + tabId);
    const boton = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
    if (seccion) seccion.classList.add('active');
    if (boton) boton.classList.add('active');
}

function agregarLineaProducto() {
    const contenedor = document.getElementById('contenedor-lineas');
    const template = document.getElementById('template-linea-producto');
    const clon = template.content.cloneNode(true);
    contenedor.appendChild(clon);
    recalcularTotalEstimado();
}

function eliminarLineaProducto(boton) {
    boton.closest('.item-venta-row').remove();
    recalcularTotalEstimado();
}

function recalcularTotalEstimado() {
    let total = 0;
    const filas = document.querySelectorAll('#contenedor-lineas .item-venta-row');
    filas.forEach(fila => {
        const selectProd = fila.querySelector('.select-producto');
        const inputCant = fila.querySelector('.input-cantidad');
        if (selectProd && inputCant) {
            const opcionElegida = selectProd.options[selectProd.selectedIndex];
            const precio = parseFloat(opcionElegida ? opcionElegida.getAttribute('data-precio') : 0) || 0;
            const cantidad = parseInt(inputCant.value, 10) || 0;
            if (cantidad > 0) {
                total += precio * cantidad;
            }
        }
    });
    const etiquetaTotal = document.getElementById('monto-estimado');
    if (etiquetaTotal) {
        etiquetaTotal.textContent = 'Bs ' + total.toFixed(2);
    }
}

function verNotaVenta(idVenta) {
    const data = DATOS_RECIBOS[idVenta];
    if (!data) {
        alert('No se encontraron datos para la venta #' + idVenta);
        return;
    }

    document.getElementById('recibo-id').textContent = '#' + data.id_venta;
    document.getElementById('recibo-fecha').textContent = data.fecha_hora;
    document.getElementById('recibo-sucursal').textContent = data.sucursal;
    document.getElementById('recibo-empleado').textContent = data.empleado;
    document.getElementById('recibo-cliente').textContent = data.cliente;
    document.getElementById('recibo-pago').textContent = data.metodo_pago;

    const tbody = document.getElementById('recibo-items');
    tbody.innerHTML = '';
    data.items.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${item.cantidad}</td>
            <td>${item.producto}</td>
            <td>Bs ${item.precio_unitario.toFixed(2)}</td>
            <td>Bs ${item.subtotal.toFixed(2)}</td>
        `;
        tbody.appendChild(tr);
    });

    document.getElementById('recibo-total').textContent = 'Bs ' + data.total.toFixed(2);
    document.getElementById('modal-recibo').style.display = 'flex';
}

function cerrarModalRecibo() {
    document.getElementById('modal-recibo').style.display = 'none';
}

function configurarModalEditar(titulo, accion, tab, idName, idVal, camposHtml) {
    document.getElementById('modal-editar-titulo').textContent = titulo;
    document.getElementById('edit-accion').value = accion;
    document.getElementById('edit-tab').value = tab;
    const idInput = document.getElementById('edit-id-input');
    idInput.name = idName;
    idInput.value = idVal;
    document.getElementById('edit-campos').innerHTML = camposHtml;
    document.getElementById('modal-editar').style.display = 'flex';
}

function cerrarModalEditar() {
    document.getElementById('modal-editar').style.display = 'none';
}

function abrirModalCliente(btn) {
    configurarModalEditar(
        'Editar Cliente #' + btn.dataset.id,
        'editar_cliente',
        'entidades',
        'id_cliente',
        btn.dataset.id,
        `<label>Nombre del Cliente:</label>
         <input type="text" name="nombre" id="edit-campo-nombre" required>`
    );
    document.getElementById('edit-campo-nombre').value = btn.dataset.nombre;
}

function abrirModalSucursal(btn) {
    configurarModalEditar(
        'Editar Sucursal #' + btn.dataset.id,
        'editar_sucursal',
        'entidades',
        'id_sucursal',
        btn.dataset.id,
        `<label>Nombre:</label>
         <input type="text" name="nombre" id="edit-campo-nombre" required>
         <label>Dirección:</label>
         <input type="text" name="direccion" id="edit-campo-dir" required>
         <label>Teléfono:</label>
         <input type="text" name="telefono" id="edit-campo-tel" required>`
    );
    document.getElementById('edit-campo-nombre').value = btn.dataset.nombre;
    document.getElementById('edit-campo-dir').value = btn.dataset.direccion;
    document.getElementById('edit-campo-tel').value = btn.dataset.telefono;
}

function abrirModalEmpleado(btn) {
    const opSuc = document.getElementById('template-opciones-sucursal').innerHTML;
    configurarModalEditar(
        'Editar Empleado #' + btn.dataset.id,
        'editar_empleado',
        'entidades',
        'id_empleado',
        btn.dataset.id,
        `<label>Nombre:</label>
         <input type="text" name="nombre" id="edit-campo-nombre" required>
         <label>Cargo:</label>
         <input type="text" name="cargo" id="edit-campo-cargo" required>
         <label>Sucursal:</label>
         <select name="id_sucursal" id="edit-campo-suc" required>${opSuc}</select>`
    );
    document.getElementById('edit-campo-nombre').value = btn.dataset.nombre;
    document.getElementById('edit-campo-cargo').value = btn.dataset.cargo;
    document.getElementById('edit-campo-suc').value = btn.dataset.sucursal;
}

function abrirModalProveedor(btn) {
    configurarModalEditar(
        'Editar Proveedor #' + btn.dataset.id,
        'editar_proveedor',
        'entidades',
        'id_proveedor',
        btn.dataset.id,
        `<label>Nombre:</label>
         <input type="text" name="nombre" id="edit-campo-nombre" required>
         <label>Teléfono:</label>
         <input type="text" name="telefono" id="edit-campo-tel" required>`
    );
    document.getElementById('edit-campo-nombre').value = btn.dataset.nombre;
    document.getElementById('edit-campo-tel').value = btn.dataset.telefono;
}

function abrirModalCategoria(btn) {
    configurarModalEditar(
        'Editar Categoría #' + btn.dataset.id,
        'editar_categoria',
        'entidades',
        'id_categoria',
        btn.dataset.id,
        `<label>Nombre:</label>
         <input type="text" name="nombre" id="edit-campo-nombre" required>
         <label>Descripción:</label>
         <input type="text" name="descripcion" id="edit-campo-desc" required>`
    );
    document.getElementById('edit-campo-nombre').value = btn.dataset.nombre;
    document.getElementById('edit-campo-desc').value = btn.dataset.descripcion;
}

function abrirModalProducto(btn) {
    const opCat = document.getElementById('template-opciones-categoria').innerHTML;
    const opProv = document.getElementById('template-opciones-proveedor').innerHTML;
    configurarModalEditar(
        'Editar Producto #' + btn.dataset.id,
        'editar_producto',
        'inventario',
        'id_producto',
        btn.dataset.id,
        `<label>Nombre del Producto:</label>
         <input type="text" name="nombre" id="edit-campo-nombre" required>
         <label>Código de Barras:</label>
         <input type="text" name="codigo_barras" id="edit-campo-codigo">
         <label>Precio (Bs):</label>
         <input type="number" step="0.50" min="0.50" name="precio" id="edit-campo-precio" required>
         <label>Categoría:</label>
         <select name="id_categoria" id="edit-campo-cat" required>${opCat}</select>
         <label>Proveedor:</label>
         <select name="id_proveedor" id="edit-campo-prov" required>${opProv}</select>`
    );
    document.getElementById('edit-campo-nombre').value = btn.dataset.nombre;
    document.getElementById('edit-campo-codigo').value = btn.dataset.codigo;
    document.getElementById('edit-campo-precio').value = btn.dataset.precio;
    document.getElementById('edit-campo-cat').value = btn.dataset.cat;
    document.getElementById('edit-campo-prov').value = btn.dataset.prov;
}

document.addEventListener('DOMContentLoaded', () => {
    const tabInicial = document.body.getAttribute('data-active-tab') || 'pos';
    cambiarTab(tabInicial);
    recalcularTotalEstimado();
});