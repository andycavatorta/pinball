function Thirtybirds(port, event_handler_callback){
    this.websocket_url = "".concat("ws://", document.URL.split("//")[1].split(":")[0], ":", port, "/");
    var event_handler_callback = event_handler_callback
    this.websocket = new WebSocket(this.websocket_url);
    this.websocket.onmessage = function(event){
        var event_data = JSON.parse(event.data)
        console.log(event.data)
        var topic = event_data.topic
        var message = event_data.message
        event_handler_callback(topic, message) 
    }
    this.publish_to_topic = function(_topic_, _message_){
        var message = {topic:_topic_,message:_message_}
        var message_json = JSON.stringify(message)
        this.websocket.send(message_json)
    }
    this.subscribe_to_topic = function(topic){
        this.publish_to_topic("tb.http.subscribe_to_topic", topic)
    }
    this.unsubscribe_from_topic = function(topic){
        this.publish_to_topic("tb.http.unsubscribe_from_topic", topic)
    }
}
function network_event_handler(topic, message){
    console.log(topic, message)
}
var network = new Thirtybirds(6789, network_event_handler)
