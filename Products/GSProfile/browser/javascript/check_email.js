// GroupServer module for checking email addresses
jQuery.noConflict();
GSCheckEmailAddress = function () {
    /* GroupServer Check Email Address
    
    xhtml markup
      Most of the markup is needed for the optional help-text, which is 
      shown when the user types in the address of a webmail provider. There
      should be one block, for the main text, that contains entries for
      each of the webmail providers.
        
        <p id="webmailHelp">
          This is some help for Webmail.
          <span id="gmail">
            This is some specific help for GMail.
          </span>
          <span id="yahoo">
            This is some specific help for Yahoo!
          </span>
          <span id="hotmail">
            This is some specific help for MSN Hotmail.
          </span>
        </p>
        
      The identifiers for each of the webmail providers should be single
      words. They will be used to form the expression that checks the email
      address that the user types in.
    
    FUNCTIONS
      "init":   Add the code to check the email-addresses to the 
                entry widget.
    
    */

    // Private variables
    var email = null;
    var button = null;
    var webmailHelp = null;
    var help = null;
    var webmail = null;
    
    // Private methods
    var check = function () {
        var addr = jQuery(email).val().toLowerCase();
        return check_address(addr);
    }
    
    var check_help = function () {
        var addr = jQuery(email).val().toLowerCase();
        if ( webmailHelp != null ) {
            check_for_webmail(addr);
        }
    }
    
    var check_for_webmail = function(addr) {
        var i = 0;
        var m = '';
        var elemId = '';
        var helpShown = ( jQuery(webmailHelp).css('display') != 'none' );
        var helpOrigShown = helpShown;
        
        for ( i in webmail ) {
            m = '@' + webmail[i] + '.';
            elemId = '#' + webmail[i];
            if ( addr.match(m) ) {
                if ( !helpShown ) {
                    helpShown = true;
                    jQuery(webmailHelp).fadeIn("slow");
                }
                jQuery(elemId).fadeIn("slow");
                break;
            } else {
                jQuery(elemId).fadeOut("slow");
                helpShown = false;
            }
        }
        if (!helpShown && helpOrigShown ) {
            jQuery(webmailHelp).fadeOut("slow");
        }
    }
    
    var check_address = function (addr) {
        // Check the email address  to see if it is valid.
        // --=mpj17=-- It would be good if we could get the following
        //    regular expression from the interface module.
        var retval = false;
        regexp = /[a-zA-Z0-9\._%-]+@([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,4}/;
        if ( regexp.test(addr) ) {
            // Good address
            retval = true;
            jQuery(help).find(".message-error").hide("slow");
        } else {
            // Bad address
            retval = false;
            jQuery(help).find(".message-error").show("slow");
        }
        return retval;
    }
    
    // Public methods and properties
    return {
        init: function (e, b, wh, w, h) {
            /* Add the address-checking code to the correct widgets
            
            ARGUMENTS
              e:  String containing the ID of the email-entry widget
              b:  String containing the ID of the submit button for the 
                  form
              h:  String containing the ID of the help-text for the entry.
                  Can be "null".
              w:  Dictionary of the webmail services that are supported by
                  the help-text, as "ID": null pairs. Can be "null".
            */
            email = e;
            button = b;
            webmailHelp = wh;
            webmail = w;
            help = h;
            
            emailEntry = jQuery(e);
            
            emailEntry.keyup(function(event) {
                check_help();
            });
            jQuery(button).click(check);
        }
    };
}(); // GSCheckEmailAddress

