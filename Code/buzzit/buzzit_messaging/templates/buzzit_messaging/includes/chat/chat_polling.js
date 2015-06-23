/**
 * Created by User on 22.06.2015.
 */

var chat, poll_func;
function get_one_poll_func(sender_id) {
    // return the poll_func
    return function () {
        var url = "/messaging/chat/" + sender_id + "/poll/json";
        $.get(url, {}, function (d) {
            // d is json data
            if (d && chat.data("sender_id") == d.sender_id && d.new_chat_messages && d.new_chat_messages.length) {
                // d.new_chat_messages : array of new messages for chat
                d.new_chat_message.forEach(function (el, i) {
                    var new_message = $('<span>')
                        .addClass("chat_message")
                        .text(el.text)
                        .appendTo(new_message);
                });
            }
        });
        setTimeout(poll_func, 5000);
    }
}
function start_chat_polling(sender_id) {
    chat = $('#chat_' + sender_id);
    poll_func = get_one_poll_func(sender_id);
    poll_func();
}