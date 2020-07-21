function downloadCase(rowObject) {
  console.log("mist");
  $.ajax({
    url: "/project/" + project_id + "/case/" + rowObject["id"] + "/download",
    type: "GET",
    xhrFields: {
      responseType: "blob",
    },
    success: function (data) {
      console.log("bla");
      let a = document.createElement("a");
      let url = window.URL.createObjectURL(data);
      a.href = url;
      a.download = "data.zip";
      document.body.append(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    },
    error: function (XMLHttpRequest, textStatus, errorThrown) {
      console.log("lol");
      location.reload();
    },
  });
}

// Function to make call to API after row has been updated
function _sendRowUpdateToServer(rowObject, server_url) {
  $.ajax({
    type: "POST",
    url: server_url.replace("%ID%", rowObject["id"]),

    data: JSON.stringify(rowObject),
    success: function (data) {
      console.log("success");
    },
    error: function (e) {
      console.log(e);
    },

    dataType: "json",
    contentType: "application/json",
  });
}

function formatDate(dateString) {
  let date = new Date(dateString);
  let day = date.getDate();
  let month = date.getMonth() + 1;
  let year = date.getFullYear();

  let hours = date.getHours();
  let minutes = date.getMinutes();

  return `${day}.${month}.${year} - ${hours}:${minutes}`;
}

function buildSelect(id, options, activeOption, isEditable) {
  let disabled = "";
  if (!isEditable) disabled = "disabled";

  let select = '<select class="custom-select" id="' + id + '"' + disabled + ">";
  if (activeOption == null)
    select += "<option selected>Not Assigned</option>\n";
  else select += "<option>Not Assigned</option>\n";

  for (let option of options) {
    if (option === activeOption) {
      select += "<option selected >" + option + "</option>\n";
    } else {
      select += "<option >" + option + "</option>\n";
    }
  }
  select += "</select>\n";
  return select;
}

// From here on: Author: jkriegel

/**
 * Default REST Fail is used to AJAX calls to display errors in console
 * @param {*} request
 * @param {*} status
 * @param {*} errorThrown
 */
function defaultRESTFail(request, status, errorThrown) {
  console.log(
    this.url + " responded with " + request.status,
    errorThrown,
    "\n",
    request.responseText
  );
}

/*
    Reducing keys like manual_segmentation.status and the object data { manual_segmentation: { status: "abc" }}
    to the value of status

    field_config.data = 'manual_segmentation.status'
    data = { manual_segmentation: { status: "abc" }}
    afterwards: start[1] = "abc"
    */
function getDeepElementFromObject(deepKey, object) {
  start = [deepKey.split("."), object];

  while (start[0].length > 0) {
    start = [start[0].splice(1, start[0].length - 1), start[1][start[0]]];
  }

  return start[1];
}
