function store() {
	data = "";
	for (i = 0; i < 50; i++) {
		if($("#cb"+i).is(":checked")) {
			data += i+",";
		}
	}
	r = new XMLHttpRequest();
	r.onreadystatechange=function(){
		if(r.readyState==4 && r.status==200) {
			$("#responsediv").html(r.responseText);	
			$("#responsediv").fadeIn().delay(1500).fadeOut()
		}
	}
	r.open("POST", "store", true);
	r.send(data)
}
