function toggle_hide_completed() {
	var a = $("#hidecompleted");
	var is_hidden = eval(a.data("hidden"));
	if (is_hidden) {
		$("li[class=completed]").each(function(){
			$(this).fadeIn()
		});
		a.data("hidden", false);
		a.html("Hide completed challenges");
	}
	else {
		$("li[class=completed]").each(function(){
			$(this).fadeOut()
		});
		a.data("hidden", true);
		a.html("Unhide completed challenges");
	}
}

function toggle_prefs() {
	if ($("#prefwindow").is(":hidden")) {
		$("#prefwindow").fadeIn();
	} else {
		$("#prefwindow").fadeOut();
	}
}

function update_session_button() {
	is_hidden = $("#hidecompleted").data("hidden");
	if (is_hidden) {
		a.html("Unhide completed challenges");
	} else {
		a.html("Hide completed challenges");
	}
}
