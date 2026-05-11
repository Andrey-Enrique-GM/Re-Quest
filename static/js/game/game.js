// Valores iniciales
let vidas = 3;
let puntos = 0;
let idActual = 1;

document.addEventListener("DOMContentLoaded", function() {
    
    // Referencias al juego
    const uiVidas = document.getElementById('contador-vidas');
    const uiPuntos = document.getElementById('contador-puntos');
    const uiFrase = document.getElementById('frase'); 
    const inputRespuesta = document.querySelector('input[type="text"]'); 
    const btnAdivinar = document.querySelector('button.btn-primary'); 

    // 1. Cargar la pista desde Flask
    async function cargarPalabra(id) {
        try {
            const respuesta = await fetch(`/api/juego/palabra/${id}`);
            
            if (respuesta.status === 404) {
                // Si Flask devuelve 404, ya no hay más IDs = Ganó el juego
                uiFrase.innerText = "¡Misterio resuelto!";
                inputRespuesta.disabled = true;
                btnAdivinar.disabled = true;
                
                // Usando SweetAlert2
                if (typeof Swal !== 'undefined') {
                    Swal.fire('¡Felicidades!', `Completaste el juego con ${puntos} puntos.`, 'success');
                } else {
                    alert(`¡Felicidades! Completaste el juego con ${puntos} puntos.`);
                }
                return;
            }

            const datos = await respuesta.json();
            if (datos.status === 'ok') {
                // Colocamos la frase en el HTML
                uiFrase.innerText = datos.phrase; 
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
                
                // Cargar el siguiente nivel
                idActual++;
                cargarPalabra(idActual);
                
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
                uiFrase.innerText = "¡Fin del juego!";
                inputRespuesta.disabled = true;
                btnAdivinar.disabled = true;
                
                if (typeof Swal !== 'undefined') {
                    Swal.fire('¡Game Over!', 'Te has quedado sin vidas.', 'error');
                } else {
                    alert('¡Game Over! Te has quedado sin vidas.');
                }
            }
        }
    }

    // Permitir enviar con la tecla "Enter"
    inputRespuesta.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') btnAdivinar.click();
    });

    cargarPalabra(idActual);
});