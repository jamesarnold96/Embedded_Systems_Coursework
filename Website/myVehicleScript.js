var blueState = false;
var redState = false;;
var overrideState = false;
var steerState = false;

$(document).ready(function(){
	$("#btn_override").click(function(){
		$(this).toggleClass("active");
		overrideState = !overrideState;
		// Posts button state to server
	$.get("/control?control=override&value=" + buttonOverride,function(data,status){
			alert("Data: " + data + "\nStatus: " + status);
			})
		}
	);
	$("#blue_led").click(function(){
		$(this).toggleClass("active");
		buttonStateBlue = !buttonStateBlue;
		// Posts button state to server
		$.get("/control?control=blueLED&value=" + blueState,function(data,status){
			alert("Data: " + data + "\nStatus: " + status);
			})
		}
	);
	$("#red_led").click(function(){
		$(this).toggleClass("active");
		buttonStateRed = !buttonStateRed;
		// Posts button state to server
		$.get("/control?control=redLED&value=" + redState,function(data,status){
			alert("Data: " + data + "\nStatus: " + status);
			})
		}
	);
	
	$("#red_led").click(function(){
		$(this).toggleClass("active");
		steerState = !steerState;
		}
	);
	// Detects arrow key presses
	$(document).keypress(function(event){
		if(steerState)
			switch(event.which){
				case 37: // left
				$.get("/control?control=left&value=true")
				break;
				
				case 38: // up
				$.get("/control?control=up&value=true")
				break;
				
				case 39: // right
				$.get("/control?control=up&value=true")
				break;
				
				case 40: // down
				$.get("/control?control=down&value=true")
				break;
				
				default: return;
			})
	)
	
	$(document).keyup(function(event){
		if(steerState)
			switch(event.which){
				case 37: // left
				$.get("/control?control=left&value=false")
				break;
				
				case 38: // up
				$.get("/control?control=up&value=false")
				break;
				
				case 39: // right
				$.get("/control?control=up&value=false")
				break;
				
				case 40: // down
				$.get("/control?control=down&value=false")
				break;
				
				default: return;
			})
	)
});

