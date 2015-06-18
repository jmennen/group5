/**
 * Created by User on 16.06.2015.
 */

window.polling = {};
window.polling.pollingactive = true;
window.polling.pollingurl = false;
window.polling.poll = function () {
    if (window.polling.pollingactive && window.polling.pollingurl) {
        $.get(window.polling.pollingurl, null, function (result) {
            window.polling.badge.text(result.new_notifications);
        });
        setTimeout(window.polling.poll, 10000);
    }
};
window.polling.startPolling = function (url) {
    window.polling.badge = $('.notification_count');
    window.polling.pollingurl = url;
    window.polling.pollingactive = true;
    window.polling.poll();
};
window.polling.stopPolling = function () {
    window.polling.pollingactive = false;
};