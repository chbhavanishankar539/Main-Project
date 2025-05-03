const uploadElement = document.getElementById("upload");

if (!uploadElement) return;

function dropHandler(e) {
  console.log(e.files);
}

uploadElement.addEventListener("drop", dropHandler);
