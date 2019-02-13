setTimeout( () => {
    console.log('reload');
    $.ajax({
        url: "{% url 'canary:visualization' %}",
        success: function(data) {
            $('body').html(data);
        }
    });
}, 3000);

