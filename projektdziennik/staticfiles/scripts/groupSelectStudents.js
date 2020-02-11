// select student by clicking on the li element
// add selected to array and remove from unselectedStudents ul
// display selected in selelctedStudent ul with a div with cross to remove them
// when cross clicked - remove item from array, add it back to options, redispaly div with current array items
// when submit clicked use only items from array to be posted

let serchBox = document.getElementById('studentSearch');
let unselectedStudents = document.getElementById('unselectedStudents');
let selectedStudents = document.getElementById('selectedStudents');
let selectedStudentsArray = [];
let groupForm = document.getElementById('groupForm');

unselectedStudents.addEventListener('click', selectStudent);
selectedStudents.addEventListener('click', unselectStudent);
serchBox.addEventListener('input', searchStudents)
groupForm.addEventListener('submit', submitForm);

function submitForm(e) {
    e.preventDefault();
    genereateStudentSelect();
    console.log('group form: ', groupForm)
    this.submit();
}

function genereateStudentSelect() {
    let sel = document.createElement('select')
    sel.name = 'student'
    sel.multiple = true;
    for (let s of selectedStudentsArray) {
        console.log(s);
        let o = document.createElement('option');
        o.value = s.id
        o.selected = true;
        sel.appendChild(o)
    }
    console.log('sel: ', sel)
    groupForm.appendChild(sel);
}

function selectStudent(e) {
    let li = e.target
    if (li.classList.contains('students')) {
        li.remove();
        addStudentToSelected(li);
        refreshSelected();
    }
}

function unselectStudent(e) {
    let el = e.target
    if (el.classList.contains('delete')) {
        let li = el.parentNode
        li.remove();
        addStudentToUnselected(li)
        refreshSelected();
    }
}

function addStudentToSelected(li) {
    let deleteBtn = document.createElement('div');
    deleteBtn.className = "btn btn-danger btn-sm float-right py-0 delete";
    deleteBtn.appendChild(document.createTextNode('x'));
    li.appendChild(deleteBtn);
    selectedStudentsArray.push(li);
}

function addStudentToUnselected(li) {
    // add to unselectedStudents, remove deleteBtn, remove from selectedStudentsArray
    unselectedStudents.appendChild(li);
    li.lastChild.remove();
    selectedStudentsArray = selectedStudentsArray.filter(el => el !== li)
}

function refreshSelected() {
    for (let el of selectedStudentsArray) {
        selectedStudents.appendChild(el);
    }
}

function searchStudents() {
    resetHide();
    let searchTerm = this.value.toLowerCase();
    for (let o of unselectedStudents.children) {
        if (o.innerText.toLowerCase().includes(searchTerm) == false) {
            o.classList.add('d-none');
        }
    }
}

function resetHide() {
    for (let o of unselectedStudents.children) {
        o.classList.remove('d-none');
    }
}
