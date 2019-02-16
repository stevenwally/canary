( () => {
    if (window.location.href.includes('/visualization')) {
        streamCount(SentimentValues) ? showResults() : hideResults()
    }

    function showResults() {
        $('#loader').hide();
        $('#donut').show();
        $('#positive').show();
        $('#neutral').show();
        $('#negative').show();
    }

    function hideResults() {
        $('#loader').show();
        $('#donut').hide();
        $('#positive').hide();
        $('#neutral').hide();
        $('#negative').hide();
    }

    function streamCount(values) {
        let results = false;
        Object.keys(values).map((key) => {
            if (values[key] > 0) {
                results = true;
            }
        });
        return results;
    }
})();
