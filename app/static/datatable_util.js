/**
 * Setup data table updates the table_def with duplicating values where the same value is needed as a different key
 * Also does some general configuration for specific typed fields like Date and DateTime
 * Also it loads the select field options from the backend
 * @param {*} table_def
 * @param {*} table_id
 * @param {*} toggle_columns_id
 */
function setup_data_table(table_def, table_id, toggle_columns_id) {
  console.log("Setup data table");

  var promises = [];

  table_def.forEach(function (entry, idx) {
    if (!("name" in entry)) {
      // do not overwrite existing name value (select)
      entry["name"] = entry["data"]; // use same data field for editor and table
    }

    if (!("label" in entry)) {
      entry["label"] = entry["title"];
    }

    // unclear what this is for
    entry["targets"] = [idx];

    // Configure DateTime fields (05.07.2020 15:30)
    if (entry.type == "datetime") {
      entry.format = "D.M.YYYY HH:mm";

      // what the Flask server sends us (Defined in /app/models/config)
      entry.wireFormat = "DD.MM.YYYY HH:mm";

      entry.def = () => new Date();
    }

    // Configure Date fields (05.07.2020)
    if (entry.type == "date") {
      // since date has no wireformat but we need to distinguish if we want to have date only, or date + time
      entry.type = "datetime";
      entry.format = "D.M.YYYY";

      // what the Flask server sends us (Defined in /app/models/config)
      entry.wireFormat = "DD.MM.YYYY";

      entry.def = () => new Date();
    }

    // Configure Upload Fields
    if (entry.type == "upload") {
      switch (entry.name) {
        case "upload_image":
          entry.display = (id) => {
            var image_meta_data = editor.file("data_pool_images", id);

            var table = create_table_of_image_meta_data(image_meta_data);

            return table.innerHTML;
          };
          break;
        case "upload_mask":
          entry.display = (id) => {
            var image_meta_data = editor.file(
              "data_pool_manual_segmentations",
              id
            );

            console.log(image_meta_data);

            var table = create_table_of_image_meta_data(image_meta_data);

            return table.innerHTML;
          };
          break;
        case "upload_auto_mask":
          entry.display = (id) => {
            var image_meta_data = editor.file(
              "data_pool_automatic_segmentations",
              id
            );

            var table = create_table_of_image_meta_data(image_meta_data);

            return table.innerHTML;
          };
          break;
        default:
          console.log(
            "Warning: Upload field " + entry.name + " is not mapped!"
          );
      }
    }

    // Configure Select Fields
    if (entry.type == "select") {
      // Use placeholder, so that no value HAS to be selected
      entry.placeholder = "Select...";
      entry.placeholderDisabled = false;
      entry.placeholderValue = null;

      switch (entry.name) {
        case "modality":
          promises.push(
            $.get("/api/data_pool/project/" + project_id + "/modalities")
              .fail(defaultRESTFail)
              .then((response) => {
                entry.options = response.modalities.map((modality) => ({
                  label: modality.name,
                  value: modality.id,
                }));
                console.log("Loaded " + entry.options.length + " modalities");
              })
          );
          break;
        case "contrast_type":
          promises.push(
            $.get("/api/data_pool/project/" + project_id + "/contrast_types")
              .fail(defaultRESTFail)
              .then((response) => {
                entry.options = response.contrast_types.map(
                  (contrast_type) => ({
                    label: contrast_type.name,
                    value: contrast_type.id,
                  })
                );
                console.log(
                  "Loaded " + entry.options.length + " contrast types"
                );
              })
          );
          break;
        case "split":
          promises.push(
            $.get("/api/data_pool/splitEnum/all")
              .fail(defaultRESTFail)
              .then((response) => {
                entry.options = response.split_enum.map((split) => ({
                  label: split.value,
                  value: split.name,
                }));
                console.log(
                  "Loaded " + entry.options.length + " splitEnum values"
                );
              })
          );
          break;
        case "status":
          promises.push(
            $.get("/api/data_pool/statusEnum/all")
              .fail(defaultRESTFail)
              .then((response) => {
                entry.options = response.status_enum.map((status) => ({
                  label: status.value,
                  value: status.name,
                }));
                console.log(
                  "Loaded " + entry.options.length + " statusEnum values"
                );
              })
          );
          break;
        default:
          console.log("Warning: " + entry.data + " not mapped!");
          break;
      }
    }
  });

  return promises;
}

/**
 * Handles init of create dialog from DataTables Editor
 * @param {*} editor
 */
function handle_initCreate(editor) {
  editor.show(); //Shows all fields

  table_def.forEach((field) => {
    // Only fields with the attribute create(: true) are shown
    if (!field.create) {
      editor.hide(field.name);
    }
  });
}

/**
 * Handles init of update/edit dialog from DataTables Editor
 * @param {*} editor
 * @param {*} e
 * @param {*} node
 * @param {*} data
 */
function handle_initEdit(editor, table_def, e, node, data) {
  editor.show(); //Shows all fields

  // TODO decide, which fields should be hidden

  editor.fields().forEach((field_name) => {
    var field_config = table_def.filter(
      (config) => config.name == field_name
    )[0];

    // setup Editor to preselect the correct option of the DataTable select field
    if (field_config.type == "select") {
      // this solves the issue of data['manual_segmentation.status']
      label = getDeepElementFromObject(field_config.data, data);
      // console.log(field_config.data, label);

      if (label != null && field_config.options != null) {
        // get the option corresponding to the label and select it in the current editor
        var options_index = field_config.options
          .map((o) => o.label)
          .indexOf(label);
        console.log(options_index, "in", field_config.options);

        if (options_index != -1) {
          editor
            .field(field_name)
            .val(field_config.options[options_index].value);
        }
      }
    }
  });
}
/**
 * Shows the small information after uploading an image file and looks like this:
 *
 * Name 21312890.nii.gz
 * ID   301
 *
 * @param {*} meta_data
 */
function create_table_of_image_meta_data(meta_data) {
  console.log(meta_data);

  // for all image types
  var table = document.createElement("table");

  var filename_row = document.createElement("tr");

  var filename_row_title = document.createElement("td");
  filename_row_title.innerHTML = "Name";

  var filename_row_value = document.createElement("td");
  filename_row_value.innerHTML = meta_data.name;

  filename_row.appendChild(filename_row_title);
  filename_row.appendChild(filename_row_value);
  table.appendChild(filename_row);

  var id_row = document.createElement("tr");

  var id_row_title = document.createElement("td");
  id_row_title.innerHTML = "ID";

  var id_row_value = document.createElement("td");
  id_row_value.innerHTML = meta_data.id;

  id_row.appendChild(id_row_title);
  id_row.appendChild(id_row_value);
  table.appendChild(id_row);

  return table;
}

/**
 * Renders a div that contains the messages from manual_segmentation.messages
 */
function renderMessages(messages) {
  console.log(messages);

  var messages_container = document.createElement("div");
  messages_container.style = "min-height: 200px;";
  messages_container.innerHTML = "Messages:";

  // EXAMPLE / DUMMY DATA
  if (messages.length == 0) {
    messages = [
      {
        user: {
          id: 4,
          first_name: "Peter",
          last_name: "Schweiger",
        },
        message: "Hallo, das ist meine Abgabe. Ist das so in Ordnung?",
      },
      {
        user: {
          id: 1,
          first_name: "Admin",
          last_name: "Admin",
        },
        message: "Hallo, nein, das musst du noch mal überarbeiten.",
      },
      {
        user: {
          id: 5,
          first_name: "Franz",
          last_name: "Ferdinand",
        },
        message: "Alles klar, sollte jetzt aber in Ordnung sein!",
      },
    ];
  }

  for (var i in messages) {
    var message_obj = messages[i];
    var message_div = document.createElement("div");
    message_div.className = "message";

    console.log(user_id);

    // display the messages of "others" on the left side (like in other well known messengers)
    if (message_obj.user.id != user_id) {
      message_div.className += " other";
    }

    var sender_label = document.createElement("label");
    sender_label.style = "font-style: italic";
    sender_label.innerHTML =
      message_obj.user.first_name + " " + message_obj.user.last_name;

    // sets the actual message
    var message_content_div = document.createElement("div");
    message_content_div.innerHTML = message_obj.message;

    message_div.appendChild(sender_label);
    message_div.appendChild(message_content_div);

    messages_container.appendChild(message_div);
  }

  return messages_container.outerHTML;
}
