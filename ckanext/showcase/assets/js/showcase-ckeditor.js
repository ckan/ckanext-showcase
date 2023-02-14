// Enable JavaScript's strict mode. Strict mode catches some common
// programming errors and throws exceptions, prevents some unsafe actions from
// being taken, and disables some confusing and bad JavaScript features.
"use strict";

ckan.module('showcase-ckeditor', function ($) {
  return {
    options: {
        site_url: ""
      },

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
                'horizontalline', 'link', 'blockQuote', 'undo', 'redo',
                '|',
                'imageUpload'
            ]

        config.image = {
            toolbar: [
                'imageTextAlternative',
                '|',
                'imageStyle:alignLeft', 'imageStyle:full', 'imageStyle:alignRight'
            ],
            styles: ['alignLeft', 'full', 'alignRight']
        }

        config.language = 'en'

        config.simpleUpload = {
            uploadUrl: this.options.site_url + 'showcase_upload'
        }

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