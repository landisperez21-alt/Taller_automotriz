/* MotorTech Service · app.js — JavaScript nativo, sin dependencias. */
(function () {
    "use strict";

    var reducirMovimiento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
    var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

    /* ---- Menú lateral (móvil) ------------------------------------------ */
    function alternarMenu(abrir) {
        document.body.classList.toggle("nav-open", abrir);
        var boton = $("[data-nav-toggle]");
        if (boton) boton.setAttribute("aria-expanded", abrir ? "true" : "false");
    }
    $$("[data-nav-toggle]").forEach(function (b) {
        b.addEventListener("click", function () { alternarMenu(!document.body.classList.contains("nav-open")); });
    });
    var scrim = $(".nav-scrim");
    if (scrim) scrim.addEventListener("click", function () { alternarMenu(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") alternarMenu(false); });

    /* ---- Avisos: se cierran solos --------------------------------------- */
    function cerrarToast(t) {
        t.classList.add("is-leaving");
        setTimeout(function () { t.remove(); }, 280);
    }
    $$(".toast").forEach(function (t) {
        var cierre = $(".toast__close", t);
        if (cierre) cierre.addEventListener("click", function () { cerrarToast(t); });
        if (!t.classList.contains("toast--error")) setTimeout(function () { cerrarToast(t); }, 6000);
    });

    /* ---- Entradas: mayúsculas y solo dígitos ---------------------------- */
    $$("[data-uppercase]").forEach(function (el) {
        el.addEventListener("input", function () {
            var pos = el.selectionStart;
            el.value = el.value.toUpperCase().replace(/\s+/g, "");
            try { el.setSelectionRange(pos, pos); } catch (_) { /* tipo sin selección */ }
        });
    });
    $$("[data-digits]").forEach(function (el) {
        el.addEventListener("input", function () { el.value = el.value.replace(/\D+/g, ""); });
    });

    /* ---- Mostrar / ocultar contraseña ----------------------------------- */
    $$("[data-toggle-password]").forEach(function (b) {
        b.addEventListener("click", function () {
            var campo = document.getElementById(b.getAttribute("data-toggle-password"));
            if (!campo) return;
            var visible = campo.type === "text";
            campo.type = visible ? "password" : "text";
            b.setAttribute("aria-label", visible ? "Mostrar contraseña" : "Ocultar contraseña");
            b.setAttribute("aria-pressed", visible ? "false" : "true");
        });
    });

    /* ---- Evitar envíos duplicados --------------------------------------- */
    $$("form[data-once]").forEach(function (f) {
        f.addEventListener("submit", function () {
            var enviar = $("[type=submit]", f);
            if (enviar) { enviar.setAttribute("data-loading", ""); enviar.setAttribute("aria-busy", "true"); }
        });
    });

    /* ---- Filtros que se aplican al cambiar ------------------------------ */
    $$("[data-autosubmit]").forEach(function (el) {
        el.addEventListener("change", function () { if (el.form) el.form.submit(); });
    });

    /* ---- Imprimir / guardar como PDF ------------------------------------ */
    $$("[data-print]").forEach(function (b) {
        b.addEventListener("click", function () { window.print(); });
    });

    /* ---- Confirmación de eliminación (diálogo nativo) ------------------- */
    var dialogo = $("#dlg-eliminar");
    if (dialogo && typeof dialogo.showModal === "function") {
        var formEliminar = $("form", dialogo);
        var nombre = $("[data-delete-name]", dialogo);
        $$("[data-delete-url]").forEach(function (b) {
            b.addEventListener("click", function (e) {
                e.preventDefault();
                formEliminar.setAttribute("action", b.getAttribute("data-delete-url"));
                nombre.textContent = b.getAttribute("data-delete-name") || "este registro";
                dialogo.showModal();
            });
        });
        $$("[data-close-dialog]", dialogo).forEach(function (b) {
            b.addEventListener("click", function () { dialogo.close(); });
        });
        dialogo.addEventListener("click", function (e) { if (e.target === dialogo) dialogo.close(); });
    }

    /* ---- Contadores animados + KPIs en tiempo real ---------------------- */
    function animarNumero(el, destino) {
        if (reducirMovimiento || destino < 1) { el.textContent = destino.toLocaleString("es-PE"); return; }
        var inicio = null, dur = 900;
        function paso(t) {
            if (inicio === null) inicio = t;
            var p = Math.min((t - inicio) / dur, 1), suave = 1 - Math.pow(1 - p, 3);
            el.textContent = Math.round(destino * suave).toLocaleString("es-PE");
            if (p < 1) requestAnimationFrame(paso);
        }
        requestAnimationFrame(paso);
    }
    $$("[data-countup]").forEach(function (el) {
        var n = parseInt(el.textContent.replace(/\D/g, ""), 10);
        if (!isNaN(n)) animarNumero(el, n);
    });

    var panel = $("[data-kpi-url]");
    if (panel) {
        var url = panel.getAttribute("data-kpi-url");
        var indicador = $("[data-live]");
        var hora = $("[data-live-time]");

        var refrescar = function () {
            if (document.hidden) return;
            fetch(url, { credentials: "same-origin", headers: { "Accept": "application/json" } })
                .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
                .then(function (datos) {
                    $$("[data-kpi]").forEach(function (el) {
                        var clave = el.getAttribute("data-kpi");
                        if (!(clave in datos)) return;
                        var valor = datos[clave];
                        var nuevo = typeof valor === "number" ? valor.toLocaleString("es-PE") : String(valor);
                        if (el.textContent.trim() !== nuevo) {
                            el.textContent = nuevo;
                            el.classList.remove("is-flash");
                            void el.offsetWidth;
                            el.classList.add("is-flash");
                        }
                    });
                    if (hora) hora.textContent = datos.actualizado;
                    if (indicador) indicador.classList.remove("is-offline");
                })
                .catch(function () { if (indicador) indicador.classList.add("is-offline"); });
        };
        setInterval(refrescar, 30000);
        document.addEventListener("visibilitychange", function () { if (!document.hidden) refrescar(); });
    }

    /* ---- Orden de servicio: total en vivo ------------------------------- */
    var caja = $("[data-orden-total]");
    if (caja) {
        var selRep = $("#id_repuesto"), cant = $("#id_cantidad_repuesto"), mano = $("#id_costo_mano_obra");
        var salida = {
            rep: $("[data-out=repuestos]", caja), mano: $("[data-out=mano]", caja),
            total: $("[data-out=total]", caja), stock: $("[data-out=stock]", caja)
        };
        var moneda = function (n) {
            return "S/ " + (isFinite(n) ? n : 0).toLocaleString("es-PE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        };
        var calcular = function () {
            var opcion = selRep && selRep.options[selRep.selectedIndex];
            var precio = opcion ? parseFloat(opcion.getAttribute("data-precio")) : NaN;
            var stock = opcion ? opcion.getAttribute("data-stock") : null;
            var c = parseInt(cant && cant.value, 10) || 0;
            var m = parseFloat(mano && mano.value) || 0;
            var repuestos = (isNaN(precio) ? 0 : precio) * c;
            salida.rep.textContent = moneda(repuestos);
            salida.mano.textContent = moneda(m);
            salida.total.textContent = moneda(repuestos + m);
            salida.stock.textContent = stock === null ? "—" : stock + " u.";
        };
        [selRep, cant, mano].forEach(function (el) { if (el) { el.addEventListener("input", calcular); el.addEventListener("change", calcular); } });
        calcular();
    }
})();
