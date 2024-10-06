ckan.module("showcase-actions", function ($) {
    "use strict";
  
    return {
      options: {
        showcaseId: null,
        ajaxReload: false,
      },
  
      initialize: function () {
        $.proxyAll(this, /_on/);
  
        // Attach event handlers for approve and reject buttons
        this.$(".showcase-actions .approve-showcase").on(
          "click",
          this._onApproveShowcase
        );
        this.$(".showcase-actions .reject-showcase").on(
          "click",
          this._onRejectShowcase
        );
      },
  
      _showConfirmation: function (message, callback) {
        // Set the message in the modal
        $('#confirmation-message').text(message);
        
        // Show the modal
        $('#custom-confirmation-modal').modal('show');
        
        // Set the callback for the confirm button
        $('#confirm-button').off('click').on('click', function () {
          callback();
          $('#custom-confirmation-modal').modal('hide'); // Hide the modal after confirmation
        });
      },
  
      _onApproveShowcase: function (e) {
        var self = this;
        var id = e.currentTarget.dataset.id;
        var message = e.currentTarget.getAttribute("data-module-content");
  
        // Show confirmation dialog
        this._showConfirmation(message, function () {
          self._updateShowcaseStatus(id, 'd');
        });
      },
  
      _onRejectShowcase: function (e) {
        var self = this;
        var id = e.currentTarget.dataset.id;
        var message = e.currentTarget.getAttribute("data-module-content");
  
        // Show confirmation dialog
        this._showConfirmation(message, function () {
          self._updateShowcaseStatus(id, 'c');
        });
      },
  
      _updateShowcaseStatus: function (id, status) {
        var ajaxReload = this.options.ajaxReload;
  
        this.sandbox.client.call(
          "POST",
          "ckanext_showcase_status_update",
          {
            showcase_id: id,
            status: status,
          },
          function () {
            if (ajaxReload) {
              $(document).trigger("showcase:statusChanged");
            } else {
              window.location.reload();
            }
          }
        );
      },
    };
  });
  