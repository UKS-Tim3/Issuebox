function invoke_typeahead(url) {

    // Instantiate the Bloodhound suggestion engine
    var contributors = new Bloodhound({
//         datumTokenizer: function (datum) {
//            return Bloodhound.tokenizers.obj.whitespace;
//            return Bloodhound.tokenizers.obj.whitespace(datum.label);
//        },
        identify: function(obj) { return obj.label; },
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('label'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: {
            url: url + '?query=%QUERY',
            wildcard: '%QUERY',
            filter: function (contributors) {
                // Map the remote source JSON array to a JavaScript object array
                return $.map(contributors, function (contributor) {
                    return {
                        label: contributor.username,
                        value: contributor
                    };
                });
            }
        }
    });

    // Initialize the Bloodhound suggestion engine
    contributors.initialize();

    // Instantiate the Typeahead UI
    $('#typeahead').typeahead(
        {
            hint: true,
            highlight: true,
            minLength: 1,
//            limit: 10,
        }
        , {
            displayKey: 'label',
            valueKey: 'label',
            source: contributors,
            templates: {
                empty: [
                    '<div class="empty-message">',
                    'Unable to find any contributors that match the current query!',
                    '</div>'
                ].join('\n'),
                // suggestion: Handlebars.compile('<div><strong>{{value.username}}</strong> – {{username}} = {{first_name}} - {{value}}</div>'),
                suggestion: function (data) {
                    // return '<div><strong>' + data.value.username + '</strong> – ' + data.value.first_name + ' - ' + data.value.last_name + '</div>';
                    var obj = data.value;
                    var html = ''
                        + '<div class="media">'
                        + '<div class="media-left">'
                        + '<a href="#">'
                        + '<img class="media-object img-circle center-image"'
                        + ' src="' + obj.img_url + '" alt="No image" width="48" height="48"/>'
                        + '</a>'
                        + '</div>'
                        + '<div class="media-body">'
                        + '<h4 class="media-heading"><b>' + obj.username + '</b></h4>'
                        + '<h5 class="media-heading">' + obj.first_name + '&nbsp;' + obj.last_name
                        + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[' + obj.email + ']</h5>'
                        + '</div>'
                        + '</div>'
                    ;
                    return html;
                },
                // footer: Handlebars.compile("<b>Searched for '{{query}}'</b>")
            }
    });

}