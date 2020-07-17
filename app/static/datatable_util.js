function setup_data_table(table_def, table_id, toggle_columns_id) {
  var promises = [];

  table_def.forEach(function (entry, idx) {
    if (!("name" in entry)) {
      // do not overwrite existing name value (select)
      entry["name"] = entry["data"]; // use same data field for editor and table
    }

    if (!("label" in entry)) {
      entry["label"] = entry["title"];
    }

    // date + timestamp needed
    if (entry.type == "datetime") {
      entry.format = "D.M.YYYY HH:mm";

      // what the Flask server sends us (Defined in /app/models/config)
      entry.wireFormat = "DD.MM.YYYY HH:mm";

      entry.def = () => new Date();
    }

    // only a date is needed
    if (entry.type == "date") {
      // since date has no wireformat but we need to distinguish if we want to have date only, or date + time
      entry.type = "datetime";
      entry.format = "D.M.YYYY";
      // what the Flask server sends us (Defined in /app/models/config)
      entry.wireFormat = "DD.MM.YYYY";

      entry.def = () => new Date();
    }

    entry["targets"] = [idx];

    // Add data to fields for create/update commands
    if (entry.type == "select") {
      // console.log("Select entry", entry);

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

    // // add data columns to table
    // $(table_id)
    //   .find("tr")
    //   .append("<th>" + entry["title"] + "</th>");
  });

  return promises;
}
