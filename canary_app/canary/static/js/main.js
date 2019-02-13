$(all_sentiment).each( function(i) {
    console.log(all_sentiment[i]);
    if (all_sentiment[i] === 0) {
        $('#loader').show();
        $('#donut').hide();
        $('#positive').hide();
        $('#neutral').hide();
        $('#negative').hide();
    } else {
        $('#loader').hide();
        $('#donut').show();
        $('#positive').show();
        $('#neutral').show();
        $('#negative').show();
    }
});
