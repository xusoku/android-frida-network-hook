// OkHttp Hook
Java.perform(function() {
    var HttpUrl = Java.use('okhttp3.HttpUrl');
    var RequestBody = Java.use('okhttp3.RequestBody');
    var ResponseBody = Java.use('okhttp3.ResponseBody');
    var RealCall = Java.use('okhttp3.RealCall');
    
    RealCall.execute.implementation = function() {
        var request = this.originalRequest;
        var url = request.url().toString();
        
        console.log('[OKHTTP] ' + request.method() + ' ' + url);
        
        var result = this.execute();
        
        send({
            type: 'http_request',
            url: url,
            method: request.method(),
            library: 'OkHttp',
            response_code: result.code()
        });
        
        return result;
    };
});

// HttpURLConnection Hook
Java.perform(function() {
    var HttpURLConnection = Java.use('java.net.HttpURLConnection');
    
    HttpURLConnection.connect.implementation = function() {
        var url = this.getURL().toString();
        var method = this.getRequestMethod();
        
        console.log('[HTTP] ' + method + ' ' + url);
        
        var result = this.connect();
        
        send({
            type: 'http_request',
            url: url,
            method: method,
            library: 'HttpURLConnection'
        });
        
        return result;
    };
});