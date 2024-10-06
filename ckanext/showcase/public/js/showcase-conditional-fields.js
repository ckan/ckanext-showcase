this.ckan.module('showcase-conditional-fields', function ($) {
    return {
      initialize: function () {
        jQuery.proxyAll(this, /_on/);
        this.el.ready(this._onReady);
      },
  
      _onReady: function () {
        var statusField = $('#field-status');
        var feedback = $('#field-feedback').closest('.control-full');
  
        function toggleFields(status) {
            if (status === 'b' ) feedback.show();
            else feedback.hide();
        }
  
        toggleFields(statusField.val());
  
        // On status change, show/hide fields accordingly
        statusField.change(function () {
          toggleFields($(this).val());
        });
      }
    };
  });