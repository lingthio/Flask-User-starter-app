// Most basic table definition that is used by all tables
let generalTable = {
    serverSide: true,
    ajax: {
        url: '',
        data: function (args) {
            return {"args": JSON.stringify(args)};
        }

    },
    columns: [
        {
            className: 'details-control',
            orderable: false,
            data: null,
            render: function (data) {
                return '<button class="btn btn-add row-hide-btn"><i class="fa fa-plus-circle fa-2x"></i></button>';
            }
        },
        {name: 'name', data: 'name'},
        {name: 'patient_name', data: 'patient_name'},
        {name: 'modality', data: 'modality'},
        {name: 'contrast_type', data: 'contrast_type'},
        {name: 'accession_number', data: 'accession_number'},
        {name: 'insert_date', data: 'insert_date', render: formatDate},
        {name: 'last_updated', data: 'last_updated', render: formatDate},
        {name: 'last_message', data: null, render: getLastMessage}
    ],
    columnDefs: [{"className": "dt-center", "targets": "_all"}],
    autoWidth: false
};

function getLastMessage(imageObj) {
    let messages = imageObj["manual_segmentation"]["messages"];
    if (messages.length === 0)
        return "";
    else
        return messages.slice(-1)[0]["message"];
}

function createStatusLabel(caseObject, addResetButton) {
    /**
     * This function constructs the html representation of the status caseObject is in.
     *
     * In case addResetButton == True, an additional button is added to reset the status to new
     */
        // Fetch users of current project
    let status = caseObject["manual_segmentation"]["status"];
    let assignee = caseObject["manual_segmentation"]["assignee"];

    let status_strings = {
        "new": "New",
        "assigned": "Assigned",
        "open_for_segmentation": "Open For Segmentation",
        "rejected": "Rejected",
        "valid": "Valid",
        "submitted": "Submitted"
    };
    let statusString = "";
    if (assignee != null && status === "assigned") {
        statusString = "Assigned to " + assignee["first_name"] + " " + assignee["last_name"]
    } else {
        statusString = status_strings[status];
    }
    let containerHTML = "<div><div><label>" + statusString + "</label></div></div>";
    let container = $(containerHTML);
    if (addResetButton) {

        let buttonHTML = '<div><button class="btn btn-danger btn-sm reset-status-btn">Reset</button>\n';
        let button = $(buttonHTML);
        $(container).append(button)
    }
    return container.html();
}


function createUserAssignSelect(caseObject) {
    /**
     * This function creates the html representation of a dropdown menu.
     */
    let table = $('#datatable').DataTable();
    let projectUsers = table.ajax.json()["project"]["users"];

    let sel = "<select class='userAssign custom-select'>";
    if (caseObject["manual_segmentation"]["assignee_id"] != null) {
        sel += "<option>Not Assigned</option>";
    } else {
        sel += "<option selected>Not Assigned</option>";
    }
    if (caseObject["manual_segmentation"]["status"] === "open_for_segmentation") {
        sel += "<option selected>Open for Segmentation</option>";
    } else {
        sel += "<option>Open for Segmentation</option>";
    }

    for (let user of projectUsers) {
        user = user[0];
        let user_representation = user["first_name"] + " " + user["last_name"] + " (" + user["email"] + ")";
        if (user["id"] === caseObject["manual_segmentation"]["assignee_id"]) {
            sel += "<option selected value = '" + user["id"] + "' >" + user_representation + "</option>";
        } else {
            sel += "<option value = '" + user["id"] + "' >" + user_representation + "</option>";
        }
    }
    sel += "</select>";
    return sel;
}

function createSplitAssignSelect(caseObject) {
    /**
     *  Function to create drop down menu for split assignment
     */
        // Fetch users of current project
    let options = ["train", "test", "validation"];

    // Build select
    let sel = "<select class='splitAssign custom-select'><option value=null>Assign</option>";

    for (let option of options) {
        if (option === caseObject["split"]) {
            sel += "<option selected >" + option + "</option>";
        } else {
            sel += "<option >" + option + "</option>";
        }
    }
    sel += "</select>";
    return sel;
}

function formatHiddenRowInformation(imageObj) {

    // Container for content
    let containerHTML = '<div class="parent-container d-flex">\n' +
        '    <div class="container">\n' +
        '        <div class="row">\n' +
        '            <div class="col">\n' +
        '               <h2>Attributes</h2>' +
        '               <div id="formContainer"></div>' +
        '            </div>\n' +
        '        </div>\n' +
        '    </div>\n' +
        '\n' +
        '    <div class="container">\n' +
        '        <div class="row">\n' +
        '            <div class="col">\n' +
        '               <h2>Messages</h2>\n' +
        '               <div id="messengerContainer"></div>' +
        '            </div>\n' +
        '        </div>\n' +
        '    </div>\n' +
        '</div>';
    let container = $(containerHTML);
    let form;
    if (role === "admin")
        form = createAttributesForm(imageObj, true, true);
    else
        form = createAttributesForm(imageObj, false, false);
    let messenger = createMessenger(imageObj);

    // Add content
    $(container).find("#formContainer").append(form);
    $(container).find("#messengerContainer").append(messenger);

    return container;
}

function createAttributesForm(imageObj, isEditable, drawSubmitButton){
    let disabled = "";
    if (!isEditable)
        disabled = "disabled";

    let formHTML = "<div>\n";
    // Create selects for modality and contrast type
    let table = $('#datatable').DataTable();
    let projectObj = table.ajax.json()["project"];
    let modalities = projectObj["modalities"];
    let contrastTypes = projectObj["contrast_types"];
    let activeModality = imageObj["modality"];
    let activeContrastType = imageObj["contrast_type"];
    formHTML +=
            '<div class="form-group-sm row">\n' +
            '    <label for="modality" class="col-sm-4 col-form-label">Modality</label>\n' +
            '    <div class="col-sm-6">\n';
    formHTML += buildSelect("modality", modalities, activeModality, isEditable);
    formHTML +=
            '    </div>\n' +
            '  </div>';
    formHTML +=
            '<div class="form-group-sm row">\n' +
            '    <label for="contrast_type" class="col-sm-4 col-form-label">Contrast Type</label>\n' +
            '    <div class="col-sm-6">\n';
    formHTML += buildSelect("contrast_type", contrastTypes, activeContrastType, isEditable);
    formHTML +=
            '    </div>\n' +
            '  </div>';


    // Create form for all relevant editable fields
    let relevantFields = {
        accession_number: "Accession Number",
        body_region: "Body Region",
        patient_name: "Patiend Name",
        patient_dob: "Birthday",
        institution: "Institution",
        study_date: "Study Date",
        study_name: "Study Name",
        study_number: "Study Number",
        study_description: "Study Description",
        study_instance_uid: "Study Instance UID",
        series_description: "Series Description",
        series_instance_uid: "Series Instance UID",
        custom_1: "Custom Field 1",
        custom_2: "Custom Field 2",
        custom_3: "Custom Field 3",
    };

    // Form for attributes
    for (let [id, descr] of Object.entries(relevantFields)) {
        let dataEntry;
        if (id in imageObj)
            dataEntry = imageObj[id];
        else
            dataEntry = "";
        formHTML +=
            '<div class="form-group-sm row">\n' +
            '    <label for="' + id + '" class="col-sm-4 col-form-label">' + descr + ':</label>\n' +
            '    <div class="col-sm-6">\n' +
            '      <input class="form-control" id="' + id + '" value="' + dataEntry + '"' + disabled + '>\n' +
            '    </div>\n' +
            '  </div>';
    }

    if (drawSubmitButton) {
        formHTML += "<button class='btn btn-success' id='submit-attribute-form-btn'>Submit</button>";
    }
    formHTML += "</div>";

    let form = $(formHTML);

    // Register data function to extract form data
    $(form).data("formData", function () {
        let result = {};
        for (let [id, descr] of Object.entries(relevantFields)) {
            result[id] = $("#" + id).val();
        }
        return result;
    });

    // If required, add submit button functionality
    $(form).ready(function () {
        $("#submit-attribute-form-btn").click(function () {
            // Contrast type and modality
            let selectedContrastType = $( "#contrast_type option:selected" ).text();
            let selectedModadality = $( "#modality option:selected" ).text();
            if (selectedContrastType !== "Not Assigned")
                imageObj["contrast_type"] = selectedContrastType;
            if (selectedModadality !== "Not Assigned")
                imageObj["modality"] = selectedModadality;

            // Standard fields
            for (let [id, descr] of Object.entries(relevantFields)) {
                imageObj[id] = $("#" + id).val();

            }
            sendRowUpdateToServer(imageObj);
            location.reload();
        });
    });
    return form;
}


function registerDatatableElements() {
    /**
     * This function registers all interactive datatable elements and adds the according functionality to them.
     *
     * It is not a problem if the current window does not contain some of these elements, since jQuery would
     * just ignore non existing elements anyway. This way it is just more convenient.
     */
    // Add event listener for opening and closing rows
    $('.row-hide-btn').click(function () {
        let table = $('#datatable').DataTable();
        let tr = $(this).closest('tr');
        let row = table.row(tr);

        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
            $(this).html("<i class=\"fa fa-plus-circle fa-2x\"></i>")
        } else {
            // Open this row but hide all others first
            table.rows().eq(0).each(function (idx) {
                let row = table.row(idx);
                if (row.child.isShown()) {
                    row.child.hide();
                    $(".row-hide-btn").html("<i class=\"fa fa-plus-circle fa-2x\"></i>");
                }
            });
            row.child(formatHiddenRowInformation(row.data())).show();
            $(this).html("<i class=\"fa fa-minus-circle fa-2x\"></i>")
        }
    });


    // User assignment
    $('.userAssign').change(function () {
        // Get row object of row this select resides in
        let table = $('#datatable').DataTable();
        let caseObject = table.row($(this).closest('tr')).data();

        // Change assignee and status
        let value = $(this).val();
        let text = this.options[this.selectedIndex].text;

        if (text === "Not Assigned") {
            caseObject["manual_segmentation"]["assignee_id"] = null;
            caseObject["manual_segmentation"]["status"] = "new";
        } else if (text === "Open for Segmentation") {
            caseObject["manual_segmentation"]["assignee_id"] = null;
            caseObject["manual_segmentation"]["status"] = "open_for_segmentation";
        } else {
            caseObject["manual_segmentation"]["assignee_id"] = parseInt(value);
            caseObject["manual_segmentation"]["assigned_date"] = new Date(Date.now()).toUTCString();
            caseObject["manual_segmentation"]["status"] = "assigned";
        }

        sendRowUpdateToServer(caseObject);
        table.draw(false);
    });

    // Split assignment
    $('.splitAssign').change(function () {
        // Get row object of row this select resides in
        let table = $('#datatable').DataTable();
        let caseObject = table.row($(this).closest('tr')).data();

        // Change assignee
        let value = $(this).val();
        let option = $(this).find('option:selected').text();

        if (value === "null") {
            caseObject["split"] = null;
        } else {
            caseObject["split"] = option;
        }

        // Send change to server
        sendRowUpdateToServer(caseObject);
    });

    // Upload new segmentations
    $('.segmentationUploadButton').click(function () {
        let table = $('#datatable').DataTable();
        let caseObject = table.row($(this).closest('tr')).data();
        showSegmentationUploadModal(caseObject);
    });

    // Download data
    $('.dataDownloadButton').click(function () {
        let table = $('#datatable').DataTable();
        let caseObject = table.row($(this).closest('tr')).data();

        showDownloadModal(caseObject);
    });

    // Review dialog
    $('.reviewButton').click(function () {
        // Retrieve the data belonging to this specific row
        let table = $('#datatable').DataTable();
        let imageObj = table.row($(this).closest('tr')).data();

        showReviewModal(imageObj)
    });

    // Reset status Button
    $('.reset-status-btn').click(function () {
        // Retrieve the data belonging to this specific row
        let table = $('#datatable').DataTable();
        let imageObj = table.row($(this).closest('tr')).data();

        imageObj["manual_segmentation"]["status"] = "new";
        sendRowUpdateToServer(imageObj);
        location.reload();
    });

    // Delete button
    $('.rowDeleteButton').click(function () {
        // Retrieve the data belonging to this specific row
        let table = $('#datatable').DataTable();
        let imageObj = table.row($(this).closest('tr')).data();
        let imageID = imageObj["id"];
        console.log(imageID);
        $.ajax({
            type: 'POST',
            url: '/data/delete_image',
            success: function (data) {
                console.log("success");
            },
            error: function (e) {
                console.log("Fuuuck");
            },
            data: JSON.stringify(imageObj),
            dataType: "json",
            contentType: "application/json"
        });
        location.reload();
    });
}