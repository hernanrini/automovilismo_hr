// Variable global para almacenar los datos de la agenda
let agendaGlobal = [];
let filtroActual = "todas"; // Por defecto mostramos todas

document.addEventListener("DOMContentLoaded", () => {
    cargarAgenda();
    configurarFiltrosEstaticos();
});

async function cargarAgenda() {
    try {
        const respuesta = await fetch("carreras.json");
        agendaGlobal = await respuesta.json();
        
        // Renderizar la agenda aplicando el filtro actual
        renderizarAgenda();

    } catch (error) {
        console.error("Error al cargar la agenda de Automovilismo_HR:", error);
    }
}

function configurarFiltrosEstaticos() {
    const contenedorFiltros = document.querySelector(".filtros-scroll");
    if (!contenedorFiltros) return;

    // Escuchar clics en los botones de filtro ya existentes en el HTML
    contenedorFiltros.addEventListener("click", (e) => {
        const boton = e.target.closest(".pill-filtro");
        if (!boton) return;

        // Cambiar clases activas visuales
        contenedorFiltros.querySelectorAll(".pill-filtro").forEach(b => b.classList.remove("activo", "active"));
        boton.classList.add("activo");

        // Capturar categoría y re-renderizar
        filtroActual = boton.getAttribute("data-categoria").toLowerCase().trim();
        renderizarAgenda();
    });
}

function renderizarAgenda() {
    const contenedor = document.getElementById("contenedor-principal");
    if (!contenedor) return;
    
    contenedor.innerHTML = "";

    agendaGlobal.forEach(semana => {
        const bloque = document.createElement("section");
        bloque.className = `bloque-finde ${semana.semana === 1 ? 'actual' : ''}`;

        let HTMLTarjetasCategorias = "";
        let eventosVisiblesCount = 0;

        semana.eventos.forEach(evento => {
            const claseEvento = (evento.categoriaClase || "").toLowerCase().trim();

            // Filtrar si no coincide con la categoría seleccionada (y el filtro no es 'todas' o 'todos')
            if (filtroActual !== "todas" && filtroActual !== "todos" && claseEvento !== filtroActual) {
                return; // Omitir este evento
            }

            eventosVisiblesCount++;

            const sesionesPorDia = {};
            evento.sesiones.forEach(sesion => {
                if (!sesionesPorDia[sesion.dia]) {
                    sesionesPorDia[sesion.dia] = [];
                }
                sesionesPorDia[sesion.dia].push(sesion);
            });

            let HTMLBloquesDias = "";

            for (const [nombreDia, listaSesiones] of Object.entries(sesionesPorDia)) {
                let HTMLFilasSesiones = "";

                listaSesiones.forEach(sesion => {
                    const fechaObj = new Date(sesion.fechaUtc);
                    const horaLocal = !isNaN(fechaObj) 
                        ? fechaObj.toLocaleTimeString([], { 
                            hour: '2-digit', 
                            minute: '2-digit', 
                            hour12: false 
                          })
                        : 'A confirmar';

                    const subcategoriaTag = sesion.divisional 
                        ? `<span class="badge-divisional">${sesion.divisional}</span>` 
                        : '';

                    HTMLFilasSesiones += `
                        <div class="sesion-row ${sesion.destacado ? 'destacado' : ''}">
                            <div class="sesion-info">
                                ${subcategoriaTag}
                                <span class="nombre-sesion">${sesion.nombre}</span>
                            </div>
                            <span class="hora-sesion">
                                <small class="orig-time">${sesion.horaOriginal}</small> / 
                                <strong class="user-time">${horaLocal} (Tu hora)</strong>
                            </span>
                        </div>
                    `;
                });

                HTMLBloquesDias += `
                    <div class="dia-sesion">
                        <div class="dia-titulo">${nombreDia}</div>
                        ${HTMLFilasSesiones}
                    </div>
                `;
            }

            HTMLTarjetasCategorias += `
                <article class="tarjeta-carrera ${evento.categoriaClase}">
                    <div class="card-header">
                        <div class="header-top-row">
                            <span class="categoria-tag tag-${evento.categoriaClase}">${evento.categoria}</span>
                            ${evento.logoUrl ? `<img src="${evento.logoUrl}" alt="" class="logo-categoria" onerror="this.style.display='none'">` : ''}
                        </div>
                        <h3>${evento.evento}</h3>
                        <p class="circuito">${evento.circuito}</p>
                    </div>
                    <div class="cronograma-sesiones">
                        ${HTMLBloquesDias}
                    </div>
                </article>
            `;
        });

        // Si hay un filtro aplicado y este fin de semana no tiene eventos, ocultamos el bloque de la semana
        if (filtroActual !== "todas" && filtroActual !== "todos" && eventosVisiblesCount === 0) {
            return;
        }

        bloque.innerHTML = `
            <div class="header-finde">
                <h2>📅 Fin de Semana: ${semana.tituloSemana}</h2>
                <span class="badge-semana ${semana.semana > 1 ? 'proximo' : ''}">${semana.estado}</span>
            </div>
            <div class="grid-tarjetas">
                ${HTMLTarjetasCategorias}
            </div>
        `;

        contenedor.appendChild(bloque);
    });

    if (contenedor.innerHTML.trim() === "") {
        contenedor.innerHTML = `<p class="sin-resultados">No hay eventos programados para esta categoría en las próximas semanas.</p>`;
    }
}