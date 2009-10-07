// GroupServer module for suggesting a display name (fn) based on the 
//   family and given names
jQuery.noConflict();
GSSuggestFN = function () {
    /* GroupServer Suggest FN
    
    FUNCTIONS
      "init":   Add the callbacks to the entry widgets
    
    */

    // Private variables
    var userModified = false;
    var givenEntry   = null;
    var familyEntry  = null;
    var fnEntry      = null;
    
    // Private methods
    var update_fn = function() {
        var newFn = '';
        if ( !userModified ) {
            firstGivenName = givenEntry.val();
            newFn = firstGivenName + ' ' + familyEntry.val();
            fnEntry.val(newFn);
            fnEntry.change();
        }
    }
    
    // Public methods and properties
    return {
        init: function (given, family, fn) {
            /* Add the suggestion-callbacks to the correct widgets
            
            ARGUMENTS
              given:  String containing the ID of the given-name entry
              family: String containing the ID of the family-name entry
              fn:     String containing the ID of the fn entry
            */
            givenEntry  = jQuery(given);
            familyEntry = jQuery(family);
            fnEntry     = jQuery(fn);
            
            givenEntry.keyup(function(event) {
                update_fn();
            });
            familyEntry.keyup(function(event) {
                update_fn();
            });
            fnEntry.keyup(function(event) {
                if ( event.keyCode != 9 ) {
                    userModified = true;
                }
            });

        }
    };
}(); // GSCheckEmailAddress

