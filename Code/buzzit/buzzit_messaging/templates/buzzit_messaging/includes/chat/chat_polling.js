/**
 * Created by User on 22.06.2015.
 */

var chat, poll_func;
function get_one_poll_func(username) {
    // return the poll_func
    return function () {
        var url = "/messaging/chat/" + username + "/poll/json";
        $.get(url, {}, function (d) {
            // d is json data
            if (d && chat.data("username") == d.username && d.new_chat_messages && d.new_chat_messages.length) {
                // d.new_chat_messages : array of new messages for chat
                d.new_chat_messages.forEach(function (html, i) {
                    var new_message = $(html);
                    $('.area').append(new_message);
                    var objDiv = document.getElementsByClassName("area")[0];
                    objDiv.scrollTop = objDiv.scrollHeight;
                });
            }
            if (d && d.chats) {
                for (var username in d.chats) {
                    var shortinfo = d.chats[username];
                    $('#chat_' + username).find('.badge').text(shortinfo.count);
                    $('#chat_' + username).find('i').text(shortinfo.text);
                }
            }
        });
        setTimeout(poll_func, 5000);
    }
}
function start_chat_polling(username) {
    chat = $('#chat_' + username);
    chat.data("username", username);
    poll_func = get_one_poll_func(username);
    poll_func();
}