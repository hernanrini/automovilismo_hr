function renderizarAgenda() {
    const contenedor = document.getElementById("contenedor-principal");
    if (!contenedor) return;
    
    contenedor.innerHTML = "";

    const esFiltroGeneral = (filtroActual === "todas" || filtroActual === "todos");
    
    // Obtenemos la fecha actual en formato YYYY-MM-DD para comparar (hoy es 26/09/2026)
    const hoyStr = new Date().toISOString().split('T')[0];

    // 1. Filtrar primero todas las semanas para eliminar las que ya pasaron por completo
    let semanasAMostrar = agendaGlobal.filter(semana => {
        // Una semana es válida si al menos uno de sus eventos tiene alguna sesión hoy o en el futuro
        return semana.eventos.some(evento => {
            return evento.sesiones.some(sesion => {
                const fechaSesion = (sesion.fechaUtc || "").split('T')[0];
                return fechaSesion >= hoyStr;
            });
        });
    });

    // 2. Si es la vista general, limitamos opcionalmente a las 3 próximas semanas vigentes
    if (esFiltroGeneral) {
        semanasAMostrar = semanasAMostrar.slice(0, 3);
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