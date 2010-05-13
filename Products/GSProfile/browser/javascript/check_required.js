// GroupServer module for checking required form fields.
jQuery.noConflict();
GSCheckRequired = function () {
    /* GroupServer Check Required Form Fields
    
        To function correctly, some forms require that particular fields
        have been filled out. This module provides this check.
    
        FUNCTIONS
          init:   Add the code to check the required-fields.
    
    */

    // Private variables
    var widgets = null;
    var button = null;
    var list = null;
       
    // Private methods
    var check = function () {
        var checksOut = true; // Uncharastic optimisim
        var widgetChecksOut = true; // Uncharastic optimisim
        var i = 0;
        var widget = null;
        var numWidgets = widgets.length;
        var submitButton = null;
        var unfinished = new Array();
        
        submitButton = jQuery(button);
        for ( i=0; i < numWidgets; i++ ) {
            widget = widgets[i];
            widgetChecksOut = check_widget(widget);
            checksOut = checksOut && widgetChecksOut;
            if ( !widgetChecksOut ) {
                unfinished.push(widget);
            }
        }
        if ( checksOut ) {
            submitButton.removeAttr("disabled");
        } else {
            submitButton.attr("disabled", "disabled");
            alert(unfinished);
        }
        return true;
    }

    var check_widget = function(widget) {
        var retval = false;
        var w = null;
        var val = null;
        var a = null;
        var b = null;
        var c = null
        w = jQuery(widget);
        
        val = w.val();
        a = (val != '');
        b = (val != null);
        c = (val != undefined);
        retval = a;// && (b || c);
        return retval;
    }

    // Public methods and properties
    return {
        init: function (w, b) {
            /*  Add the required-field checking code to the widgets
                
                arguments
                  w:  An array of IDs, for the required form elements.
                  b:  A string for the submit button for the form.
            */
            button = b;
            widgets = w;
                        
            var i = 0;
            for ( i in widgets ) {
                jQuery(widgets[i]).keyup(function(event) {
                    check();
                });
            }
            check();
        },
        init_list: function(w, b, l) {
            /*  Add the required-field checking code to the widgets
                
                arguments
                  w:  An array of IDs, for the required form elements.
                  b:  A string for the submit button for the form.
                  l:  A string for the UL that lists the unfilled fields.
            */
            button = b;
            widgets = w;
            list = l;
                        
            var i = 0;
            for ( i in widgets ) {
                jQuery(widgets[i]).keyup(function(event) {
                    check();
                });
            }
            check();          
        }
    };
}(); // GSCheckRequired

