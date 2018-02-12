var blueState = false;
var redState = false;;
var overrideState = false;
var steerState = false;

$(document).ready(function(){
	// Hides controls, as the the "override" instructino hasn't been made yet	
	$("#btn_override").click(function(){
		$(this).toggleClass("active");
		$(".controls").toggle("slow","swing");
		overrideState = !overrideState;
		// Posts button state to server
		$.get("/control?control=override&value=" + overrideState);
	});
	$("#blue_led").click(function(){
		$(this).toggleClass("active");
		blueState = !blueState;
		// Posts button state to server
		$.get("/control?control=blueLED&value=" + blueState);
	});
	$("#red_led").click(function(){
		$(this).toggleClass("active");
		redState = !redState;
		// Posts button state to server
		$.get("/control?control=redLED&value=" + redState)
	});	
	$("#btn_steer").click(function(){
		$(this).toggleClass("active");
		steerState = !steerState;
		}
	);
	$("#tbl_refresh").click(function(){
		$.get("/table",function(data,status){
			$(".dataTable").html(data);
		})			
	})
	// Detects arrow key presses
	$(document).keydown(function(event){
		if(steerState){
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
				
				default: break;
			}
			event.preventDefault(); // prevent the default action (scroll / move caret)
		}
	})
	
	$(document).keyup(function(event){
		if(steerState){
			switch(event.which){
				case 37: // left
				$.get("/control?control=left&value=false")
				break;
				
				case 38: // up
				$.get("/control?control=up&value=false")
				break;
				
				case 39: // right
				$.get("/control?control=right&value=false")
				break;
				
				case 40: // down
				$.get("/control?control=down&value=false")
				break;
				
				default: break;
			}
			event.preventDefault(); // prevent the default action (scroll / move caret)
		}
	})
});

