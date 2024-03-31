import { crypting, decrypting } from "./crypting.js";

export function handleFileSelect(evt) {
   var original = document.getElementById("original"),
      stego = document.getElementById("stego"),
      img = document.getElementById("img"),
      cover = document.getElementById("cover"),
      message = document.getElementById("message");

   if(!original || !stego) return;

   var filesData = evt.target.files;

   const f = filesData[0];

   if (!f.type.match('image.*')) return;

   var reader = new FileReader();

   // Closure to capture the file information.
   reader.onload = (function(theFile) {
      return function(e) {
         img.src = e.target.result;
         img.title = escape(theFile.name);
         stego.className = "half invisible";
         cover.src = "";
         message.innerHTML="";
         message.parentNode.className="invisible";
         updateCapacity();
      };
   })(f);

   // Read in the image file as a data URL.
   reader.readAsDataURL(f);
}

export function hide() {
  var stego = document.getElementById("stego"),
     img = document.getElementById("img"),
     cover = document.getElementById("cover"),
     message = document.getElementById("message"),
     textarea = document.getElementById("text"),
     download = document.getElementById("download");
  if(img && textarea) {
   crypting(textarea.value).then((bufferArr) => {
      return new Uint8Array(bufferArr);
   }).then((uint8) => {
      return Array.from(uint8).map(byte => byte.toString(16).padStart(2, '0')).join('');
   }).then((res) => {
      cover.src = steg.encode(res, img);
      stego.className = "half main__block crypt__img";
      message.innerHTML = "";
      message.parentNode.className = "main__block invisible";
      download.href = cover.src.replace("image/png", "image/octet-stream");
   });
  }
}

export function read() {
  var img = document.getElementById("img"),
     cover = document.getElementById("cover"),
     message = document.getElementById("message"),
     textarea = document.getElementById("text");
  if(img && textarea) {
   const hexWithoutSpaces = steg.decode(img).replace(/\s/g, '');
   const bytes = new Uint8Array(hexWithoutSpaces.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
   const bufferArrData = bytes.buffer;

   decrypting(bufferArrData).then((res) => {
      console.log(res);
   });
   if(message.innerHTML !== "") {
      message.parentNode.className="";
      textarea.value = message.innerHTML;
      updateCapacity();
   }
  }
}

export function updateCapacity() {
  var img = document.getElementById('img'),
     textarea = document.getElementById('text');
  if(img && text)
     document.getElementById('capacity').innerHTML='('+textarea.value.length + '/' + steg.getHidingCapacity(img) +' символов)';
}