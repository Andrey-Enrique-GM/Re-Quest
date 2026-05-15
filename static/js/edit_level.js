document.addEventListener('DOMContentLoaded', function(){
    const select = document.getElementById('select-level');
    const inputWord = document.getElementById('input-word');
    const inputPhrase = document.getElementById('input-phrase');
    const btnSave = document.getElementById('btn-save');
    const saveMsg = document.getElementById('save-msg');

    function showSwalMessage(msg, success){
        if (typeof Swal !== 'undefined'){
            if(success){
                Swal.fire({
                    icon: 'success',
                    title: 'Guardado',
                    text: msg,
                    timer: 1500,
                    showConfirmButton: false
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: msg,
                });
            }
        } else {
            // fallback to console
            console.log((success? 'OK: ':'ERR: ')+msg);
        }
    }

    // cargar ids
    fetch('/api/words').then(r=>r.json()).then(data=>{
        const ids = data.ids || [];
        select.innerHTML = '';
        ids.forEach(id=>{
            const opt = document.createElement('option');
            opt.value = id;
            opt.textContent = id;
            select.appendChild(opt);
        });
        if(ids.length>0){
            select.value = ids[0];
            loadById(ids[0]);
        }
    }).catch(e=>console.error(e));

    function loadById(id){
        fetch(`/api/words/${id}`).then(r=>r.json()).then(data=>{
            if(data && !data.error){
                inputWord.value = data.word || '';
                inputPhrase.value = data.phrase || '';
            }
        }).catch(e=>console.error(e));
    }

    select.addEventListener('change', function(){
        loadById(this.value);
    });

    btnSave.addEventListener('click', function(){
        const id = select.value;
        const payload = { word: inputWord.value.trim(), phrase: inputPhrase.value.trim() };
        fetch(`/api/words/${id}`, {
            method: 'POST',
            headers: { 'Content-Type':'application/json' },
            body: JSON.stringify(payload)
        }).then(r=>r.json()).then(resp=>{
            if(resp.success){
                showSwalMessage('Guardado correctamente', true);
            }else{
                showSwalMessage(resp.message || 'Error al guardar', false);
            }
        }).catch(e=>{
            console.error(e);
            showSwalMessage('Error de red', false);
        });
    });
});
