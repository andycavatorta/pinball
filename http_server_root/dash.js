var SVG_NS ="http://www.w3.org/2000/svg";
var canvas = null;
var background_rectangle = null;

var websocket;
var interface = {};
const block_grid_x = [50,250,450,650,850,1050,1250,1450,1650,1850,2050,2250,2450,2650,2850,3050,3250,3450,3650]
const block_grid_y = [20,70,150,280,350,480,550,650,750,850,950,1050,1150,1250,1350,1450,1550,1650,1750,1850,2000]

hostmap = {}

// ------------------- utils -------------------

function setAttributes(element, attributes_o){
  for ( var key in attributes_o) {
    if (attributes_o.hasOwnProperty(key)) {
      element.setAttribute(key,attributes_o[key]);
    }
  }
}

function degrees_to_radians(radians){
  return radians * Math.PI / 180;
}

function format_date(date_string){
  var epoch_ms = Date.parse(date_string);
  var dt = new Date(epoch_ms);
  var year = dt.getFullYear();
  var month = dt.getMonth() + 1;
  var date = dt.getDate() +1;
  var hours = dt.getHours();
  var minutes = dt.getMinutes();
  var seconds = dt.getSeconds();
  return year+":"+month+":"+date+" "+hours+":"+minutes+":"+seconds;
}


function format_df(df_a){
  console.log(df_a)
  df_1 = parseInt(df_a[0]);
  df_2 = parseInt(df_a[1]);
  df_1 = df_1 / 1000000000;
  df_2 = df_2 / 1000000000;
  return df_1.toFixed(2)+"/"+df_2.toFixed(2)+"GB"
}

function makeColor(num, den, error) { // receive numerator, denominator, error of interval
  error = Math.abs(error);
  var hex_a = ["00","11","22","33","44","55","66","77","88","99","aa","bb","cc","dd","ee","ff","ff"];
  var red_str = "00";
  var green_str = hex_a[num];
  var blue_str = hex_a[den];
  var color_str = "#" + red_str + green_str + blue_str;
  return color_str;
}

/* ========== N E T W O R K  ========== */



function websocket_connect() {
    console.log("connecting to wesockets")
    try {
        //console.log("readyState=",websocket.readyState)
        url = "ws://" + location.hostname + ":8001/"
        websocket = new WebSocket(url);
        websocket.onopen = function (evt) { websocket_open(evt) };
        websocket.onclose = function () { websocket_close() };
        websocket.onmessage = function (evt) { websocket_message_handler(evt) };
        websocket.onerror = function (evt) { websocket_error_handler(evt) };
    }
    catch (e) {
        console.log(e)
        console.log("connection failed")
    }
}

function websocket_send(evt) {
    websocket.send("Sample data ")
    console.log(evt)
}
function websocket_open(evt) {
    console.log("send test websocket message")
    try {
        websocket.send("Sending test message from dashboard client")

    } catch (e) {
        console.log(e)
    }

    window.clearInterval(timers.retry_connection)
    timers.retry_connection = false;
    console.log(evt)
}
function websocket_close() {
    if (timers.retry_connection == false) {
        //timers.retry_connection = window.setInterval(try_to_connect, 1000);
    }
    // console.log("closed")
}

function sendTrigger(command) {
    console.log("Sending command ", command)
    websocket.send(command)
}

function websocket_message_handler(evt) {
    var topic_data_origin = JSON.parse(evt.data);
    console.log(topic_data_origin)
    var topic = topic_data_origin[0];
    var message = eval(topic_data_origin[1]);
    var origin = topic_data_origin[2];
    switch (topic) {
      case "deadman":
        break;
      case "event_button_comienza":
        break;
      case "event_button_derecha":
        break;
      case "event_button_dinero":
        break;
      case "event_button_izquierda":
        break;
      case "event_button_trueque":
        break;
      case "event_carousel_ball_detected":
        break;
      case "event_carousel_error":
        break;
      case "event_destination_reached":
        var motor_name = message[0];
        var reached = message[1];
        var position = message[2];
        var disparity = message[3];
        var lookup = {
          carousel_1:"amt_1",
          carousel_2:"amt_2",
          carousel_3:"amt_3",
          carousel_4:"amt_4",
          carousel_5:"amt_5",
          carousel_center:"amt_6",
        }
        hostmap[origin][lookup[motor_name]].set_value("θ relative", position);
        hostmap[origin][lookup[motor_name]].set_value("discrepancy", disparity);
        if (reached){
          hostmap[origin][motor_name].set_value("status", "finished");
          hostmap[origin][motor_name].background_rectangle.setAttribute("class","theme_present");
        }else{
          hostmap[origin][motor_name].set_value("status", "started");
          hostmap[origin][motor_name].background_rectangle.setAttribute("class","theme_nominal");
        }
        break;
      case "event_destination_stalled":
        var motor_name = message[0];
        var stalled = message[1];
        var position = message[2];
        var disparity = message[3];
        var lookup = {
          carousel_1:"amt_1",
          carousel_2:"amt_2",
          carousel_3:"amt_3",
          carousel_4:"amt_4",
          carousel_5:"amt_5",
          carousel_center:"amt_6",
        }
        hostmap[origin][lookup[motor_name]].set_value("θ relative", position);
        hostmap[origin][lookup[motor_name]].set_value("discrepancy", disparity);
        if (stalled){
          hostmap[origin][motor_name].set_value("stall", stalled);
          hostmap[origin][motor_name].background_rectangle.setAttribute("class","theme_fault");
        }
        break;
      case "event_destination_timeout":
        var motor_name = message[0];
        var timeout = message[1];
        var position = message[2];
        var disparity = message[3];
        var lookup = {
          carousel_1:"amt_1",
          carousel_2:"amt_2",
          carousel_3:"amt_3",
          carousel_4:"amt_4",
          carousel_5:"amt_5",
          carousel_center:"amt_6",
        }
        hostmap[origin][lookup[motor_name]].set_value("θ relative", position);
        hostmap[origin][lookup[motor_name]].set_value("discrepancy", disparity);
        if (timeout){
          hostmap[origin][motor_name].set_value("status", "timeout");
          hostmap[origin][motor_name].background_rectangle.setAttribute("class","theme_fault");
        }
        break;
      case "event_left_stack_ball_present":
        break;
      case "event_left_stack_motion_detected":
        break;
      case "event_pop_left":
        break;
      case "event_pop_middle":
        break;
      case "event_pop_right":
        break;
      case "event_right_stack_ball_present":
        break;
      case "event_right_stack_motion_detected":
        break;
      case "event_roll_inner_left":
        break;
      case "event_roll_inner_right":
        break;
      case "event_roll_outer_left":
        break;
      case "event_roll_outer_right":
        break;
      case "event_slingshot_left":
        break;
      case "event_slingshot_right":
        break;
      case "event_spinner":
        break;
      case "event_trough_sensor":
        break;
      case "request_current_sensor_nominal":
        break;
      case "response_amt203_absolute_position":
        hostmap[origin].amt_1.set_value("θ absolute", message[0]);
        hostmap[origin].amt_2.set_value("θ absolute", message[1]);
        hostmap[origin].amt_3.set_value("θ absolute", message[2]);
        hostmap[origin].amt_4.set_value("θ absolute", message[3]);
        hostmap[origin].amt_5.set_value("θ absolute", message[4]);
        hostmap[origin].amt_6.set_value("θ absolute", message[5]);
        break;
      case "response_amt203_present":
        if (message[0]){
          hostmap[origin].amt_1.background_rectangle.setAttribute("class","theme_present");
        }else{
          hostmap[origin].amt_1.background_rectangle.setAttribute("class","theme_absent");
        }
        if (message[1]){
          hostmap[origin].amt_2.background_rectangle.setAttribute("class","theme_present");
        }else{
          hostmap[origin].amt_2.background_rectangle.setAttribute("class","theme_absent");
        }
        if (message[2]){
          hostmap[origin].amt_3.background_rectangle.setAttribute("class","theme_present");
        }else{
          hostmap[origin].amt_3.background_rectangle.setAttribute("class","theme_absent");
        }
        if (message[3]){
          hostmap[origin].amt_4.background_rectangle.setAttribute("class","theme_present");
        }else{
          hostmap[origin].amt_4.background_rectangle.setAttribute("class","theme_absent");
        }
        if (message[4]){
          hostmap[origin].amt_5.background_rectangle.setAttribute("class","theme_present");
        }else{
          hostmap[origin].amt_5.background_rectangle.setAttribute("class","theme_absent");
        }
        if (message[5]){
          hostmap[origin].amt_6.background_rectangle.setAttribute("class","theme_present");
        }else{
          hostmap[origin].amt_6.background_rectangle.setAttribute("class","theme_absent");
        }
        break;
      case "response_amt203_zeroed":
        if (message[0]){
          hostmap[origin].amt_1.background_rectangle.setAttribute("class","theme_nominal");
        }else{
          hostmap[origin].amt_1.background_rectangle.setAttribute("class","theme_fault");
        }
        if (message[1]){
          hostmap[origin].amt_2.background_rectangle.setAttribute("class","theme_nominal");
        }else{
          hostmap[origin].amt_2.background_rectangle.setAttribute("class","theme_fault");
        }
        if (message[2]){
          hostmap[origin].amt_3.background_rectangle.setAttribute("class","theme_nominal");
        }else{
          hostmap[origin].amt_3.background_rectangle.setAttribute("class","theme_fault");
        }
        if (message[3]){
          hostmap[origin].amt_4.background_rectangle.setAttribute("class","theme_nominal");
        }else{
          hostmap[origin].amt_4.background_rectangle.setAttribute("class","theme_fault");
        }
        if (message[4]){
          hostmap[origin].amt_5.background_rectangle.setAttribute("class","theme_nominal");
        }else{
          hostmap[origin].amt_5.background_rectangle.setAttribute("class","theme_fault");
        }
        if (message[5]){
          hostmap[origin].amt_6.background_rectangle.setAttribute("class","theme_nominal");
        }else{
          hostmap[origin].amt_6.background_rectangle.setAttribute("class","theme_fault");
        }
        break;
      case "response_carousel_ball_detected":
        for (var [fruit_name,ball_presence] in Object.entries(message)){
          interface.carousel_panel.set_ball_presence(origin, fruit_name, ball_presence)
        }
        break;
      case "response_computer_details":
          hostmap[origin]["rpi"].set_value("df", format_df(message["df"]))
          hostmap[origin]["rpi"].set_value("temp", message["cpu_temp"])
          hostmap[origin]["rpi"].set_value("pin git", format_date(message["pinball_git_timestamp"]))
          hostmap[origin]["rpi"].set_value("tb git", format_date(message["tb_git_timestamp"]))
        break;
      case "response_current_sensor_nominal":
        break;
      case "response_current_sensor_present":
        break;
      case "response_current_sensor_value":
        break;
      case "respond_host_connected":
        if (message){
          hostmap[origin].rpi.background_rectangle.setAttribute("class","theme_present");
        }else{
          hostmap[origin].rpi.background_rectangle.setAttribute("class","theme_absent");
        }
        break;
      case "response_sdc2160_channel_faults":
        var motor = message["carousel_1"];
        hostmap[origin].carousel_1.set_value("amps", motor["motor_amps"]);
        hostmap[origin].carousel_1.set_value("temp", motor["temperature"]);
        hostmap[origin].carousel_1.set_value("pid error", motor["closed_loop_error"]);
        hostmap[origin].carousel_1.set_value("status", motor["runtime_status_flags"]);
        hostmap[origin].carousel_1.set_value("stall", motor["stall_detection"]);
        var motor = message["carousel_2"];
        hostmap[origin].carousel_2.set_value("amps", motor["motor_amps"]);
        hostmap[origin].carousel_2.set_value("temp", motor["temperature"]);
        hostmap[origin].carousel_2.set_value("pid error", motor["closed_loop_error"]);
        hostmap[origin].carousel_2.set_value("status", motor["runtime_status_flags"]);
        hostmap[origin].carousel_2.set_value("stall", motor["stall_detection"]);
        var motor = message["carousel_3"];
        hostmap[origin].carousel_3.set_value("amps", motor["motor_amps"]);
        hostmap[origin].carousel_3.set_value("temp", motor["temperature"]);
        hostmap[origin].carousel_3.set_value("pid error", motor["closed_loop_error"]);
        hostmap[origin].carousel_3.set_value("status", motor["runtime_status_flags"]);
        hostmap[origin].carousel_3.set_value("stall", motor["stall_detection"]);
        var motor = message["carousel_4"];
        hostmap[origin].carousel_4.set_value("amps", motor["motor_amps"]);
        hostmap[origin].carousel_4.set_value("temp", motor["temperature"]);
        hostmap[origin].carousel_4.set_value("pid error", motor["closed_loop_error"]);
        hostmap[origin].carousel_4.set_value("status", motor["runtime_status_flags"]);
        hostmap[origin].carousel_4.set_value("stall", motor["stall_detection"]);
        var motor = message["carousel_5"];
        hostmap[origin].carousel_5.set_value("amps", motor["motor_amps"]);
        hostmap[origin].carousel_5.set_value("temp", motor["temperature"]);
        hostmap[origin].carousel_5.set_value("pid error", motor["closed_loop_error"]);
        hostmap[origin].carousel_5.set_value("status", motor["runtime_status_flags"]);
        hostmap[origin].carousel_5.set_value("stall", motor["stall_detection"]);
        var motor = message["carousel_center"];
        hostmap[origin].carousel_center.set_value("amps", motor["motor_amps"]);
        hostmap[origin].carousel_center.set_value("temp", motor["temperature"]);
        hostmap[origin].carousel_center.set_value("pid error", motor["closed_loop_error"]);
        hostmap[origin].carousel_center.set_value("status", motor["runtime_status_flags"]);
        hostmap[origin].carousel_center.set_value("stall", motor["stall_detection"]);
        break;
      case "response_sdc2160_closed_loop_error":
        break;
      case "response_sdc2160_controller_faults":
        console.log("response_sdc2160_controller_faults", message);
        break;
      case "response_sdc2160_present":
        var carousel1and2 = message["carousel1and2"]
        var carousel3and4 = message["carousel3and4"]
        var carousel5and6 = message["carousel5and6"]
        if (carousel1and2==""){
          hostmap[origin].sdc_1_2.background_rectangle.setAttribute("class","theme_absent");
        }else{
          hostmap[origin].sdc_1_2.background_rectangle.setAttribute("class","theme_nominal");
        }
        if (carousel3and4==""){
          hostmap[origin].sdc_3_4.background_rectangle.setAttribute("class","theme_absent");
        }else{
          hostmap[origin].sdc_3_4.background_rectangle.setAttribute("class","theme_nominal");
        }
        if (carousel5and6==""){
          hostmap[origin].sdc_5_6.background_rectangle.setAttribute("class","theme_absent");
        }else{
          hostmap[origin].sdc_5_6.background_rectangle.setAttribute("class","theme_nominal");
        }
        break;

      case "update_status":
        if (data_value == "status_absent"){
          hostmap[origin][device].background_rectangle.setAttribute("class","theme_absent");
        }
        if (data_value == "status_present"){
          hostmap[origin][device].background_rectangle.setAttribute("class","theme_present");
        }
        if (data_value == "status_nominal"){
          hostmap[origin][device].background_rectangle.setAttribute("class","theme_nominal");
        }
        if (data_value == "status_fault"){
          hostmap[origin][device].background_rectangle.setAttribute("class","theme_fault");
        }
        break;
      case "update_value":
        if (device == "amps"){
          hostmap[origin][device].set_value(data_value);
        }else{

          hostmap[origin][device].set_value(data_name, data_value);
        }
        break;
      }

}
function websocket_error_handler(evt) {
    console.log("websocket_error_handler", evt)
    if (timers.retry_connection == false) {
        //timers.retry_connection = window.setInterval(try_to_connect, 1000);
    }
}

function try_to_connect() {
    console.log("try_to_connect")
    try {
        websocket_connect()
    }
    catch (e) {
        console.log("connection failed")
    }
}

timers = {
    retry_connection: window.setInterval(try_to_connect, 1000)
}


function update_display_values(data){
  console.log(data)
}

////////// SVG ELEMENT CONVENIENCE METHODS //////////
function create_rectangle(dom_parent, attributes_o = new Object()) {
  var rect = document.createElementNS( SVG_NS, "rect" );
  setAttributes(rect, attributes_o);
  dom_parent.appendChild(rect)
  return rect;
}
function create_text(dom_parent, display_text, attributes_o = new Object()) {
  var text_container = document.createElementNS( SVG_NS, "text");
  setAttributes(text_container, attributes_o);
  text_container.appendChild(document.createTextNode(""))
  text_container.update_text = function(new_text){
    var textnode = document.createTextNode(new_text);
    text_container.replaceChild(textnode, text_container.childNodes[0]);
  }
  text_container.update_text(display_text);
  dom_parent.appendChild(text_container)
  return text_container;
}
function create_group(dom_parent, attributes_o = new Object()){
  var group = document.createElementNS( SVG_NS, "g");
  setAttributes(group, attributes_o);
  dom_parent.appendChild(group);
  return group;
}
function create_path(dom_parent, attributes_o = new Object()){
  var path = document.createElementNS( SVG_NS, "path");
  setAttributes(path, attributes_o);
  dom_parent.appendChild(path);
  return path;
}
function create_ellipse(dom_parent, attributes_o = new Object()){
  var ellipse = document.createElementNS( SVG_NS, "ellipse");
  setAttributes(ellipse, attributes_o);
  dom_parent.appendChild(ellipse);
  return ellipse;
}

////////// INTERFACE COMPONENT CONSTRUCTORS //////////

class Status_Block_Name_Value{
  constructor(dom_parent, coordinates, name, value = "---" ) {
    this.name = name;
    this.value = value;
    this.dom_parent = dom_parent;
    this.container = create_group(
      this.dom_parent,
      {
        class:"status_block_name_value",
        transform:`matrix(1,0,0,1,${coordinates[0]},${coordinates[1]})`,
      }
    );
    this.name_display = create_text(this.container, this.name, {class:"status_block_name"});
    this.value_display = create_text(this.container, this.value, {class:"status_block_value"});
    this.set_value(this.value); // first time setup
  }
  set_value(value){
    this.value = value;
    let textnode = document.createTextNode(this.value);
    this.value_display.replaceChild(textnode, this.value_display.childNodes[0]);
    let offset_for_right_justify = this.dom_parent.getBBox().width - this.value_display.getBBox().width - 30;
    this.value_display.setAttribute('transform', `translate(${offset_for_right_justify},0)`);
  }
}

class Status_Block{
  constructor(dom_parent, coordinates, title, names){
    this.dom_parent = dom_parent;
    this.title = title;
    this.names = names;
    var line_height = 20;
    this.container = create_group(
      this.dom_parent,
      {
        class:"status_block",
        transform:`matrix(1,0,0,1,${coordinates[0]},${coordinates[1]})`,
        height: `${(line_height*(this.names.length+6))}px`,
      }
    );
    let block_height = ((names.length+1)*line_height)
    this.background_rectangle = create_rectangle(
      this.container,
      {
        class:"status_block",
        height:`${block_height}px`,
        width:`180px`,
      }
    );
    this.title = create_text(
      this.container, 
      this.title, 
      {
        class:"status_block_title",
      }
    );
    this.rows = {};
    for (var n_i in this.names){
      this.rows[this.names[n_i]] = new Status_Block_Name_Value(this.container, [10,((n_i)*line_height)+(2*line_height)], this.names[n_i])
    }
  }
  set_value(name, val){
    //console.log("Status_Block set_value", name, val)
    //if (["pin git","tb git"].includes(name)){
    //  val = new Date(val)
    //}
    console.log("name=",name)
    this.rows[name].set_value(val);
  }
}






class Amps_Block{
  constructor(dom_parent, coordinates, title, amps=0){
    this.dom_parent = dom_parent;
    this.title = title;
    this.amps = amps;
    this.container = create_group(
      this.dom_parent,
      {
        class:"status_block",
        transform:`matrix(1,0,0,1,${coordinates[0]},${coordinates[1]})`,
        height: `30px`,
      }
    );
    this.background_rectangle = create_rectangle(
      this.container,
      {
        class:"status_block",
        height:`60px`,
        width:`180px`,
      }
    );
    this.title = create_text(
      this.container, 
      this.title, 
      {
        class:"status_block_title",
      }
    );
    this.amps_display = create_text(
      this.container, 
      this.amps, 
      {
        class:"amps_block_value",
      }
    );
    this.set_value(amps);

  }
  set_value(amps){
    this.amps = Number.parseFloat(amps).toFixed(2)
    let textnode = document.createTextNode(`${this.amps}A`);
    this.amps_display.replaceChild(textnode, this.amps_display.childNodes[0]);
  }
}





class Carousel_Segment{
  constructor(fruit_id, dom_parent) {
    this.fruit_id = fruit_id;
    this.dom_parent = dom_parent;
    var carousel_segment_path = "m 8,13 -3.92158,-5.4041  a 9.448819,9.448819 0 0 1 -7.825628,0  l -3.927775,5.3996 a 16.046641,16.046641 0 0 0 15.674983,0.01 z";
    var angle_increment = 72;
    this.path = create_path(
      dom_parent,
      {
        d:carousel_segment_path,
        transform:`rotate(${angle_increment*this.fruit_id})`,
        class:"carousel_segment"
      }
    )
    this.no_ball_circle = create_ellipse(
      dom_parent,
      {
        class:"carousel_segment background_lines",
        ry:"2",
        rx:"2",
        cy:"18",
        cx:"0",
        transform:`rotate(${angle_increment*this.fruit_id})`,
      }
    )

    this.ball_circle = create_ellipse(
      dom_parent,
      {
        class:"carousel_segment, lit_or_present",
        ry:"2.1",
        rx:"2.1",
        cy:"18",
        cx:"0",
        transform:`rotate(${angle_increment*this.fruit_id})`,
      }
    )

  }
  set_ball_presence(ball_b){
    if (ball_b){ 
      if (!this.dom_parent.contains(this.ball_circle)){
        this.dom_parent.appendChild(this.ball_circle)
      }
    }else{
      if (this.dom_parent.contains(this.ball_circle)){
        this.dom_parent.removeChild(this.ball_circle)
      }
    }
  }
// more methods to follow
}

class Carousel{
  constructor(fruit_id, coordinates, dom_parent) {
    this.fruit_id = fruit_id;
    this.coordinates = coordinates;
    this.dom_parent = dom_parent;
    this.carousel_container = create_group(dom_parent, {transform:`matrix(1,0,0,1,${coordinates[0]},${coordinates[1]})`})

    this.segments = [ // what is the map() syntax for creating an array of class instances?
      new Carousel_Segment(0,this.carousel_container),
      new Carousel_Segment(1,this.carousel_container),
      new Carousel_Segment(2,this.carousel_container),
      new Carousel_Segment(3,this.carousel_container),
      new Carousel_Segment(4,this.carousel_container)
    ]

    this.outer_circle = create_ellipse(
      this.carousel_container,
      {
        class:"carousel_segment background_lines",
         ry:"21",
         rx:"21",
         cy:"0",
         cx:"0"
      }
    )

    this.inner_circle = create_ellipse(
      this.carousel_container,
      {
        class:"carousel_segment",
         ry:"6",
         rx:"6",
         cy:"0",
         cx:"0"
      }
    )

  }
  set_ball_presence(fruit_id, ball_b){
    this.segments[fruit_id].set_ball_presence(ball_b);
  }
  set_angle(deg){
    this.carousel_container.setAttribute('transform', `rotate(${deg})`);
  }
  // more methods to follow
}

class Carousel_Panel{
  constructor(coordinates, dom_parent) {
    this.coordinates = coordinates;
    this.dom_parent = dom_parent;
    const carousel_separate_radius = 44;
    this.carousel_panel = create_group(this.dom_parent, {transform:`matrix(6,0,0,6,${coordinates[0]},${coordinates[1]})`});
    var carousel_coordinates = [
      [0,0],
      [0, -carousel_separate_radius],
      [-carousel_separate_radius*Math.sin(degrees_to_radians(72)),-carousel_separate_radius*Math.cos(degrees_to_radians(72))],
      [carousel_separate_radius*Math.sin(degrees_to_radians(72)),-carousel_separate_radius*Math.cos(degrees_to_radians(72))],
      [-carousel_separate_radius*Math.sin(degrees_to_radians(36)),carousel_separate_radius*Math.cos(degrees_to_radians(36))],
      [carousel_separate_radius*Math.sin(degrees_to_radians(36)),carousel_separate_radius*Math.cos(degrees_to_radians(36))]
    ];

    this.carousels = []
    for (var c_i in carousel_coordinates){
      this.carousels.push(new Carousel(0, carousel_coordinates[c_i], this.carousel_panel));
    }
    const wf_scale_x = 3.9;
    const wf_scale_y = 3.5;
    const wf_translate_x = -200;
    const wf_translate_y = 50;
    this.wireframe_1 = create_path(
      dom_parent,
      {
        d:"m 465.02338,414.43155 -45.90456,63.18218 -50.2614,0.0552 V 138.47816",
        transform:`translate(${wf_translate_x},${wf_translate_y}),scale(${wf_scale_x},${wf_scale_y})`,
        class:"carousel_segment"
      }
    )
    this.wireframe_2 = create_path(
      dom_parent,
      {
        d:"m 429.03962,304.95539 -9.9208,-3.22347 v -163.25376 0",
        transform:`translate(${wf_translate_x},${wf_translate_y}),scale(${wf_scale_x},${wf_scale_y})`,
        class:"carousel_segment"
      }
    )
    this.wireframe_3 = create_path(
      dom_parent,
      {
        d:"m 489.44078,259.34863 -17.19474,-5.5869 v -115.28357 0",
        transform:`translate(${wf_translate_x},${wf_translate_y}),scale(${wf_scale_x},${wf_scale_y})`,
        class:"carousel_segment"
      }
    )
    this.wireframe_4 = create_path(
      dom_parent,
      {
        d:"m 523.16884,138.47816 v 43.49431 l 66.50143,21.60762 v 76.49037 l 0.26536,0.0862",
        transform:`translate(${wf_translate_x},${wf_translate_y}),scale(${wf_scale_x},${wf_scale_y})`,
        class:"carousel_segment"
      }
    )
    this.wireframe_5 = create_path(
      dom_parent,
      {
        d:"m 583.74048,418.20139 17.04119,23.45518 h 26.43715 V 200.93073 l -51.1432,-16.61743 v -45.83514",
        transform:`translate(${wf_translate_x},${wf_translate_y}),scale(${wf_scale_x},${wf_scale_y})`,
        class:"carousel_segment"
      }
    )
    this.wireframe_5 = create_path(
      dom_parent,
      {
        d:"m 523.16884,368.63215 v 108.7365 H 676.59848 V 200.93073 l -49.37966,-16.04442 v -46.40815 0",
        transform:`translate(${wf_translate_x},${wf_translate_y}),scale(${wf_scale_x},${wf_scale_y})`,
        class:"carousel_segment"
      }
    )
  }
  set_ball_presence(carousel_id, fruit_id, ball_b){
    this.carousels[carousel_id].set_ball_presence(fruit_id,ball_b);
  }
  set_carousel_angle(carousel_id, deg){
    this.carousels[carousel_id].set_angle(deg);
  }
  // more methods to follow
}

/* ########### D I S P L A Y S ########### */

class Display{
  constructor(coordinates, dom_parent) {
    this.coordinates = coordinates;
    this.dom_parent = dom_parent;
    var paths_como = [
       "m 18.568802,24.359315 c -3.439583,0 -5.365749,2.247194 -5.365749,4.952999 v 0.04586 c 0,2.705804 1.926166,4.907137 5.365749,4.907137 3.439582,0 5.319887,-2.201333 5.319887,-4.907137 v -0.04586 c 0,-2.705805 -1.880305,-4.952999 -5.319887,-4.952999 z m 9.905997,30.543492 v -7.475359 h -0.04586 c -3.531304,2.201332 -7.750526,3.714749 -11.602858,3.714749 -2.705805,0 -4.815415,-0.596195 -4.815415,-2.568222 0,-1.605138 1.513416,-3.118555 9.997719,-5.090582 v -6.466415 h -0.04586 C 9.7634708,39.17245 3.6180835,42.474449 3.6180835,49.078447 c 0,6.191249 5.9160818,8.805331 12.4283575,8.805331 4.907138,0 8.75947,-1.28411 12.428358,-2.980971 z",
       "m 48.293705,51.050475 c 5.778499,0 10.227026,-1.834444 12.565942,-3.439583 v -8.209137 h -0.04586 c -3.439583,2.568222 -6.970888,4.265083 -11.740442,4.265083 -6.466415,0 -10.043581,-3.898194 -10.043581,-9.355665 0,-5.595054 3.760611,-9.539108 10.089442,-9.539108 4.769555,0 8.163276,2.017888 11.694581,4.356804 h 0.04586 v -8.117414 c -2.568222,-1.834444 -6.695721,-3.623027 -12.015608,-3.623027 -11.832164,0 -18.34444,7.612942 -18.34444,16.968606 0,9.263942 5.640915,16.693441 17.794106,16.693441 z",
       "m 82.696478,51.142197 c 11.052525,0 18.023412,-6.603999 18.023412,-16.922746 0,-10.318747 -6.970887,-16.922745 -18.023412,-16.922745 -11.006664,0 -17.977551,6.603998 -17.977551,16.922745 0,10.318747 6.970887,16.922746 17.977551,16.922746 z m 0,-7.337776 c -6.099526,0 -9.539109,-3.577166 -9.539109,-9.58497 0,-6.007804 3.531305,-9.58497 9.58497,-9.58497 6.099526,0 9.539108,3.577166 9.539108,9.58497 0,6.007804 -3.531304,9.58497 -9.584969,9.58497 z",
       "m 106.13853,50.270836 h 8.16328 V 30.367119 h 0.18344 l 10.45633,18.069273 h 0.55034 l 10.59391,-18.069273 h 0.13758 v 19.903717 h 8.255 v -32.10277 h -9.81427 l -9.26395,16.555857 -9.49324,-16.555857 h -9.76842 z",
       "m 167.8746,51.142197 c 11.05252,0 18.02341,-6.603999 18.02341,-16.922746 0,-10.318747 -6.97089,-16.922745 -18.02341,-16.922745 -11.00667,0 -17.97755,6.603998 -17.97755,16.922745 0,10.318747 6.97088,16.922746 17.97755,16.922746 z m 0,-7.337776 c -6.09953,0 -9.53911,-3.577166 -9.53911,-9.58497 0,-6.007804 3.5313,-9.58497 9.58497,-9.58497 6.09952,0 9.53911,3.577166 9.53911,9.58497 0,6.007804 -3.53131,9.58497 -9.58497,9.58497 z",
       "m 201.41309,50.270836 h 28.06699 l 0.27517,-7.108471 h -19.99544 v -6.007804 h 15.40933 V 30.41298 h -15.40933 v -5.136443 h 19.39925 l -0.32103,-7.108471 h -27.42494 z",
       "m 235.21972,50.270836 h 25.72807 l 0.32103,-7.429498 H 243.6123 V 18.168066 h -8.39258 z",
       "m 276.00426,50.270836 h 16.55586 c 10.04358,0 16.14311,-5.961943 16.14311,-16.097246 0,-10.135303 -6.09953,-16.005524 -16.14311,-16.005524 h -16.55586 z m 8.39258,-7.200193 V 25.368259 h 7.61295 c 5.13644,0 8.16327,2.751666 8.16327,8.897053 0,6.145388 -3.02683,8.805331 -8.16327,8.805331 z",
       "m 314.16773,50.270836 h 8.39258 v -32.10277 h -8.39258 z",
       "m 329.85924,50.270836 h 8.07156 V 29.954369 h 0.18344 l 15.31761,20.316467 h 8.57602 v -32.10277 h -8.07155 v 19.720273 h -0.18344 L 338.80216,18.168066 h -8.94292 z",
       "m 369.21508,50.270836 h 28.06699 l 0.27517,-7.108471 H 377.5618 v -6.007804 h 15.40933 V 30.41298 H 377.5618 v -5.136443 h 19.39924 l -0.32102,-7.108471 h -27.42494 z",
       "m 403.02169,50.270836 h 8.39258 v -8.942914 h 7.29191 l 6.3747,8.942914 h 9.67669 l -7.88811,-10.548053 c 4.31094,-1.559277 6.55814,-5.044721 6.55814,-10.272886 0,-7.337776 -4.08164,-11.281831 -12.47422,-11.281831 h -17.93169 z m 8.39258,-15.822079 v -9.17222 h 8.80533 c 3.53131,0 4.76956,1.926166 4.76956,4.540249 0,2.659943 -1.23825,4.631971 -4.76956,4.631971 z",
       "m 455.21865,51.142197 c 11.05253,0 18.02341,-6.603999 18.02341,-16.922746 0,-10.318747 -6.97088,-16.922745 -18.02341,-16.922745 -11.00666,0 -17.97755,6.603998 -17.97755,16.922745 0,10.318747 6.97089,16.922746 17.97755,16.922746 z m 0,-7.337776 c -6.09952,0 -9.53911,-3.577166 -9.53911,-9.58497 0,-6.007804 3.53131,-9.58497 9.58497,-9.58497 6.09953,0 9.53911,3.577166 9.53911,9.58497 0,6.007804 -3.5313,9.58497 -9.58497,9.58497 z",
       "m 89.80514,93.83888 h 8.392581 V 82.327744 H 114.11152 V 75.402718 H 98.197721 V 68.890442 H 117.18422 L 116.90905,61.73611 H 89.80514 Z",
       "m 116.68671,93.83888 h 8.66775 l 2.56822,-7.108471 h 14.30866 l 2.56822,7.108471 h 8.75947 l -11.7863,-32.10277 h -13.25386 z m 17.5648,-24.673272 h 1.69686 l 3.8982,10.82322 h -9.49325 z",
       "m 172.64419,94.618518 c 5.7785,0 10.22703,-1.834444 12.56594,-3.439582 v -8.209137 h -0.0459 c -3.43958,2.568222 -6.97089,4.265082 -11.74044,4.265082 -6.46642,0 -10.04358,-3.898193 -10.04358,-9.355664 0,-5.595054 3.76061,-9.539109 10.08944,-9.539109 4.76955,0 8.16328,2.017889 11.69458,4.356805 h 0.0459 v -8.117415 c -2.56822,-1.834444 -6.69572,-3.623027 -12.01561,-3.623027 -11.83216,0 -18.34444,7.612943 -18.34444,16.968607 0,9.263942 5.64092,16.69344 17.79411,16.69344 z",
       "m 191.17907,93.83888 h 8.39258 V 61.73611 h -8.39258 z",
       "m 206.87058,93.83888 h 25.72807 l 0.32103,-7.429498 H 215.26316 V 61.73611 h -8.39258 z",
       "m 237.65043,93.83888 h 8.39258 V 61.73611 h -8.39258 z",
       "m 262.14728,93.83888 h 8.39258 V 69.165608 h 11.41941 L 281.6841,61.73611 h -30.63521 l -0.32103,7.429498 h 11.41942 z",
       "m 280.54453,93.83888 h 8.66775 l 2.56822,-7.108471 h 14.30866 l 2.56823,7.108471 h 8.75947 L 305.63055,61.73611 H 292.3767 Z m 17.5648,-24.673272 h 1.69686 l 3.8982,10.82322 h -9.49325 z",
       "m 331.60192,93.83888 h 28.067 l 0.27516,-7.108471 h -19.99544 v -6.007804 h 15.40933 v -6.741581 h -15.40933 v -5.136443 h 19.39925 l -0.32103,-7.108471 h -27.42494 z",
       "m 365.40856,93.83888 h 25.72808 l 0.32103,-7.429498 H 373.80115 V 61.73611 h -8.39259 z",
       "m 50.803787,137.40692 h 8.392582 v -32.10277 h -8.392582 z",
       "m 66.495299,137.40692 h 8.071553 v -20.31646 h 0.183445 l 15.317607,20.31646 h 8.576025 v -32.10277 h -8.071553 v 19.72028 H 90.388932 L 75.438213,105.30415 h -8.942914 z",
       "m 114.65646,137.40692 h 8.39259 v -24.67327 h 11.41941 l -0.27517,-7.4295 h -30.63521 l -0.32103,7.4295 h 11.41941 z",
       "m 139.06154,137.40692 h 28.067 l 0.27516,-7.10847 h -19.99544 v -6.0078 h 15.40933 v -6.74158 h -15.40933 v -5.13645 h 19.39925 l -0.32103,-7.10847 h -27.42494 z",
       "m 172.86818,137.40692 h 8.39258 v -8.94291 h 7.29191 l 6.3747,8.94291 h 9.67669 l -7.88811,-10.54805 c 4.31094,-1.55928 6.55814,-5.04472 6.55814,-10.27289 0,-7.33777 -4.08164,-11.28183 -12.47422,-11.28183 h -17.93169 z m 8.39258,-15.82208 v -9.17222 h 8.80533 c 3.5313,0 4.76955,1.92617 4.76955,4.54025 0,2.65995 -1.23825,4.63197 -4.76955,4.63197 z",
       "m 224.88168,138.18656 c 5.7785,0 10.22703,-1.83444 12.56594,-3.43958 v -8.20914 h -0.0459 c -3.43958,2.56822 -6.97089,4.26509 -11.74044,4.26509 -6.46641,0 -10.04358,-3.8982 -10.04358,-9.35567 0,-5.59505 3.76061,-9.53911 10.08944,-9.53911 4.76956,0 8.16328,2.01789 11.69458,4.35681 h 0.0459 v -8.11742 c -2.56822,-1.83444 -6.69572,-3.62302 -12.0156,-3.62302 -11.83217,0 -18.34444,7.61294 -18.34444,16.9686 0,9.26394 5.64091,16.69344 17.7941,16.69344 z",
       "m 240.16043,137.40692 h 8.66774 l 2.56823,-7.10847 h 14.30866 l 2.56822,7.10847 h 8.75947 l -11.7863,-32.10277 h -13.25386 z m 17.5648,-24.67327 h 1.69686 l 3.89819,10.82322 h -9.49325 z",
       "m 281.12138,137.40692 h 8.16328 v -19.90371 h 0.18344 l 10.45633,18.06927 h 0.55034 l 10.59391,-18.06927 h 0.13758 v 19.90371 h 8.255 v -32.10277 h -9.81427 l -9.26395,16.55586 -9.49324,-16.55586 h -9.76842 z",
       "m 326.66849,137.40692 h 18.48202 c 7.06261,0 12.10733,-2.38477 12.10733,-9.03463 0,-3.80647 -1.97203,-6.00781 -6.09953,-7.65881 3.98992,-1.19239 5.41161,-3.76061 5.41161,-7.33777 0,-5.31989 -3.98991,-8.07156 -10.63977,-8.07156 h -19.26166 z m 8.25499,-19.2158 v -6.14538 h 9.26395 c 2.75166,0 4.03577,0.87136 4.03577,2.98097 0,2.29305 -1.14652,3.16441 -4.03577,3.16441 z m 0,12.47422 v -6.69572 h 9.6767 c 3.16441,0 4.26508,1.10067 4.26508,3.302 0,2.29306 -1.19239,3.302 -4.26508,3.34786 z",
       "m 362.44716,137.40692 h 8.39258 v -32.10277 h -8.39258 z",
       "m 394.32764,138.27828 c 11.05252,0 18.02341,-6.60399 18.02341,-16.92274 0,-10.31875 -6.97089,-16.92275 -18.02341,-16.92275 -11.00667,0 -17.97755,6.604 -17.97755,16.92275 0,10.31875 6.97088,16.92274 17.97755,16.92274 z m 0,-7.33777 c -6.09953,0 -9.53911,-3.57717 -9.53911,-9.58497 0,-6.00781 3.5313,-9.58497 9.58497,-9.58497 6.09953,0 9.53911,3.57716 9.53911,9.58497 0,6.0078 -3.53131,9.58497 -9.58497,9.58497 z",
       "m 415.52239,107.41376 v 7.4295 h 0.0459 c 3.53131,-2.20133 7.75053,-3.71475 11.60286,-3.71475 2.70581,0 4.81542,0.5962 4.81542,2.56823 0,1.65099 -1.51342,3.16441 -9.99772,5.09058 v 6.51227 h 0.0459 c 12.19905,-2.20133 18.34444,-5.50333 18.34444,-12.10733 0,-6.19125 -5.91608,-8.75947 -12.3825,-8.75947 -4.953,0 -8.80533,1.23825 -12.47422,2.98097 z m 9.95186,30.49764 c 3.39372,0 5.31989,-2.20134 5.31989,-4.953 v -0.0459 c 0,-2.70581 -1.92617,-4.90714 -5.31989,-4.90714 -3.48544,0 -5.36575,2.20133 -5.36575,4.90714 v 0.0917 c 0,2.7058 1.88031,4.90714 5.36575,4.90714 z"
    ];
    var paths_fue = [
       "m 86.452299,24.491605 c -3.439582,0 -5.365749,2.247194 -5.365749,4.952998 v 0.04586 c 0,2.705804 1.926167,4.907137 5.365749,4.907137 3.439582,0 5.319888,-2.201333 5.319888,-4.907137 v -0.04586 c 0,-2.705804 -1.880306,-4.952998 -5.319888,-4.952998 z m 9.905997,30.543492 v -7.475359 h -0.04586 c -3.531304,2.201332 -7.750525,3.714749 -11.602858,3.714749 -2.705805,0 -4.815415,-0.596195 -4.815415,-2.568222 0,-1.605138 1.513416,-3.118555 9.997719,-5.090582 v -6.466415 h -0.04586 C 77.64697,39.30474 71.501583,42.606739 71.501583,49.210737 c 0,6.191249 5.916081,8.805331 12.428358,8.805331 4.907137,0 8.75947,-1.284111 12.428357,-2.980971 z",
       "m 101.91441,50.403126 h 8.39258 V 38.89199 h 15.9138 v -6.925026 h -15.9138 v -6.512276 h 18.98649 l -0.27516,-7.154332 h -27.10391 z",
       "m 149.89208,51.274487 c 9.12636,0 15.9138,-3.577166 15.9138,-13.529025 V 18.300356 h -8.39258 v 19.261662 c 0,4.723693 -3.5313,6.145387 -7.47536,6.145387 -3.94405,0 -7.42949,-1.513416 -7.42949,-6.328831 V 18.300356 H 134.07 v 19.628551 c 0,9.768414 6.64986,13.34558 15.82208,13.34558 z",
       "m 172.73793,50.403126 h 28.06699 l 0.27517,-7.108471 h -19.99544 v -6.007804 h 15.40933 V 30.54527 h -15.40933 v -5.136443 h 19.39924 l -0.32103,-7.108471 h -27.42493 z",
       "m 216.64098,50.403126 h 16.55586 c 10.04358,0 16.1431,-5.961943 16.1431,-16.097246 0,-10.135303 -6.09952,-16.005524 -16.1431,-16.005524 h -16.55586 z m 8.39258,-7.200193 V 25.500549 h 7.61294 c 5.13645,0 8.16328,2.751666 8.16328,8.897053 0,6.145387 -3.02683,8.805331 -8.16328,8.805331 z",
       "m 254.80443,50.403126 h 8.39259 v -32.10277 h -8.39259 z",
       "m 270.49595,50.403126 h 8.39258 V 38.89199 h 15.9138 v -6.925026 h -15.9138 v -6.512276 h 18.98649 l -0.27516,-7.154332 h -27.10391 z",
       "m 303.66049,14.860774 h 7.15434 l 8.07155,-7.337776 V 7.0185259 h -9.58497 z m -0.64205,35.542352 h 8.39258 v -32.10277 h -8.39258 z",
       "m 334.71547,51.182764 c 5.7785,0 10.22703,-1.834444 12.56594,-3.439582 v -8.209137 h -0.0459 c -3.43958,2.568222 -6.97088,4.265082 -11.74044,4.265082 -6.46641,0 -10.04358,-3.898193 -10.04358,-9.355664 0,-5.595054 3.76061,-9.539108 10.08944,-9.539108 4.76956,0 8.16328,2.017888 11.69458,4.356804 h 0.0459 v -8.117415 c -2.56822,-1.834444 -6.69572,-3.623026 -12.0156,-3.623026 -11.83217,0 -18.34444,7.612942 -18.34444,16.968606 0,9.263942 5.64091,16.69344 17.7941,16.69344 z",
       "m 353.25036,50.403126 h 8.39258 v -32.10277 h -8.39258 z",
       "m 368.94187,50.403126 h 25.72807 l 0.32103,-7.429498 H 377.33445 V 18.300356 h -8.39258 z",
       "m 36.876387,93.971169 h 8.392581 V 61.8684 h -8.392581 z",
       "m 52.567898,93.971169 h 8.071554 V 73.654703 h 0.183444 l 15.317607,20.316466 h 8.576026 V 61.8684 H 76.644975 V 81.588673 H 76.461531 L 61.510812,61.8684 h -8.942914 z",
       "m 100.72906,93.971169 h 8.39259 V 69.297898 h 11.41941 L 120.26589,61.8684 H 89.630678 l -0.321028,7.429498 h 11.41941 z",
       "m 125.13414,93.971169 h 28.067 l 0.27516,-7.10847 h -19.99544 v -6.007804 h 15.40933 V 74.113314 H 133.48086 V 68.97687 h 19.39925 l -0.32103,-7.10847 h -27.42494 z",
       "m 158.94078,93.971169 h 8.39258 v -8.942914 h 7.29191 l 6.3747,8.942914 h 9.67669 l -7.88811,-10.548052 c 4.31094,-1.559278 6.55814,-5.044721 6.55814,-10.272887 0,-7.337775 -4.08164,-11.28183 -12.47422,-11.28183 h -17.93169 z m 8.39258,-15.822079 v -9.17222 h 8.80533 c 3.5313,0 4.76955,1.926167 4.76955,4.540249 0,2.659944 -1.23825,4.631971 -4.76955,4.631971 z",
       "m 210.95428,94.750808 c 5.7785,0 10.22703,-1.834444 12.56594,-3.439582 v -8.209137 h -0.0459 c -3.43958,2.568222 -6.97089,4.265082 -11.74044,4.265082 -6.46642,0 -10.04358,-3.898193 -10.04358,-9.355664 0,-5.595054 3.76061,-9.539109 10.08944,-9.539109 4.76956,0 8.16328,2.017889 11.69458,4.356805 h 0.0459 v -8.117415 c -2.56822,-1.834444 -6.69572,-3.623027 -12.01561,-3.623027 -11.83216,0 -18.34444,7.612943 -18.34444,16.968607 0,9.263942 5.64092,16.69344 17.79411,16.69344 z",
       "m 226.23303,93.971169 h 8.66774 l 2.56823,-7.10847 h 14.30866 l 2.56822,7.10847 h 8.75947 L 251.31905,61.8684 h -13.25386 z m 17.5648,-24.673271 h 1.69686 l 3.89819,10.82322 h -9.49325 z",
       "m 267.19398,93.971169 h 8.16328 V 74.067452 h 0.18344 l 10.45633,18.069274 h 0.55034 l 10.59391,-18.069274 h 0.13758 v 19.903717 h 8.255 V 61.8684 h -9.81427 L 286.45564,78.424257 276.9624,61.8684 h -9.76842 z",
       "m 312.74109,93.971169 h 18.48202 c 7.06261,0 12.10733,-2.384777 12.10733,-9.034636 0,-3.806471 -1.97203,-6.007804 -6.09953,-7.658804 3.98992,-1.192388 5.41161,-3.76061 5.41161,-7.337776 0,-5.319887 -3.98991,-8.071553 -10.63977,-8.071553 h -19.26166 z m 8.25499,-19.2158 v -6.145387 h 9.26395 c 2.75166,0 4.03577,0.871361 4.03577,2.980971 0,2.293055 -1.14653,3.164416 -4.03577,3.164416 z m 0,12.474219 v -6.695721 h 9.6767 c 3.16441,0 4.26508,1.100667 4.26508,3.302 0,2.293055 -1.19239,3.301999 -4.26508,3.34786 z",
       "m 348.51976,93.971169 h 8.39258 V 61.8684 h -8.39258 z",
       "m 361.04685,93.971169 h 8.66775 l 2.56822,-7.10847 h 14.30867 l 2.56822,7.10847 h 8.75947 L 386.13288,61.8684 h -13.25386 z m 17.5648,-24.673271 h 1.69687 l 3.89819,10.82322 h -9.49325 z",
       "m 402.00781,93.971169 h 8.39258 v -8.942914 h 7.29191 l 6.3747,8.942914 h 9.67669 l -7.88811,-10.548052 c 4.31094,-1.559278 6.55814,-5.044721 6.55814,-10.272887 0,-7.337775 -4.08164,-11.28183 -12.47422,-11.28183 h -17.93169 z m 8.39258,-15.822079 v -9.17222 h 8.80533 c 3.53131,0 4.76956,1.926167 4.76956,4.540249 0,2.659944 -1.23825,4.631971 -4.76956,4.631971 z",
       "m 17.133333,137.53921 h 8.392581 v -24.67327 h 11.419413 l -0.275166,-7.4295 H 6.0349465 l -0.3210277,7.4295 H 17.133333 Z",
       "m 57.085325,138.41057 c 9.126359,0 15.913802,-3.57716 15.913802,-13.52902 v -19.44511 h -8.392582 v 19.26167 c 0,4.72369 -3.531304,6.14538 -7.475359,6.14538 -3.944054,0 -7.429498,-1.51341 -7.429498,-6.32883 v -19.07822 h -8.438442 v 19.62855 c 0,9.76842 6.649859,13.34558 15.822079,13.34558 z",
       "m 93.276728,138.31885 c 11.602862,0 14.675552,-5.82436 14.675552,-10.41047 0,-6.87916 -5.73264,-8.71361 -12.290775,-9.86013 -5.365748,-0.96309 -8.438442,-1.19239 -8.438442,-3.43959 0,-1.74272 1.696861,-2.84338 5.778498,-2.84338 4.127499,0 9.034639,1.42169 12.795249,3.66888 h 0.0459 v -8.02569 c -3.66889,-1.78858 -8.117415,-2.75166 -12.199053,-2.75166 -10.181164,0 -15.042441,4.86127 -15.042441,10.54805 0,6.42055 5.640915,8.43844 12.199053,9.49325 7.10847,1.19238 8.576025,1.74272 8.576025,3.62302 0,1.83445 -1.972027,2.88925 -5.824359,2.88925 -4.494388,0 -9.814276,-1.42169 -14.813135,-4.03578 h -0.04586 v 8.07156 c 4.219222,1.83444 8.75947,3.07269 14.58383,3.07269 z",
       "m 122.73356,137.53921 h 8.39258 v -8.25499 h 8.89705 c 7.29192,0 12.56594,-3.80648 12.56594,-12.06147 0,-7.29192 -4.08164,-11.78631 -11.87802,-11.78631 h -17.97755 z m 8.39258,-15.27174 v -9.72256 h 8.30086 c 3.25614,0 4.81541,1.69686 4.81541,4.86128 0,2.79753 -1.42169,4.86128 -4.67783,4.86128 z",
       "m 157.36568,137.53921 h 8.39258 v -8.94291 h 7.29191 l 6.37469,8.94291 h 9.6767 l -7.88811,-10.54805 c 4.31094,-1.55928 6.55813,-5.04472 6.55813,-10.27289 0,-7.33777 -4.08163,-11.28183 -12.47421,-11.28183 h -17.93169 z m 8.39258,-15.82208 v -9.17222 h 8.80533 c 3.5313,0 4.76955,1.92617 4.76955,4.54025 0,2.65995 -1.23825,4.63197 -4.76955,4.63197 z",
       "m 209.56262,138.41057 c 11.05253,0 18.02342,-6.60399 18.02342,-16.92274 0,-10.31875 -6.97089,-16.92275 -18.02342,-16.92275 -11.00666,0 -17.97755,6.604 -17.97755,16.92275 0,10.31875 6.97089,16.92274 17.97755,16.92274 z m 0,-7.33777 c -6.09952,0 -9.5391,-3.57717 -9.5391,-9.58497 0,-6.00781 3.5313,-9.58497 9.58496,-9.58497 6.09953,0 9.53911,3.57716 9.53911,9.58497 0,6.0078 -3.5313,9.58497 -9.58497,9.58497 z",
       "m 233.00467,137.53921 h 16.55585 c 10.04359,0 16.14311,-5.96194 16.14311,-16.09724 0,-10.13531 -6.09952,-16.00553 -16.14311,-16.00553 h -16.55585 z m 8.39258,-7.20019 v -17.70238 h 7.61294 c 5.13644,0 8.16328,2.75166 8.16328,8.89705 0,6.14539 -3.02684,8.80533 -8.16328,8.80533 z",
       "m 286.62333,138.41057 c 9.12636,0 15.9138,-3.57716 15.9138,-13.52902 v -19.44511 h -8.39258 v 19.26167 c 0,4.72369 -3.53131,6.14538 -7.47536,6.14538 -3.94406,0 -7.4295,-1.51341 -7.4295,-6.32883 v -19.07822 h -8.43844 v 19.62855 c 0,9.76842 6.64986,13.34558 15.82208,13.34558 z",
       "m 325.47467,138.31885 c 5.7785,0 10.22702,-1.83444 12.56594,-3.43958 v -8.20914 h -0.0459 c -3.43958,2.56822 -6.97089,4.26508 -11.74044,4.26508 -6.46642,0 -10.04358,-3.89819 -10.04358,-9.35566 0,-5.59505 3.76061,-9.53911 10.08944,-9.53911 4.76955,0 8.16327,2.01789 11.69458,4.35681 h 0.0459 v -8.11742 c -2.56822,-1.83444 -6.69572,-3.62302 -12.01561,-3.62302 -11.83216,0 -18.34444,7.61294 -18.34444,16.9686 0,9.26394 5.64092,16.69344 17.79411,16.69344 z",
       "m 352.67725,137.53921 h 8.39258 v -24.67327 h 11.41941 l -0.27516,-7.4295 h -30.63522 l -0.32103,7.4295 h 11.41942 z",
       "m 392.2623,138.41057 c 11.05253,0 18.02341,-6.60399 18.02341,-16.92274 0,-10.31875 -6.97088,-16.92275 -18.02341,-16.92275 -11.00666,0 -17.97755,6.604 -17.97755,16.92275 0,10.31875 6.97089,16.92274 17.97755,16.92274 z m 0,-7.33777 c -6.09953,0 -9.53911,-3.57717 -9.53911,-9.58497 0,-6.00781 3.53131,-9.58497 9.58497,-9.58497 6.09953,0 9.53911,3.57716 9.53911,9.58497 0,6.0078 -3.5313,9.58497 -9.58497,9.58497 z",
       "m 429.14159,138.31885 c 11.60286,0 14.67555,-5.82436 14.67555,-10.41047 0,-6.87916 -5.73264,-8.71361 -12.29077,-9.86013 -5.36575,-0.96309 -8.43845,-1.19239 -8.43845,-3.43959 0,-1.74272 1.69686,-2.84338 5.7785,-2.84338 4.1275,0 9.03464,1.42169 12.79525,3.66888 h 0.0459 v -8.02569 c -3.66889,-1.78858 -8.11741,-2.75166 -12.19905,-2.75166 -10.18117,0 -15.04244,4.86127 -15.04244,10.54805 0,6.42055 5.64091,8.43844 12.19905,9.49325 7.10847,1.19238 8.57602,1.74272 8.57602,3.62302 0,1.83445 -1.97202,2.88925 -5.82435,2.88925 -4.49439,0 -9.81428,-1.42169 -14.81314,-4.03578 h -0.0459 v 8.07156 c 4.21922,1.83444 8.75947,3.07269 14.58383,3.07269 z",
       "m 446.75924,107.54605 v 7.4295 h 0.0459 c 3.53131,-2.20133 7.75053,-3.71475 11.60286,-3.71475 2.7058,0 4.81541,0.5962 4.81541,2.56822 0,1.651 -1.51341,3.16442 -9.99772,5.09059 v 6.51227 h 0.0459 c 12.19905,-2.20133 18.34444,-5.50333 18.34444,-12.10733 0,-6.19125 -5.91609,-8.75947 -12.3825,-8.75947 -4.953,0 -8.80533,1.23825 -12.47422,2.98097 z m 9.95186,30.49764 c 3.39372,0 5.31989,-2.20134 5.31989,-4.953 v -0.0459 c 0,-2.70581 -1.92617,-4.90714 -5.31989,-4.90714 -3.48545,0 -5.36575,2.20133 -5.36575,4.90714 v 0.0917 c 0,2.7058 1.8803,4.90714 5.36575,4.90714 z",
    ];
    var paths_juega = [
       "m 116.98816,100.80272 c 14.82372,0 23.51616,-6.131278 23.51616,-19.713221 V 45.15556 h -33.6056 l -0.54328,12.029721 h 19.94605 v 21.88633 c 0,6.752165 -4.11339,9.23572 -10.55511,9.23572 -5.82083,0 -12.34016,-2.017888 -18.393828,-6.441721 h -0.07761 v 13.581943 c 5.898438,3.647721 12.184938,5.355167 19.713218,5.355167 z",
       "m 178.13854,100.95794 c 15.44461,0 26.93105,-6.053665 26.93105,-22.895274 V 45.15556 h -14.20283 v 32.596662 c 0,7.993943 -5.97605,10.399887 -12.65061,10.399887 -6.67455,0 -12.573,-2.561166 -12.573,-10.710331 V 45.15556 h -14.28044 v 33.217551 c 0,16.531164 11.25361,22.584829 26.77583,22.584829 z",
       "m 216.3937,99.48333 h 47.49799 l 0.46567,-12.029721 H 230.51892 V 77.286555 h 26.07733 V 65.877724 h -26.07733 v -8.692443 h 32.82949 L 262.80513,45.15556 H 216.3937 Z",
       "m 300.12881,100.88033 c 15.44461,0 29.33699,-7.838721 29.33699,-27.707163 0,-2.405944 -0.15522,-4.035777 -0.23283,-5.587999 h -31.19966 v 10.787943 h 17.69533 c -0.38806,6.829777 -6.51933,10.555109 -14.51328,10.555109 -11.176,0 -16.91922,-6.674554 -16.91922,-15.910275 0,-10.244665 6.44172,-16.91922 18.00578,-16.91922 7.99394,0 14.04761,2.871611 20.2565,6.674555 h 0.0776 V 49.424171 c -4.8895,-3.337278 -12.49539,-5.66561 -20.64456,-5.66561 -20.64455,0 -32.2086,13.42672 -32.2086,29.259384 0,15.910275 10.86555,27.862385 30.34594,27.862385 z",
       "m 331.70933,99.48333 h 14.6685 l 4.34622,-12.029721 h 24.21466 l 4.34622,12.029721 h 14.82372 L 374.1626,45.15556 h -22.42961 z m 29.72505,-41.754772 h 2.87161 l 6.59695,18.31622 h -16.0655 z",
    ]
    var paths_dinero = [
       "m 70.982412,99.483337 h 28.017607 c 16.996831,0 27.319111,-10.089442 27.319111,-27.241495 0,-17.152053 -10.32228,-27.086274 -27.319111,-27.086274 H 70.982412 Z M 85.185243,87.298395 V 57.340511 h 12.883443 c 8.692444,0 13.814774,4.656665 13.814774,15.056553 0,10.399887 -5.12233,14.901331 -13.814774,14.901331 z",
       "m 137.80551,99.483337 h 14.20283 V 45.155568 h -14.20283 z",
       "m 166.59916,99.483337 h 13.65956 V 65.10162 h 0.31044 l 25.92211,34.381717 h 14.51328 V 45.155568 h -13.65956 v 33.372773 h -0.31044 L 181.73333,45.155568 h -15.13417 z",
       "m 235.44015,99.483337 h 47.49799 l 0.46566,-12.02972 H 249.56537 V 77.286563 h 26.07732 V 65.877731 h -26.07732 v -8.692443 h 32.82949 l -0.54328,-12.02972 h -46.41143 z",
       "m 294.89016,99.483337 h 14.20283 V 84.349173 h 12.34016 l 10.78795,15.134164 h 16.37594 L 335.24793,81.632785 c 7.29544,-2.638778 11.09839,-8.537221 11.09839,-17.384887 0,-12.417776 -6.90739,-19.09233 -21.11022,-19.09233 h -30.34594 z m 14.20283,-26.775829 v -15.52222 h 14.90133 c 5.97605,0 8.07155,3.259666 8.07155,7.683499 0,4.501444 -2.0955,7.838721 -8.07155,7.838721 z",
       "m 385.46226,100.95795 c 18.70427,0 30.50116,-11.176 30.50116,-28.638497 0,-17.462498 -11.79689,-28.638496 -30.50116,-28.638496 -18.62666,0 -30.42355,11.175998 -30.42355,28.638496 0,17.462497 11.79689,28.638497 30.42355,28.638497 z m 0,-12.417778 c -10.32228,0 -16.14311,-6.053665 -16.14311,-16.220719 0,-10.167054 5.97606,-16.22072 16.22072,-16.22072 10.32228,0 16.14311,6.053666 16.14311,16.22072 0,10.167054 -5.97605,16.220719 -16.22072,16.220719 z"
    ]
    var paths_trueque = [
       "M 38.787916,99.483345 H 52.990747 V 57.728574 H 72.315911 L 71.850244,45.155576 H 20.00603 l -0.543278,12.572998 h 19.325164 z",
       "M 81.798446,99.483345 H 96.001277 V 84.349181 h 12.340163 l 10.78795,15.134164 h 16.37594 L 122.15622,81.632792 c 7.29544,-2.638777 11.09839,-8.537221 11.09839,-17.384886 0,-12.417776 -6.90739,-19.09233 -21.11022,-19.09233 H 81.798446 Z M 96.001277,72.707516 v -15.52222 h 14.901333 c 5.97605,0 8.07155,3.259666 8.07155,7.683499 0,4.501444 -2.0955,7.838721 -8.07155,7.838721 z",
       "m 170.59953,100.95796 c 15.4446,0 26.93105,-6.05367 26.93105,-22.895278 V 45.155576 h -14.20283 v 32.596661 c 0,7.993943 -5.97606,10.399888 -12.65061,10.399888 -6.67456,0 -12.573,-2.561167 -12.573,-10.710332 V 45.155576 H 143.8237 v 33.21755 c 0,16.531164 11.25361,22.584834 26.77583,22.584834 z",
       "m 210.97135,99.483345 h 47.49799 l 0.46567,-12.02972 H 225.09657 V 77.286571 H 251.1739 V 65.877739 h -26.07733 v -8.692443 h 32.82949 l -0.54328,-12.02972 h -46.41143 z",
       "m 296.97834,43.680965 c -18.62666,0 -30.42355,11.175998 -30.42355,28.638495 0,17.462498 11.79689,28.6385 30.42355,28.6385 7.99394,0 14.82372,-2.173115 20.10128,-6.208892 l 11.9521,7.993942 h 0.0776 V 89.316291 l -4.96711,-3.414888 c 2.17311,-3.958166 3.33727,-8.614832 3.33727,-13.581943 0,-17.462497 -11.79688,-28.638495 -30.50116,-28.638495 z m 0.31045,12.417776 c 10.39988,0 16.37594,6.208887 16.37594,16.375941 0,2.328333 -0.31045,4.423833 -0.85372,6.2865 l -13.89239,-9.002888 -6.2865,9.002888 13.58194,8.381998 c -2.40594,1.241778 -5.43278,1.940278 -8.92527,1.940278 -10.4775,0 -16.45356,-6.441722 -16.45356,-16.608776 0,-10.167054 5.97606,-16.375941 16.45356,-16.375941 z",
       "m 365.21243,100.95796 c 15.44461,0 26.93106,-6.05367 26.93106,-22.895278 V 45.155576 h -14.20284 v 32.596661 c 0,7.993943 -5.97605,10.399888 -12.65061,10.399888 -6.67455,0 -12.57299,-2.561167 -12.57299,-10.710332 V 45.155576 H 338.4366 v 33.21755 c 0,16.531164 11.25361,22.584834 26.77583,22.584834 z",
       "m 405.58425,99.483345 h 47.49799 l 0.46567,-12.02972 H 419.70947 V 77.286571 H 445.7868 V 65.877739 h -26.07733 v -8.692443 h 32.82949 l -0.54328,-12.02972 h -46.41143 z"
    ]
    for (var path_i=0; path_i<paths_trueque.length;path_i++){
      path = paths_trueque[path_i]
      console.log(path_i)
      create_path(
        canvas,
        {
          d:path,
          transform:`translate(1000,1000)`,
          class:"carousel_segment"
        }
      )
    }
  }
}









function init() {
  canvas = document.getElementById( "top_level" );
  var background_rectangle = create_rectangle(canvas,{id:"background_rect"})
  interface.mode_title = create_text(canvas, "MODE: WAITING_FOR_CONNECTIONS", {class:"title_text",id:"mode_title"})
  interface.high_power_title = create_text(canvas, "HIGH POWER: OFF", {class:"title_text",id:"high_power_title"})
  interface.carousel_panel = new Carousel_Panel([1850,1200],canvas);

  hostmap = {
    controller:{
      rpi:new Status_Block(canvas, [block_grid_x[11],block_grid_y[1]], "RPi CONTROLLER", ["df","temp","pin git","tb git"]),
      nucleo:new Status_Block(canvas, [block_grid_x[10],block_grid_y[1]], "NUCLEO BOARD", ["connected"]),
      amps:new Amps_Block(canvas, [block_grid_x[6],block_grid_y[20]], "SOLENOID AMPS", 0)
    },
    pinball1game:{
      rpi:new Status_Block(canvas, [block_grid_x[0],block_grid_y[2]], "RPi PINBALL 1", ["df","temp","pin git","tb git"]),
      p3_roc:new Status_Block(canvas, [block_grid_x[0],block_grid_y[3]], "P3 ROC 1", ["connected"]),
      amps:new Amps_Block(canvas, [block_grid_x[0],block_grid_y[1]], "GAME 1 AMPS", 0),
    },
    pinball2game:{
      rpi:new Status_Block(canvas, [block_grid_x[1],block_grid_y[2]], "RPi PINBALL 2", ["df","temp","pin git","tb git"]),
      p3_roc:new Status_Block(canvas, [block_grid_x[1],block_grid_y[3]], "P3 ROC 2", ["connected"]),
      amps:new Amps_Block(canvas, [block_grid_x[1],block_grid_y[1]], "GAME 2 AMPS", 0),
    },
    pinball3game:{
      rpi:new Status_Block(canvas, [block_grid_x[2],block_grid_y[2]], "RPi PINBALL 3", ["df","temp","pin git","tb git"]),
      p3_roc:new Status_Block(canvas, [block_grid_x[2],block_grid_y[3]], "P3 ROC 3", ["connected"]),
      amps:new Amps_Block(canvas, [block_grid_x[2],block_grid_y[1]], "GAME 3 AMPS", 0),
    },
    pinball4game:{
      rpi:new Status_Block(canvas, [block_grid_x[3],block_grid_y[2]], "RPi PINBALL 4", ["df","temp","pin git","tb git"]),
      p3_roc:new Status_Block(canvas, [block_grid_x[3],block_grid_y[3]], "P3 ROC 4", ["connected"]),
      amps:new Amps_Block(canvas, [block_grid_x[3],block_grid_y[1]], "GAME 4 AMPS", 0),
    },
    pinball5game:{
      rpi:new Status_Block(canvas, [block_grid_x[4],block_grid_y[2]], "RPi PINBALL 5", ["df","temp","pin git","tb git"]),
      p3_roc:new Status_Block(canvas, [block_grid_x[4],block_grid_y[3]], "P3 ROC 5", ["connected"]),
      amps:new Amps_Block(canvas, [block_grid_x[4],block_grid_y[1]], "GAME 5 AMPS", 0),
    },
    pinball1display:{
      rpi:new Status_Block(canvas, [block_grid_x[13],block_grid_y[2]], "RPi DISPLAY 1", ["df","temp","pin git","tb git"]),
      hc595_1:new Status_Block(canvas, [block_grid_x[13],block_grid_y[3]], "HC595 1", ["connected"]),
      amps:new Amps_Block(canvas, [block_grid_x[13],block_grid_y[1]], "DISPLAY AMPS", 0),
    },
    pinball2display:{
      rpi:new Status_Block(canvas, [block_grid_x[14],block_grid_y[2]], "RPi DISPLAY 2", ["df","temp","pin git","tb git"]),
      hc595_1:new Status_Block(canvas, [block_grid_x[14],block_grid_y[3]], "HC595 2", ["connected"]),
    },
    pinball3display:{
      rpi:new Status_Block(canvas, [block_grid_x[15],block_grid_y[2]], "RPi DISPLAY 3", ["df","temp","pin git","tb git"]),
      hc595_1:new Status_Block(canvas, [block_grid_x[15],block_grid_y[3]], "HC595 3", ["connected"]),
    },
    pinball4display:{
      rpi:new Status_Block(canvas, [block_grid_x[16],block_grid_y[2]], "RPi DISPLAY 4", ["df","temp","pin git","tb git"]),
      hc595_1:new Status_Block(canvas, [block_grid_x[16],block_grid_y[3]], "HC595 4", ["connected"]),
    },
    pinball5display:{
      rpi:new Status_Block(canvas, [block_grid_x[17],block_grid_y[2]], "RPi DISPLAY 5", ["df","temp","pin git","tb git"]),
      hc595_1:new Status_Block(canvas, [block_grid_x[17],block_grid_y[3]], "HC595 5", ["connected"]),
    },
    pinballmatrix:{
      rpi:new Status_Block(canvas, [block_grid_x[6],block_grid_y[2]], "RPi MATRIX", ["df","temp","pin git","tb git"]),
      sdc_1_2: new Status_Block(canvas, [block_grid_x[6],block_grid_y[3]], "SDC2160  1 & 2", ["faults"]),
      sdc_3_4: new Status_Block(canvas, [block_grid_x[8],block_grid_y[3]], "SDC2160  3 & 4", ["faults"]),
      sdc_5_6: new Status_Block(canvas, [block_grid_x[10],block_grid_y[3]], "SDC2160  5 & 6", ["faults"]),
      amt_1: new Status_Block(canvas, [block_grid_x[6],block_grid_y[6]], "AMT203 1", ["θ relative","θ absolute","discrepancy"]),
      amt_2: new Status_Block(canvas, [block_grid_x[7],block_grid_y[6]], "AMT203 2", ["θ relative","θ absolute","discrepancy"]),
      amt_3: new Status_Block(canvas, [block_grid_x[8],block_grid_y[6]], "AMT203 3", ["θ relative","θ absolute","discrepancy"]),
      amt_4: new Status_Block(canvas, [block_grid_x[9],block_grid_y[6]], "AMT203 4", ["θ relative","θ absolute","discrepancy"]),
      amt_5: new Status_Block(canvas, [block_grid_x[10],block_grid_y[6]], "AMT203 5", ["θ relative","θ absolute","discrepancy"]),
      amt_6: new Status_Block(canvas, [block_grid_x[11],block_grid_y[6]], "AMT203 CENTER", ["θ relative","θ absolute","discrepancy"]),
      carousel_1 :new Status_Block(canvas, [block_grid_x[6],block_grid_y[4]], "MOTOR 1", ["amps","temp","pid error","status","stall","θ target"]),
      carousel_2 :new Status_Block(canvas, [block_grid_x[7],block_grid_y[4]], "MOTOR 2", ["amps","temp","pid error","status","stall","θ target"]),
      carousel_3 :new Status_Block(canvas, [block_grid_x[8],block_grid_y[4]], "MOTOR 3", ["amps","temp","pid error","status","stall","θ target"]),
      carousel_4 :new Status_Block(canvas, [block_grid_x[9],block_grid_y[4]], "MOTOR 4", ["amps","temp","pid error","status","stall","θ target"]),
      carousel_5 :new Status_Block(canvas, [block_grid_x[10],block_grid_y[4]], "MOTOR 5", ["amps","temp","pid error","status","stall","θ target"]),
      carousel_center :new Status_Block(canvas, [block_grid_x[11],block_grid_y[4]], "MOTOR CENTER", ["amps","temp","pid error","status","stall","θ target"]),
      amps:new Amps_Block(canvas, [block_grid_x[6],block_grid_y[1]], "MOTORS AMPS", 0),
    },
    carousel1:{
      rpi:new Status_Block(canvas, [block_grid_x[6],block_grid_y[19]], "RPi CAROUSEL 1", ["df","temp","pin git","tb git"]),
    },
    carousel2:{
      rpi:new Status_Block(canvas, [block_grid_x[7],block_grid_y[19]], "RPi CAROUSEL 2", ["df","temp","pin git","tb git"]),
    },
    carousel3:{
      rpi:new Status_Block(canvas, [block_grid_x[8],block_grid_y[19]], "RPi CAROUSEL 3", ["df","temp","pin git","tb git"]),
    },
    carousel4:{
      rpi:new Status_Block(canvas, [block_grid_x[9],block_grid_y[19]], "RPi CAROUSEL 4", ["df","temp","pin git","tb git"]),
    },
    carousel5:{
      rpi:new Status_Block(canvas, [block_grid_x[10],block_grid_y[19]], "RPi CAROUSEL 5", ["df","temp","pin git","tb git"]),
    },
    carouselcenter:{
      rpi:new Status_Block(canvas, [block_grid_x[11],block_grid_y[19]], "RPi CAROUSEL CENTER", ["df","temp","pin git","tb git"]),
    },
  }
}
