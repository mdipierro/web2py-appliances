/**
 * @license Copyright (c) 2003-2016, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or http://ckeditor.com/license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here. For example:
	// config.language = 'fr';
  config.height = '25em';
  config.toolbar = [
      ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'],
      ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo'],
      ['Link', 'Unlink', 'Anchor'],
      ['Maximize', 'ShowBlocks', '-', 'Source'],
      ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']
  ];
  config.skin = 'bootstrapck';
  config.htmlEncodeOutput = false;
  config.entities = false;
  /*toolbar: [
      {name: 'clipboard', items: ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
      {name: 'editing', items: ['Find', 'Replace', '-', 'SelectAll', '-', 'SpellChecker', 'Scayt']},
      {name: 'links', items: ['Link', 'Unlink', 'Anchor']},
      {name: 'insert', items: ['Image', 'Flash', 'Table', 'SpecialChar']},
      {name: 'tools', items: ['Maximize', 'ShowBlocks', '-', 'Source']},
      '/',
      {name: 'styles', items: ['Format', 'Font', 'FontSize']},
      {name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat']},
      {name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
  ],*/
};
