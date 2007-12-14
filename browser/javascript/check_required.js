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
       
    // Private methods
    var check = function () {
        var checksOut = true; // Uncharastic optimisim
        var i = 0;
        var widget = null;
        var numWidgets = widgets.length;
        for (i=0; i < numWidgets; i++) {
            widget = widgets[i];
            checksOut = checksOut && check_widget(widget);
        }
        if ( checksOut ) {
            jQuery(button).attr("disabled", "");
        } else {
            jQuery(button).attr("disabled", "disabled");
        }
    }

    var check_widget = function(widget) {
        var retval = false;
        retval = jQuery(widget).val() != '';
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
        }
    };
}(); // GSCheckRequired

