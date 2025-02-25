window.onload = function() {
    //document.getElementById('file').addEventListener('change', getFileName);
    document.getElementById('submit').addEventListener('click', sendData);
}


async function sendData(data) {
  const form = document.getElementById('form');
  const formData = new FormData(form);
  const file = form.file.files[0];

    try {
    const response = await fetch("/upload", {
      method: "POST",
      // Set the FormData instance as the request body
      body: formData,

    });
    console.log(await response.json());
  } catch (e) {
    console.error(e);
  }
}

