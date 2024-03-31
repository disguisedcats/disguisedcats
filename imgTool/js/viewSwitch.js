export default class ViewSwitcher {
  hideBtn = document.getElementById('hide');
  readBtn = document.getElementById('read');
  textArea = document.getElementById('text');

  navItems = document.querySelectorAll('.nav__item');
  hideNavItem = this.navItems[0];
  readNavItem = this.navItems[1];

  messageArea = document.querySelector('#messageArea');
  textBlock = document.querySelector('.main__textBlock');
  keyBlock = document.querySelector('.main__keyBlock');
  rootImg = document.querySelector('.root__img');
  cryptImgBlock = document.querySelector('.crypt__img');
  cryptImg = this.cryptImgBlock.querySelector('#cover');

  addListeners() {
    this.switchToEncrypt();
    this.hideNavItem.addEventListener('click', this.switchToEncrypt.bind(this));
    this.readNavItem.addEventListener('click', this.switchToDecrypt.bind(this));
  }

  switchToEncrypt() {
    this.readNavItem.classList.remove('nav__item-active');
    this.hideNavItem.classList.add('nav__item-active');

    this.messageArea.style.display = 'none';
    this.readBtn.style.display = 'none';

    this.rootImg.style.display = 'block';
    this.cryptImgBlock.style.display = 'block';
    this.textBlock.style.display = 'block';
    this.hideBtn.style.display = 'inline';

    if (!this.cryptImg.src) {
      document.querySelector('#download').setAttribute('disabled', '');
      document.querySelector('.main').style.alignItems = 'center';
    } else {
      document.querySelector('#download').removeAttribute('disabled');
      document.querySelector('.main').style.alignItems = 'flex-start';
    }

    this.keyBlock.querySelector('.main__title').textContent = 'Приватный ключ:';
  }

  switchToDecrypt() {
    this.hideNavItem.classList.remove('nav__item-active');
    this.readNavItem.classList.add('nav__item-active');

    this.hideBtn.style.display = 'none';
    this.textBlock.style.display = 'none';
    this.rootImg.style.display = 'none';
    this.cryptImgBlock.style.display = 'none';

    this.messageArea.style.display = 'block';
    this.readBtn.style.display = 'inline';

    this.keyBlock.querySelector('.main__title').textContent = 'Публичный ключ:';
  }
}