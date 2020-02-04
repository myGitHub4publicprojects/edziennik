let serchBox = document.getElementById('selectWithSearch').getElementsByTagName('input')[0];
let selectEl = document.getElementById('selectWithSearch').getElementsByTagName('select')[0];

serchBox.addEventListener('input', function () {
    resetHide();
    let searchTerm = this.value.toLowerCase();
    for (let o of selectEl.children) {
        if (o.innerText.toLowerCase().includes(searchTerm) == false && o.value != '') {
            o.className = 'd-none';
        }
    }
    selectEl.selectedIndex = 0;
})

function resetHide() {
    for (let o of selectEl.children) {
        o.className = '';
    }
}

selectEl.addEventListener('focus', function () {
    serchBox.classList.remove('d-none');
    selectEl.selectedIndex = 0;
})