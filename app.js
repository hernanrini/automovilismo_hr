document.addEventListener("DOMContentLoaded", () => {
    cargarAgenda();
});

async function cargarAgenda() {
    try {
        const respuesta = await fetch("carreras.json");
        const semanas = await respuesta.json();
        
        const contenedor = document.getElementById("contenedor-principal");
        contenedor.innerHTML = "";

        semanas.forEach(semana => {
            const bloque = document.createElement("section");
            bloque.className = `bloque-finde ${semana.semana === 1 ? 'actual' : ''}`;

            let HTMLTarjetasCategorias = "";

            // Nivel 2: Iterar Categorías Principales (F1, NASCAR, TN, IndyCar, etc.)
            semana.eventos.forEach(evento => {
                
                // Nivel 3: Agrupar por Día todas las sesiones de la categoría y sus divisionales
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

                        // Badge para identificar la divisional si es secundaria (ej. F2, F3, WRC2, Xfinity)
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

    } catch (error) {
        console.error("Error al cargar la agenda de Automovilismo_HR:", error);
    }
}