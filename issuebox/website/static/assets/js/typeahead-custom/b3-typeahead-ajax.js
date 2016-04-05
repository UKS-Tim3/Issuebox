// big thanks to http://fusiongrokker.com/post/heavily-customizing-a-bootstrap-typeahead
// https://github.com/bassjobsen/Bootstrap-3-Typeahead

function invoke_typeahead(url) {

    var contributors = {};
    var contributor_labels = [];
    var global_query = '';

    $( "#typeahead" ).typeahead({
        source: function ( query, process ) {

            global_query = query;

            // resetting value in generated hidden field and triggering change event
//            var current_val = $( "#id_contributor_id" ).val();
//            if(current_val != '') {
                $( "#id_contributor_id" ).val('').trigger('change');
//            }

            // the "process" argument is a callback, expecting an array of values (strings) to display

            // get the data to populate the typeahead (plus some)
            // from your api, wherever that may be
            $.get( url, { query: query }, function (data) {

                // reset these containers
                contributors = {};
                contributor_labels = [];

                // for each item returned, if the display name is already included
                // (e.g. multiple "John Smith" records) then add a unique value to the end
                // so that the user can tell them apart.
                $.each( data, function( idx, item ) {
                    // not necessary if username is unique
                    if ( $.contains( contributors, item.username ) ){
                        item.username = item.username + ' #' + item.id;
                    }

                    // add the label to the display array
                    contributor_labels.push( item.username );

                    // also store a mapping to get from label back to object
                    // storing whole object as a value for item.username as key
                    contributors[ item.username ] = item;
                });

                //return the display array
                process( contributor_labels );
            });
        }

        , showHintOnFocus: true

        // called when item is selected
        // item is a value that is passed to the process() method
        , updater: function (item) {
            // saving value in generated hidden field and triggering change event
            $( "#id_contributor_id" ).val( contributors[ item ].id ).trigger('change');
            // return the string you want to go into the textbox (e.g. name)
            return item;
        }

        // optional, to disable exact match, e.g. enables 'string 1,string 2' search pattern
        , matcher: function () { return true; }

        // customization of item display, possible to create custom html for displaying items
        // item is a value that is passed to the process() method
        , highlighter: function (item) {
            var obj = contributors[ item ];

            // function that bolds every part of word that matches the current query
            function insert_highlight(word) {
                var highlighted_word = word;
                var index = word.toLowerCase().indexOf(global_query);
                if (global_query.length > 0 && index >= 0) {
                    highlighted_word = word.substr(0, index) + '<b>' + word.substr(index, global_query.length) + '</b>'
                            + insert_highlight(word.substr(index + global_query.length));
                }
                return highlighted_word;
            };

            var html = ''
                    + '<div class="media">'
                    + '<div class="media-left">'
                    + '<a href="#">'
                    + '<img class="media-object img-circle center-image"'
                    + ' src="' + obj.img_url + '" alt="No image" width="48" height="48"/>'
                    + '</a>'
                    + '</div>'
                    + '<div class="media-body">'
                    + '<h4 class="media-heading"><b>' + insert_highlight(obj.username) + '</b></h4>'
                    + '<h5 class="media-heading">' + insert_highlight(obj.first_name) + '&nbsp;' + insert_highlight(obj.last_name)
                    + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[' + insert_highlight(obj.email) + ']</h5>'
                    + '</div>'
                    + '</div>'
            ;

            return html;
        }
    });

};