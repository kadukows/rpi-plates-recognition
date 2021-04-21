document.addEventListener("DOMContentLoaded", () => {
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
});
