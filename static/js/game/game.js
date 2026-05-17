// Valores iniciales
let vidas = 3;
let puntos = 0;
let idActual = 1;
const TYPING_SPEED = 50;

document.addEventListener("DOMContentLoaded", function() {
    
    // Referencias al juego
    const uiVidas = document.getElementById('contador-vidas');
    const uiPuntos = document.getElementById('contador-puntos');
    const uiNivel = document.getElementById('nivel-actual');
    const uiFrase = document.getElementById('frase'); 
    const inputRespuesta = document.querySelector('input[type="text"]'); 
    const btnAdivinar = document.querySelector('button.btn-primary'); 
    const MAX_NIVEL = 5;

    function actualizarNivel() {
        uiNivel.innerText = `Nivel ${idActual}`;
    }

    async function mostrarVictoria() {
        await guardarGanador(puntos);

        escribirTextoRPG("¡Misterio resuelto!");
        inputRespuesta.disabled = true;
        btnAdivinar.disabled = true;

        if (typeof Swal !== 'undefined') {
            Swal.fire('¡Felicidades!', `Completaste el juego con ${puntos} puntos.`, 'success');
        } else {
            alert(`¡Felicidades! Completaste el juego con ${puntos} puntos.`);
        }
    }

    async function guardarGanador(score) {
        try {
            const response = await fetch('/api/juego/guardar_ganador', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ score })
            });
            const result = await response.json();

            if (!response.ok) {
                console.error('Error guardando ganador:', result.message || result);
            }
        } catch (error) {
            console.error('Error en la petición de guardado del ganador:', error);
        }
    }

    // 1. Cargar la pista desde Flask
    async function cargarPalabra(id) {
        try {
            const respuesta = await fetch(`/api/juego/palabra/${id}`);
            
            if (respuesta.status === 404) {
                // Si Flask devuelve 404, ya no hay más IDs = Ganó el juego
                await mostrarVictoria();
                return;
            }

            const datos = await respuesta.json();
            if (datos.status === 'ok') {
                // Colocamos la frase en el HTML
                escribirTextoRPG(datos.phrase); 
            }

        } catch (error) {
            console.error("Error al cargar la pista:", error);
        }
    }

    //  Validar el intento
    btnAdivinar.addEventListener("click", async function() {
        const intento = inputRespuesta.value;
        if (intento.trim() === "") return;

        try {
            const respuesta = await fetch('/api/juego/validar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: idActual, intento: intento })
            });

            const resultado = await respuesta.json();

            if (resultado.correcto) {
                // Adivinó correctamente
                puntos += 100;
                uiPuntos.innerText = puntos;
                inputRespuesta.value = ""; 

                // Avanzar al siguiente nivel o mostrar victoria
                if (idActual < MAX_NIVEL) {
                    idActual++;
                    actualizarNivel();
                    cargarPalabra(idActual);
                } else {
                    mostrarVictoria();
                }
            } else {
                // Se equivocó
                inputRespuesta.value = ""; 
                perderVida();
            }

        } catch (error) {
            console.error("Error en la validación:", error);
        }
    });

    // 3. Control de Vidas
    function perderVida() {
    if (vidas > 0) {
        vidas--;
        uiVidas.innerText = vidas;
        
        inputRespuesta.classList.add('is-invalid', 'border-danger');
        setTimeout(() => inputRespuesta.classList.remove('is-invalid', 'border-danger'), 800);
        
        if (vidas === 0) {
            
            
            const gameOverContainer = document.getElementById('game-over-container');
            gameOverContainer.style.display = 'flex';
            
            inputRespuesta.disabled = true;
            btnAdivinar.disabled = true;
        }
    }
}

    inputRespuesta.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') btnAdivinar.click();
    });

    actualizarNivel();
    cargarPalabra(idActual);
});

function escribirTextoRPG(texto) {
    const contenedor = document.getElementById('frase-typing');
    
   
    contenedor.innerHTML = ''; 

    
    const textList = texto.split('');
    let html = '';
    for (const char of textList) {
        html += `<span>${char}</span>`;
    }
    contenedor.innerHTML = html;

    const spans = contenedor.querySelectorAll('span');
    let delay = 0;

    for (let i = 0; i < spans.length; i++) {
        const span = spans[i];
        const charText = span.textContent;

        delay += TYPING_SPEED;
        
        if (charText === ' ') delay += TYPING_SPEED * 2; 

       
        setTimeout(() => {
            span.style.display = 'inline-block';
        }, delay);
    }
}