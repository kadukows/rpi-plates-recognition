class AjaxForm extends EventTarget {
    constructor(form_node, ajax_form_route, submit_btns) {
        super();
        this.form_node = form_node;
        this.ajax_form_route = ajax_form_route;

        this.invalid_feedbacks = [];

        submit_btns.forEach(button => {
            button.onclick = () => { this.fake_submit(); };
        });

        this.form_node.onsubmit = () => {
            this.fake_submit();
            return false;
        };
    }

    fake_submit() {
        const req = new XMLHttpRequest();
        req.open('POST', this.ajax_form_route);

        req.onload = () => {
            if (req.status === 201) {
                const event = new CustomEvent('validatedAndSubmitted');
                this.dispatchEvent(event);
            }
            else if (req.status === 409) {
                // pop all warnings beforehand
                this.pop_all_warnings();

                const data = JSON.parse(req.responseText);

                for (var field in data.errors) {
                    const invalid_feedback = create_invalid_feedback(data.errors[field]);
                    this.invalid_feedbacks.push(invalid_feedback);

                    var field_node = this.form_node.querySelector(`#${field}`);
                    if (field_node === null) {
                        // hack for 'remote' inputs to form
                        const possible_fields = [...document.querySelectorAll(`#${field}`)];
                        field_node = possible_fields.find(el => {
                             return el.form === this.form_node;
                        });
                    }
                    if (field_node !== null && field_node !== undefined) {
                        field_node.parentNode.insertBefore(invalid_feedback, field_node.nextSibling);
                        field_node.classList.add('is-invalid');
                    }
                }
            }
        };

        const form_data = new FormData(this.form_node);
        req.send(form_data);
    }

    pop_all_warnings() {
        const fields = this.form_node.querySelectorAll('input');
        fields.forEach(field => {
            field.classList.remove('is-invalid');
        });

        //const new_container = document.createElement('div');
        //this.invalid_feedback_container_node.replaceWith(new_container);
        //this.invalid_feedback_container_node = new_container;
        this.invalid_feedbacks.forEach(node => {
            node.remove();
        });
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
