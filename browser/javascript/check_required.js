// GroupServer module for checking required form fields.
jQuery.noConflict();
GSCheckRequired = function () {
    /* GroupServer Check Required Form Fields
    
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

