class EditableParamManager {
    constructor (td, regex, original_param_value) {
        this.td = td;
        this.regex = regex;
        this.original_param_value = original_param_value;

        td.addEventListener('input', () => { this.on_input(); });
    }

    on_input() {
        if (this.regex.test(this.td.innerText)) {
            if (this.td.innerText.replace(/^\s+|\s+$/g, '') === this.original_param_value) {
                this.reset();
            }
            else {
                this.different();
            }
        }
        else {
            this.wrong_syntax();
        }
    }

    reset() {
        this.td.classList = this.td.classList.remove('table-danger', 'table-warning')
    }

    different() {
        if (!this.td.classList.contains('table-warning')) {
            this.reset();
            this.td.classList.add('table-warning');
        }
    }

    wrong_syntax() {
        if (!this.td.classList.contains('table-danger')) {
            this.reset();
            this.td.classList.add('table-danger')
        }
    }

    is_valid() {
        return !this.td.classList.contains('table-danger');
    }

    to_data() {
        throw "Method not implemented!";
    }
}

class EditableParamManagerSingleInt extends EditableParamManager {
    constructor(td, original_param_value) {
        super(td, /^\d+\s*$/, original_param_value);
    }

    to_data() {
        return parseInt(this.td.innerText);
    }
}

class EditableParamManagerTupleInts extends EditableParamManager {
    constructor(td, original_param_value) {
        super(td, /^((\d+),\s*)+(\d+)\s*$/, original_param_value);
    }

    to_data() {
        const match_arr = [...this.td.innerText.matchAll(/\d+/g)];
        const result = [];

        match_arr.forEach(match => {
            result.add(parseInt(match[0]));
        });

        return result;
    }
}

class ParamsTableManager {
    constructor (module_params, table_node) {
        this.module_params = module_params;
        this.table_node = table_node;

        this.fill_table_with_original_params();
        //this.hook_up_table_with_diff_viewer();
    }

    fill_table_with_original_params() {
        const old_tbody = this.table_node.querySelector('tbody');
        const tbody = document.createElement('tbody');
        old_tbody.replaceWith(tbody);

        for (var key in this.module_params) {
            if (this.module_params.hasOwnProperty(key)) {
                const tr = document.createElement('tr');

                const td_param_name = document.createElement('td');
                td_param_name.dataset.paramKey = key;
                td_param_name.classList.add('td-param-name');
                add_text_node(td_param_name, key);
                tr.appendChild(td_param_name);

                const td_module_value = document.createElement('td');
                td_module_value.dataset.paramKey = key;
                td_module_value.innerHTML = this.module_params[key];
                td_module_value.classList.add('td-module-value')
                td_module_value.contentEditable = "true";
                td_module_value.editableParamManager = new EditableParamManager(td_module_value, /^\d+\s?$/, this.module_params[key]);
                tr.appendChild(td_module_value);

                tbody.appendChild(tr);
            }
        }
    }

    hook_up_table_with_diff_viewer() {
        const tds =  this.table_node.querySelectorAll('.td-module-value');
        tds.forEach(td => {
            td.addEventListener('input', () => {
                //const testing_value = ttd.innerText.replace(/^\s+|\s+$/g, '')
                if (this.td.innerText.replace(/^\s+|\s+$/g, '') != this.module_params[td.dataset.paramKey]) {
                    if (!td.classList.contains('table-danger')) {
                        td.classList.add('table-danger');
                    }
                }
                else {
                    console.log('IS SAME');
                    if (td.classList.contains('table-danger')) {
                        td.classList = td.classList.filter(className => {
                            return className !== 'table-danger'
                        });
                    }
                }
            })
        });
    }
}

function add_text_node(node, text) {
    const text_node = document.createTextNode(text);
    node.appendChild(text_node);
}

var global_table_manager = null;

document.addEventListener("DOMContentLoaded", () => {

    //
    //
    //  WebSocket, chat with RPI JS
    //
    //
    const form = document.querySelector('#command_form');
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/rpi');

    socket.on('connect', () => {
        socket.emit('join_rpi_room_from_client', {'unique_id': form.dataset.unique_id});
    });

    // implement handling message from server

    socket.on('message_from_server_to_client', data => {
        document.querySelector('#output').innerHTML += data.toString() + '<br>';
    });

    form.onsubmit = () => {
        const commandsInput = form.querySelector('#commandsInput');
        socket.emit('message_from_client', {'command': commandsInput.value});

        commandsInput.value = '';

        return false;
    };

    //
    // AJAX initial query for access attempts
    //

    const accordion = document.querySelector('#accordion');
    const req = new XMLHttpRequest();
    req.open('GET', `/rpi_connection/get_access_attempts/${form.dataset.unique_id}`);

    req.onload = () => {
        const data = JSON.parse(req.responseText);
        data.forEach(access_attempt => { add_access_attempt(access_attempt); });
    };

    req.send();


    //
    // handle access attempts that are coming through
    //

    socket.on('new_access_attempt_from_server_to_client', data => {
        const access_attempt = JSON.parse(data);
        add_access_attempt(access_attempt);
    });

    //
    // AJAX query for module's params
    //

    const module_param_req = new XMLHttpRequest();
    module_param_req.open('GET', `/rpi_connection/get_module_params/${form.dataset.unique_id}`);

    module_param_req.onload = () => {
        const params = JSON.parse(module_param_req.responseText);
        const table = document.querySelector('#table-params-output');

        global_table_manager = new ParamsTableManager(params, table);
    }

    module_param_req.send();
});

function add_access_attempt(access_attempt, accordion = null) {
    if (accordion === null) {
        accordion = document.querySelector('#accordion');
    }

    const card = create_card(access_attempt);
    const collapsible = create_collapsible(access_attempt['id']);

    accordion.insertBefore(collapsible, accordion.firstChild);
    accordion.insertBefore(card, accordion.firstChild);
}

function add_callback_to_show_access_btn(button) {
    button.fetched = false;
    button.onclick = function () {
        if (this.fetched === true) {
            return;
        }

        this.fetched = true;

        const access_attempt_id = this.dataset.accessAttemptId;
        const collapsible = document.querySelector(button.dataset.target);
        const img_src_output = collapsible.querySelector('.img-src');
        const img_segments_output = collapsible.querySelector('.img-segments');
        const img_projection_table_output = collapsible.querySelector('.table-projection');

        const req = new XMLHttpRequest();
        req.open('GET', `/rpi_connection/get_images_for_access_attempt/${access_attempt_id}`);

        req.onload = () => {
            const data = JSON.parse(req.responseText);
            if (Object.keys(data).length !== 0) {
                img_src_output.src = data['img_src'];
                img_segments_output.src = data['segments'][0];

                replace_old_tbody_img(data['edge_proj'], img_projection_table_output);
            }
        };

        req.send();
    }
}

function replace_old_tbody_img(img_links, table) {
    const old_tbody = table.getElementsByTagName('tbody')[0];
    const tbody = document.createElement('tbody');
    old_tbody.replaceWith(tbody);

    var i = 1;
    img_links.forEach(img_link => {
        var row = document.createElement("tr");

        var cell_no = document.createElement("td");
        var cell_no_text = document.createTextNode(`${i}`);
        cell_no.appendChild(cell_no_text);
        row.appendChild(cell_no);

        var cell_img = document.createElement("td");
        var cell_img_img = document.createElement("img");
        cell_img_img.src = img_link;
        cell_img_img.classList.add('img-responsive')
        cell_img.appendChild(cell_img_img);
        row.appendChild(cell_img);

        tbody.append(row);
        i += 1;
    });
}

function create_card(access_attempt) {
    const template = document.createElement('template');
    template.innerHTML = `
    <div class="card mb-3 shadow">
        <div class="card-header">
            <h5 class="mb-0">
                <button class="btn btn-link show-access-attempt-btn"
                    data-toggle="collapse" data-target="#access-attempt-card-${access_attempt['id']}"
                    data-access-attempt-id="${access_attempt['id']}">
                    Access attempt: #${access_attempt['id']} | ${access_attempt['date']} | ${access_attempt['plate']}
                </button>
            </h5>
        </div>
    </div>
    `;

    const result = template.content.cloneNode(true);

    const button = result.querySelector('button');
    add_callback_to_show_access_btn(button);

    const card = result.querySelector('.card');
    setTimeout(() => { card.classList.add('animate'); }, 100);

    return result;
}

function create_collapsible(access_attempt_id) {
    const template = document.createElement('template');
    template.innerHTML = `
    <div id="access-attempt-card-${access_attempt_id}" class="collapse hidden" data-parent="#accordion">
        <div class="card-body">
            <div class="container">
                <div class="row" style="min-height: 300px;">
                    <div class="col-md-8">
                        <img class="img-responsive img-rounded img-src" style="max-width: 100%;">
                    </div>
                    <div class="col-md-4">
                        <div class="row">
                            <div class="col-md-12">
                                <img class="img-responsive img-rounded img-segments" style="max-width: 100%;">
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-12">
                                <table class="table table-hover table-projection">
                                    <tbody>

                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `;

    return template.content.cloneNode(true);
}
