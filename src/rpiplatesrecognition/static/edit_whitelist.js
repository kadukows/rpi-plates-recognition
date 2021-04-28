document.addEventListener("DOMContentLoaded", () => {
    document.querySelector('#editModal').on('show.bs.modal', event => {
        var button = document.querySelector(event.relatedTarget);
        console.log(button);
    });


});
