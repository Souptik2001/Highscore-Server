console.log("Nothing to see here!📜📜");


function copyToClipboard(e){
  var target = e.target;
  console.log(target);

  target.select();
  target.setSelectionRange(0, 99999);
  navigator.clipboard.writeText(target.value);
  alert("Copied To Clipboard!");
}