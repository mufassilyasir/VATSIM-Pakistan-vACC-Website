function filesize(elem){
  document.cookie = `size=${elem.files[0].size}; path=/upload/avatar`;
  }