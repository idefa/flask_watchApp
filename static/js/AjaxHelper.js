function AjaxHelper() {
    this.ajax = function(url, type, dataType, data, callback) {
        $.ajax({
            url:url,
            type:type,
            data:data,
            dataType:dataType,
            //processData 指定为 false 告诉 jQuery 不要再对 data 进行处理，
            processData: false,
            //Content-Type：只限于三个值application/x-www-form-urlencoded、multipart/form-data、text/plain
            //contentType: 'application/json; charset=utf-8',
            cache: false,
            crossDomain: true,
            success:callback,
            error: function(xhr, errorType, error) {
                console.log('Ajax request error, errorType: ' + errorType +  ', error: ' + error)
            }
        });
    }
}
//AjaxHelper.prototype.get = function(url, data, callback) {
//    this.ajax(url, 'GET', 'json', data, callback)
//}
AjaxHelper.prototype.post = function(url, data, callback) {
    this.ajax(url, 'POST', 'json', data, callback)
}
//
//AjaxHelper.prototype.put = function(url, data, callback) {
//    this.ajax(url, 'PUT', 'json', data, callback)
//}
//
//AjaxHelper.prototype.delete = function(url, data, callback) {
//    this.ajax(url, 'DELETE', 'json', data, callback)
//}

AjaxHelper.prototype.constructor = AjaxHelper