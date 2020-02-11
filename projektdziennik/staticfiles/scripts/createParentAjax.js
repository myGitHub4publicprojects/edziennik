let parent_first_name = document.getElementById('id_parent_first_name');
let parent_last_name = document.getElementById('id_parent_last_name');
let email = document.getElementById('id_email');
let phone_number = document.getElementById('id_phone_number');
let btnShowParentForm = document.getElementById('btnShowParentForm');
parentEls = [parent_first_name, parent_last_name, phone_number, email];

setRequiredFalse(parentEls);

function setRequiredFalse(arr) {
    for (let inp of arr) {
        inp.required = false;
    }
};

function setRequiredTrue(arr) {
    for (let inp of arr) {
        inp.required = true;
    }
};

document.getElementById('acceptBtn').addEventListener('click', function () {

    // reset input errors
    resetInputErros(parentEls);
    // make inputs required
    setRequiredTrue([parent_first_name, parent_last_name, phone_number]);
    // INITIAL VALIDATION - CLIENT SIDE
    // if errors: add 'is-invalid' class to input and div class="invalid-feedback">  
    let inputsFilled = emptyInvalid(
        [parent_first_name, parent_last_name, phone_number], "To pole jest wymagane");
    let phoneValid = lengthPhoneInvalid(phone_number, 'Numer telefonu musi mieć 9 cyfr');
    let emailValid = emailValidation(email, "Niepoprawny format adresu email")
    // if any errors in intial validation do not send data to server
    if (inputsFilled && phoneValid && emailValid) {
        let data = ('parent_first_name=' + parent_first_name.value +
            '&parent_last_name=' + parent_last_name.value +
            '&phone_number=' + phone_number.value +
            '&email=' + email.value)
        let token = document.getElementsByName('csrfmiddlewaretoken')[0].value;

        fetch(urlParentAjax, {
            method: 'POST',
            headers: {
                // 'Content-Type': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded',
                "X-CSRFToken": token
            },
            body: data
        })
            .then((response) => response.json())
            .then((data) => {
                console.log('Success:', data);
                if (data.result == 'Error') {
                    console.log('result == Err');
                    processParentErrors(data.errors);
                }
                if (data.result == 'Success!') {
                    console.log('result == Scs');
                    processNewParent(data.parent)
                }
            })
            .catch((error) => {
                console.log('Error:', error);
            });
    }
});

function resetInputErros(parentEls) {
    for (let el of parentEls) {
        // remove is-invalid class
        el.classList.remove("is-invalid");
        // remove all div class="invalid-feedback"
        for (let elInner of el.parentNode.getElementsByClassName('invalid-feedback')) {
            elInner.remove();
        }
    }
}

function emptyInvalid(elList, msg) {
    let noErrors = true;
    for (let el of elList) {
        if (el.value == '') {
            addErrors(el, msg)
            noErrors = false
        }
    }
    return noErrors
}

function emailValidation(email, msg) {
    if (validateEmail(email.value) == false && email.value != '') {
        addErrors(email, msg)
        return false
    }
    return true
}

function lengthPhoneInvalid(phone_number, msg) {
    if (phone_number.value.length != 9) {
        addErrors(phone_number, msg)
        return false
    }
    return true
}

function addErrors(el, msg) {
    el.classList.add("is-invalid");
    let errorInfo = document.createElement('div');
    errorInfo.className = 'invalid-feedback';
    let errorMsgText = document.createTextNode(msg);
    errorInfo.appendChild(errorMsgText);
    el.parentNode.appendChild(errorInfo)
}

function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

function processNewParent(parent) {
    // hide parent create div
    document.getElementById('parentDiv').className = 'd-none';
    // add new parent to student's parent select input
    let newOption = cerateNewOption(parent);
    // select new parent
    selectNewParent(parent, newOption);
}

function processParentErrors(errors) {
    for (let err in errors) {
        let el = document.getElementById('id_' + err);
        let messageList = errors[err];
        for (let message of messageList) {
            addErrors(el, message)
        }
    }
}

function cerateNewOption(parent) {
    let newOption = document.createElement('option');
    let optionText = document.createTextNode(parent.details);
    newOption.value = parent.id;
    newOption.appendChild(optionText);
    return newOption
}

function selectNewParent(parent, newOption) {
    let parentSelect = document.getElementById('id_parent')
    parentSelect.appendChild(newOption);
    for (let o of parentSelect.options) {
        if (o.value == parent.id) {
            o.selected = true
        }
    }
}

function resetInputValues(parentEls) {
    for (let el of parentEls) {
        el.value = '';
    }
}

function cancelParentCreation(e) {
    resetInputValues(parentEls);
    setRequiredFalse(parentEls);
    // hide parent form
    e.target.parentNode.className = 'd-none';
    // hide parent create btn

    // show create new parent btn
    btnShowParentForm.className = 'btn btn-primary btn-sm mb-3';
}

document.getElementById('cancelBtn').addEventListener('click', cancelParentCreation);

btnShowParentForm.addEventListener('click', function (e) {
    e.target.nextElementSibling.className = 'd-block';
    e.target.classList += ' d-none';
});