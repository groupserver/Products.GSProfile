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
        for ( i in widgets ) {
            checksOut = checksOut && (jQuery(widgets[i]).val() != '');
        }
        if ( checksOut ) {
            jQuery(button).attr("disabled", "");
        } else {
            jQuery(button).attr("disabled", "disabled");
        }
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
            jQuery(b).attr("disabled", "disabled");
        }
    };
}(); // GSCheckRequired

