setTimeout( () => {
    $.ajax({
        url: "{% url 'canary:visualization' %}"
    })
    .done( (data) => {
        $('body').html(data);
    });
}, 3000);

