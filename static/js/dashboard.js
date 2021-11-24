window.onload = function(){
  all_link_containers = document.getElementsByClassName("link-container");
  console.log(all_link_containers.length);
  for(let i=0; i<all_link_containers.length; i++){
  	  var old_text = all_link_containers[i].value;
      all_link_containers[i].value = document.location.origin + old_text;
  }
};


console.log("Nothing to see here!📜📜");


function copyToClipboard(e){
  var target = (e.target) ? e.target : e.srcElement;
  console.log(target);

  target.select();
  target.setSelectionRange(0, 99999);
  navigator.clipboard.writeText(target.value);
  alert("Copied To Clipboard!");
}


function getCurrentUrl(){
  return document.location.origin;
}