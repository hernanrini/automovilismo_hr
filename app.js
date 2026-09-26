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

    const esFiltroGeneral = (filtroActual === "todas" || filtroActual === "todos");
    
    // Comportamiento estable: si es general, limitamos a las primeras 3 semanas. Si es categoría específica, mostramos todo.
    let semanasAMostrar = agendaGlobal;
    if (esFiltroGeneral) {
        semanasAMostrar = agendaGlobal.slice(0, 3);
    }

    semanasAMostrar.forEach(semana => {
        let HTMLTarjetasCategorias = "";
        let eventosVisiblesCount = 0;

        semana.eventos.forEach(evento => {
            const claseEvento = (evento.categoriaClase || "").toLowerCase().trim();

            // Si no es general y la categoría no coincide, saltamos este evento
            if (!esFiltroGeneral && claseEvento !== filtroActual) {
                return;
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

        // Si estamos filtrando por categoría específica y esta semana no tiene eventos de esa categoría, la saltamos
        if (!esFiltroGeneral && eventosVisiblesCount === 0) {
            return;
        }

        const bloque = document.createElement("section");
        bloque.className = `bloque-finde ${semana.semana === 1 ? 'actual' : ''}`;

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