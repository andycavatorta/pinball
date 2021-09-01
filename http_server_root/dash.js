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
    var topic_data = JSON.parse(evt.data);
    // console.log("New Websocket Message")
    //console.log(topic_data)
    var action = topic_data[0]
    var target = topic_data[1]

    var hostname = target[0]
    var device = target[1]
    var data_name = target[2]
    var data_value = target[3]
    switch (action) {
      case "update_status":

          console.log("action>>>>>>",action);
          console.log("hostname>>>>>>",hostname);
          console.log("device>>>>>>",device);
          console.log("data_name>>>>>>",data_name);
          console.log("data_value>>>>>>",data_value);
        if (data_value == "status_absent"){
          hostmap[hostname][device].background_rectangle.setAttribute("class","theme_absent");
        }
        if (data_value == "status_present"){
          hostmap[hostname][device].background_rectangle.setAttribute("class","theme_present");
        }
        if (data_value == "status_nominal"){
          hostmap[hostname][device].background_rectangle.setAttribute("class","theme_nominal");
        }
        if (data_value == "status_fault"){
          hostmap[hostname][device].background_rectangle.setAttribute("class","theme_fault");
        }
        break;
      case "update_value":
        if (device == "amps"){
          hostmap[hostname][device].set_value(data_value);
        }else{

          hostmap[hostname][device].set_value(data_name, data_value);
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
        height: `${(line_height*(this.names.length+1))}px`,
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
  }
  set_ball_presence(carousel_id, fruit_id, ball_b){
    this.carousels[carousel_id].set_ball_presence(fruit_id,ball_b);
  }
  set_carousel_angle(carousel_id, deg){
    this.carousels[carousel_id].set_angle(deg);
  }
  // more methods to follow
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
      motor_1 :new Status_Block(canvas, [block_grid_x[6],block_grid_y[4]], "MOTOR 1", ["amps","temp","pid error","status","stall","θ target"]),
      motor_2 :new Status_Block(canvas, [block_grid_x[7],block_grid_y[4]], "MOTOR 2", ["amps","temp","pid error","status","stall","θ target"]),
      motor_3 :new Status_Block(canvas, [block_grid_x[8],block_grid_y[4]], "MOTOR 3", ["amps","temp","pid error","status","stall","θ target"]),
      motor_4 :new Status_Block(canvas, [block_grid_x[9],block_grid_y[4]], "MOTOR 4", ["amps","temp","pid error","status","stall","θ target"]),
      motor_5 :new Status_Block(canvas, [block_grid_x[10],block_grid_y[4]], "MOTOR 5", ["amps","temp","pid error","status","stall","θ target"]),
      motor_6 :new Status_Block(canvas, [block_grid_x[11],block_grid_y[4]], "MOTOR CENTER", ["amps","temp","pid error","status","stall","θ target"]),
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
