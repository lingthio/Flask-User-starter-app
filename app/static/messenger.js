function sendMessage(imageObj, message, callback) {
    return $.ajax({
        url: '/data/send_message',
        type: 'GET',
        beforeSend: function (xhr) {

            xhr.setRequestHeader('image_id', imageObj["id"]);
        },
        data: {
            messageText: message
        },
        success: callback,
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert("Something went wrong")
        }
    });
}

function createMessenger(imageObj) {
    /**
     * This function creates a messenger based on imageObj inside of the jQuery object container.
     */
    let messages = imageObj["manual_segmentation"]["messages"];

    // Create html for old messages
    let messengerHTML =
        "<div style='overflow:auto; height: 400px; border: 2px solid #000; border-radius: 15px; margin: 20px'>\n";
    for (let message of messages) {
        messengerHTML +=
            "<div class=\"form-group\">\n" +
            `<label for="${message["id"]}" class="col-sm-2 col-form-label"><span style="color: blue; ">${message["user"]["email"]}</span> ${formatDate(message["date"])}</label>\n` +
            '    <div class="col-sm-10">\n' +
            `        <textarea id="${message["id"]}" class=\"form-control\" disabled>${message["message"]}</textarea>\n` +
            '    </div>\n' +
            "</div>\n";
    }
    messengerHTML += "</div>\n";
    // Append html for new text field
    messengerHTML +=
        '<div class="form-group">\n' +
        '    <label for="newMessageField">New Message</label>\n' +
        '    <div class="col-sm-10">\n' +
        '       <textarea class="form-control" id="newMessageField"></textarea>\n' +
        '    </div>\n' +
        '</div>';

    // Submit button
    messengerHTML += '<button class="btn btn-primary" name="accept-btn" id="send-message-btn">Send</button>';

    // Add submit functionality
    let messenger = $(messengerHTML);
    $(messenger).ready(function () {
        $(this).find('#send-message-btn').click(function () {
            let message = $("#newMessageField").val();
            if (message !== "") {
                sendMessage(imageObj, message, function (data) {
                    // Data contains the new message in correct form if successful
                    messages.push(data);
                    // Clear container and reload messenger with new messenger
                    $(messenger).parent().empty().append(createMessenger(imageObj));
                })
            }
        });
    });


    return messenger

}