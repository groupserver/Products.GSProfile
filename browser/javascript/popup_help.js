// GroupServer module for popup form-help
jQuery.noConflict();
GSPopupFormHelp = function () {
    /* GroupServer Help Popup for Forms.
    
    Constructor
      "init(f)": Creates popup-help for each widget within the form 
          with the ID "f".
      
    Attributes
      "form": The jQuery form-element.
    
    */

    // Private variables
    var formWidgetClass = 'form-widget'
    var popupHelpClass = 'popup-help';
    
    // Private methods
    var create_popups = function (f) {
        var foo = 1;
        var elements = jQuery(f).find('.'+formWidgetClass);
        elements.each(create_popup);
        elements.children(':input').focus(show_popup).blur(hide_popup);
    }

    var create_popup = function(e) {
        var elem = jQuery(this);
        var helpDiv = elem.prepend(
          '<div class="'+popupHelpClass+'" style="display:none;"/>'
        ).children('.'+popupHelpClass);
        
        var helpTitle = helpDiv.append('<h3>Help</h3>').children('h3');
        helpTitle.text(elem.children('label').text());
        if ( elem.hasClass('required') ) {
            helpTitle.append('<span class="required">(required)</span>');
        }

        var helpText = helpDiv.append('<p/>').children('p');
        helpText.text(elem.children('label').attr('title'));
    }
    
    var show_popup = function (e) {
        var formWidget = jQuery(this).parent('.'+formWidgetClass);
        var helpDiv = formWidget.children('.'+popupHelpClass);
        helpDiv.slideDown('slow');
        return true;
    }
    var hide_popup = function (e) {
        var formWidget = jQuery(this).parent('.'+formWidgetClass);
        var helpDiv = formWidget.children('.'+popupHelpClass);
        helpDiv.slideUp('slow');
        return true;
    }
    
    
    // Public methods and properties
    return {
        init: function (f) {create_popups(f);}
    };
}(); // GSPopupFormHelp

