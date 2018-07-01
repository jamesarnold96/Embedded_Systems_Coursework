/*JavaScript/JQuery code to implement event handling from when
the user interacts with the "My Vehicle" website. This
sends HTTP "GET" instructions to a Python/Bottle server, 
which then sends the instructions to the bug. This allows 
the user to control the bug remotely.*/

// State of blue LED control button
var blueState = false;
// State of red LED control button
var redState = false;
// State of override button
var overrideState = false;
// Does script listen for keyboard inputs?
var steerState = false;
var up = false;
var right = false;
var left = false;
// Minimum and maximum duty cycle values accepted by the servo
var duty_min = 21;
var duty_max = 93;

$(document).ready(function(){
    // Sends the "override" instruction to the bug, which causes the default 
    // behavior to stop, allowing control by the user. 
    $("#btn_override").click(function(){
        $(this).toggleClass("active");
        // Displays the bug controls to the user 
        $(".controls").toggle("slow","swing");
        overrideState = !overrideState;
        // Posts button state to server
        $.get("/control?control=override&value=" + overrideState);
    });
    $("#blue_led").click(function(){
        // Sends an instruction to turn on/off the blue LED
        $(this).toggleClass("active");
        blueState = !blueState;
        // Posts button state to server
        $.get("/control?control=blueLED&value=" + blueState);
    });
    // Sends an instruction to turn on/off the red LED
    $("#red_led").click(function(){
        $(this).toggleClass("active");
        redState = !redState;
        // Posts button state to server
        $.get("/control?control=redLED&value=" + redState)
    };    
    // Sends an instruction to control the angle of the servo motor 
    // (containing the lux sensor)
    $("#btn_servo").click(function(){
        value=$("#servo").val();
        // Posts button state to server
        $.get("/control?control=servo&value=" + value);
        $("#servo").val("");
    });    
    // Listens out for key press inputs to steer the bug
    $("#btn_steer").click(function(){
        $(this).toggleClass("active");
        steerState = !steerState;
        }
    );
    // Instructs the server to draw a table containing the last 20 data points
    // (stored in sensorData.json)
    $("#tbl_refresh").click(function(){
        $.get("/table",function(data,status){
            // Displays the server response (a "table" HTML element)
            $(".dataTable").html(data); 
        })            
    })
    // Detects document closing (to remove override)
    $(window).on("beforeunload", function(){
        $.get("/control?control=override&value=false");
    });
    // Detects arrow key presses to steer the bug
    $(document).keydown(function(event){
        if(steerState){
            event.preventDefault(); // prevent the default action (scroll / move caret)
            switch(event.which){
                case 37: // left
                    if(!left){
                      $.get("/control?control=left&value=true");
                    }
                    left = true;
                    break;
                
                case 38: // up
                    if(!up){
                      $.get("/control?control=up&value=true");
                    }
                    up = true;
                    break;
                
                case 39: // right
                    if(!right){
                      $.get("/control?control=right&value=true")
                    }
                    right = true;
                    break;
                
                default: break;
            }
        }
    })
    
    // Detects when the key is released to stop steering the bug
    $(document).keyup(function(event){
        if(steerState){
            switch(event.which){
                case 37: // left
                    if(left){
                      $.get("/control?control=left&value=false")
                    }
                    left = false;
                            break;
                            
                            case 38: // up
                    if(up){
                      $.get("/control?control=up&value=false")
                    }
                    up = false;
                    break;
                
                case 39: // right
                    if(right){
                      $.get("/control?control=right&value=false")
                    }
                    right = false;
                    break;
                
                default: break;
            }
            // prevent the default action (scroll / move caret)
            event.preventDefault(); 
        }
    })
});

