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
    //
    //  Buttons for shwoing different access attempts
    //
    //

    const img_src_output = document.querySelector("#src-image-output");
    const edge_projection_table_ouput = document.querySelector("#edge-projection-output");
    const segmentation_table_output = document.querySelector("#segmentation-output");

    var buttons = document.querySelectorAll(".show-access-attempt-button");
    buttons.forEach(button => {
        button.onclick = function() {
            const access_attempt_id = this.dataset.accessAttemptId;
            const req = new XMLHttpRequest();
            req.open('GET', `/rpi_connection/get_images_for_access_attempt/${access_attempt_id}`);

            req.onload = () => {
                const data = JSON.parse(req.responseText);
                if (Object.keys(data).length !== 0) {
                    img_src_output.src = data['img_src'];


                    const edge_projection_images = data['edge_proj'];
                    const segmentation_images = data['segments'];

                    replace_old_tbody(edge_projection_images, edge_projection_table_ouput);
                    replace_old_tbody(segmentation_images, segmentation_table_output);
                }
            }

            req.send();
        }
    });
});

function replace_old_tbody(img_links, table) {
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
        cell_img.appendChild(cell_img_img);
        row.appendChild(cell_img);

        tbody.append(row);
        i += 1;
    });
}
