// Enable JavaScript's strict mode. Strict mode catches some common
// programming errors and throws exceptions, prevents some unsafe actions from
// being taken, and disables some confusing and bad JavaScript features.
"use strict";

ckan.module('showcase-ckeditor', function ($) {
  return {
    initialize: function () {
      jQuery.proxyAll(this, /_on/);
      this.el.ready(this._onReady);
    },

    _onReady: function(){
        var config = {};
        config.toolbar = [
                'heading',
                '|',
                'bold', 'italic','underline', 'code',
                '|',
                'outdent', 'indent',
                '|',
                'bulletedList', 'numberedList',
                '|',
                'horizontalline', 'link', 'imageUpload', 'blockQuote', 'undo', 'redo'
            ]

        config.language = 'en'

        ClassicEditor
        .create(
            document.querySelector('#editor'),
            config
            )
        .catch( error => {
            console.error( error.stack );
        } );
    }


  };
});