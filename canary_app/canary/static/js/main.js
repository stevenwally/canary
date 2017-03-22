var streaming = false;
var start = document.getElementById('start-button')
var stop = document.getElementById('stop-button')


start.addEventListener('click', function() {
    streaming = true;
    if (streaming === true) {
        $(start).toggleClass('hidden');
        $(stop).toggleClass('hidden');
    } else {
        $(start).toggleClass('hidden');
        $(stop).toggleClass('hidden');
    };
});

stop.addEventListener('click', function() {
    streaming = false;
    if (streaming === true) {
        $(start).toggleClass('hidden');
        $(stop).toggleClass('hidden');
    } else {
        $(start).toggleClass('hidden');
        $(stop).toggleClass('hidden');
    };
});

