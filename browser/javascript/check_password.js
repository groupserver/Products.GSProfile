// GroupServer Module for checking new passwords.
jQuery.noConflict();
GSCheckPassword = function () {
    /* GroupServer Check Password Module.
    
    */

    // Private variables
    var p1 = null;
    var p2 = null;
    var b = null;
    
    // Private methods
    var check_passwords = function () {
        pswd1 = jQuery(p1).val();
        pswd2 = jQuery(p2).val();
        if ( (pswd1 == pswd2) && (pswd1 != "") ) {
            jQuery(b).attr("disabled","");
        } else {
            jQuery(b).attr("disabled","disabled");
        }
    }
    
    // Public methods and properties
    return {
        init: function (password1, password2, button) {
            p1 = password1;
            p2 = password2;
            b = button;
            
            jQuery(password1).keyup(function(e) {
                check_passwords();
            });
            jQuery(password2).keyup(function(e) {
                check_passwords();
            });
            jQuery(button).attr("disabled","disabled");
        }
    };
}(); // GSDisclosureButton

