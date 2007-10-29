// GroupServer module for checking email addresses
jQuery.noConflict();
GSCheckEmailAddress = function () {
    /* GroupServer Check Email Address
    
    */

    // Private variables
    var email = null;
    var button = null;
    var help = null;
    var webmail = null;
    
    // Private methods
    var check = function () {
        var addr = jQuery(email).val().toLowerCase();
        check_for_webmail(addr);
        check_address(addr);
    }
    
    var check_for_webmail = function(addr) {
        var i = 0;
        var m = '';
        var elemId = '';
        var helpShown = ( jQuery(help).css('display') != 'none' );
        var helpOrigShown = helpShown;
        
        for ( i in webmail ) {
            m = '@' + webmail[i] + '.';
            elemId = '#' + webmail[i];
            if ( addr.match(m) ) {
                if ( !helpShown ) {
                    helpShown = true;
                    jQuery(help).fadeIn("slow");
                }
                jQuery(elemId).fadeIn("slow");
                break;
            } else {
                jQuery(elemId).fadeOut("slow");
                helpShown = false;
            }
        }
        if (!helpShown && helpOrigShown ) {
            jQuery(help).fadeOut("slow");
        }
    }
    
    var check_address = function (addr) {
        // Check the email address  to see if it is valid.
        // --=mpj17=-- It would be good if we could get the following
        //    regular expression from the interface module.
        regexp = /[a-zA-Z0-9\._%-]+@([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,4}/;
        elem = jQuery(button)
        if ( regexp.test(addr) ) {
            elem.attr("disabled",""); //Enable the element
        } else {
            elem.attr("disabled","disabled"); //Disable the element
        }
    }
    
    // Public methods and properties
    return {
        init: function (e, b, h, w) {
            email = e;
            button = b;
            help = h;
            webmail = w;
            
            emailEntry = jQuery(e);
            
            emailEntry.keyup(function(event) {
                check();
            });
            
            jQuery(b).attr("disabled","disabled");
        }
    };
}(); // GSCheckEmailAddress

