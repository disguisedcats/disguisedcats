"use strict";

import * as actions from './actions.js';
import ViewSwitcher from './viewSwitch.js';

window.onload = function() {
  const hideBtn = document.getElementById('hide');
  const readBtn = document.getElementById('read');
  const textArea = document.getElementById('text');

  document.getElementById('file').addEventListener('change', actions.handleFileSelect, false);
  hideBtn.addEventListener('click', () => {
    actions.hide();
    document.querySelector('#download').removeAttribute('disabled');
    document.querySelector('.main').style.alignItems = 'flex-start';
  }, false);
  readBtn.addEventListener('click', actions.read, false);
  textArea.addEventListener('keyup', actions.updateCapacity, false);

  actions.hide();
  actions.updateCapacity();

  new ViewSwitcher().addListeners();
};