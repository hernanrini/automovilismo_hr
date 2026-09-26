// Variable global para almacenar los datos de la agenda
let agendaGlobal = [];
let filtroActual = "todas"; // Por defecto mostramos todas

document.addEventListener("DOMContentLoaded", () => {
    cargarAgenda();
    configurarFiltrosEstaticos();
});

async function cargarAgenda() {
    const contenedor = document.getElementById("contenedor-principal");
    try {
        const respuesta = await fetch("carreras.json");
        if (!respuesta.ok) {
            throw new Error(`HTTP error! status: ${respuesta.status}`);
        }
        agendaGlobal = await respuesta.json();
        
        if (!Array.isArray(agendaGlobal) || agendaGlobal.length === 0) {
            if (contenedor) {
                contenedor.innerHTML = `<p class="sin-resultados">El archivo carreras.json está vacío o no tiene el formato correcto.</p>`;
            }
            return;
        }

        renderizarAgenda();

    } catch (error) {
        console.error("Error al cargar la agenda:", error);
        if (contenedor) {
            contenedor.innerHTML = `<p class="sin-resultados">Error al cargar `carreras.json`. Comprueba la consola.</p>`;
        }
    }
}

function configurarFiltrosEstaticos() {
    const contenedorFiltros = document.querySelector(".filtros-scroll");
    if (!contenedorFiltros) return;

    contenedorFiltros.addEventListener("click", (e) => {
        const boton = e.target.closest(".pill-filtro");
        if (!boton) return;

        contenedorFiltros.querySelectorAll(".pill-filtro").forEach(b => b.classList.remove("activo", "active"));
        boton.classList.add("activo");

        filtroActual = boton.getAttribute("data-categoria").toLowerCase().trim();
        renderizarAgenda();
    });
}

function renderizarAgenda() {
    const contenedor = document.getElementById("contenedor-principal");
    if (!contenedor) return;
    
    contenedor.innerHTML = "";

    const esFiltroGeneral = (filtroActual === "todas" || filtroActual === "todos");
    
    let semanasAMostrar = agendaGlobal;
    if (esFiltroGeneral) {
        semanasAMostrar = agendaGlobal.slice(0, 3);
    }

    semanasAMostrar.forEach(semana => {
        let HTMLTarjetasCategorias = "";
        let eventosVisiblesCount = 0;

        if (!semana.eventos) return;

        semana.eventos.forEach(evento => {
            const claseEvento = (evento.categoriaClase || "").toLowerCase().trim();

            if (!esFiltroGeneral && claseEvento !== filtroActual) {
                return;
            }

            eventosVisiblesCount++;

            const sesionesPorDia = {};
            if (evento.sesiones) {
                evento.sesiones.forEach(sesion => {
                    if (!sesionesPorDia[sesion.dia]) {
                        sesionesPorDia[sesion.dia] = [];
                    }
                    sesionesPorDia[sesion.dia].push(sesion);
                });
            }

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