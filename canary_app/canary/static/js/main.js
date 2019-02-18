( () => {
    if (window.location.href.includes('/visualization')) {
        streamCount(SentimentValues) ? showResults() : hideResults();
    }

    function showResults() {
        $('#loader').hide();
        $('.viz-elements').show();
    }

    function hideResults() {
        $('#loader').show();
        $('.viz-elements').hide();
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
