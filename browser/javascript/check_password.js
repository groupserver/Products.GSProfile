// GroupServer Module for checking new passwords.
jQuery.noConflict();
GSCheckPassword = function () {
    /* GroupServer Check Password Module.
    
        Passwords are awkward to get from the user. For security, what the
        user types is not shown, so it is easier for a user to make a slip
        and not notice the error. To overcome this, the user is required
        to type the password again, with the second password checked
        against the first. The idea is that the user will not make the
        same slip twice. This module provides the check for GroupServer
        forms.
        
        FUNCTIONS
          init:   Add the password-checking code to the appropriate 
                  widgets.
    */

    // Private variables
    var p1 = null;
    var p2 = null;
    var b = null;
    var h = null;
    var passwdMatch = true; // This is correct.
    
    // Private methods
    var check_passwords = function () {
        pswd1 = jQuery(p1).val();
        pswd2 = jQuery(p2).val();
        if ( (pswd1 == pswd2) && (pswd1 != "") ) {
            if ( (h != null) && (!passwdMatch) ) {
                jQuery(h).find(".message-error").hide("slow");
            }
            passwdMatch = true;
        } else {
            if ( (h != null) && passwdMatch ) {
                jQuery(h).find(".message-error").show("slow");
            }
            passwdMatch = false;
        }
        return passwdMatch;
    }
    
    // Public methods and properties
    return {
        init: function (password1, password2, button, help) {
            /* Add the password-checking code to the appropriate widgets
              
              ARGUMENTS
                password1:  String of the ID of the first password entry.
                password2:  String of the ID of the second password entry.
                button:     String of the ID of the form-submit button.
                help:       String of the ID of the "passwords do not 
                            match" help. Can be null.
            */
            p1 = password1;
            p2 = password2;
            b = button;
            h = help;
            
            jQuery(b).click(check_passwords);
        }
    };
}(); // GSDisclosureButton

