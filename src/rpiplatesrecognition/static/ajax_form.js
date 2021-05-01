class AjaxForm {
    constructor(form_node, invalid_feedback_container_node, ajax_form_route, submit_btns) {
        this.form_node = form_node;
        this.invalid_feedback_container_node = invalid_feedback_container_node;

        submit_btns.forEach(button => {
            button.onclick = () => {
                const req = new XMLHttpRequest();
                req.open('POST', ajax_form_route);

                req.onload = () => {
                    const data = JSON.parse(req.responseText);

                    if (req.status === 201) {
                        location.reload();
                    }
                    else if (req.status === 409) {
                        // pop all warnings beforehand
                        this.pop_all_warnings();

                        for (var field in data.errors) {
                            const invalid_feedback = create_invalid_feedback(data.errors[field]);

                            this.invalid_feedback_container_node.appendChild(invalid_feedback);

                            const field_node = this.form_node.querySelector(`#${field}`);
                            field_node.classList.add('is-invalid');
                        }
                    }
                };

                const form_data = new FormData(this.form_node);
                req.send(form_data);
            };
        });
    }

    pop_all_warnings() {
        const fields = this.form_node.querySelectorAll('input');
        fields.forEach(field => {
            field.classList.remove('is-invalid');
        });

        const new_container = document.createElement('div');
        this.invalid_feedback_container_node.replaceWith(new_container);
        this.invalid_feedback_container_node = new_container;
    }
}

function create_invalid_feedback(error) {
    const el = document.createElement('div');
    el.className = 'invalid-feedback';
    el.style = 'display: block;';

    const text_node = document.createTextNode(error);
    el.appendChild(text_node);

    return el;
}
