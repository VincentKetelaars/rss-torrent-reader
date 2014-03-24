$('#check-all').click(function() {
    $(".checkbox").prop('checked', this.checked);
});

$('#configuration-show-button').click(function() {
	var formData = $('#configuration-file-form').serializeArray();
  	formData.push({ name: this.name, value: this.value });
	$.post($(this).attr('action'), formData, function(response){
		$("#configuration-content").replaceWith(response.div);
	},'json');
	return false;
});
$('#configuration-file-button').click(function() {
	var formData = $('#configuration-file-form').serializeArray();
  	formData.push({ name: this.name, value: this.value });
	$.post($(this).attr('action'), formData, function(response){
		console.debug(response);
	    alert(response.message);
	},'json');
	return false;
});
$('.save-button').click(function() {
	var formData = $('#save-form').serializeArray();
  	formData.push({ name: this.name, value: this.value });
  	formData.push({ name: $('#configuration-file-input').attr("name"), 
  		value: $('#configuration-file-input').attr("value")});
	$.post($(this).attr('action'), formData, function(response){
		console.debug(response);
	    alert(response.message);
	},'json');
	return false;
});

function add_input_element(me, ename) {
	$(me).parent().append($('<input></input>').attr({type : "text", size : 50, name : ename}));
	$(me).parent().append($('</br>'));
	$(me).parent().append($('<input></input>').attr({type : "image", height : 20, width : 20, 
		src : "pics/add.png", onclick : "return add_input_element(this, 'feed')"}));
	$(me).attr("src", "pics/remove.jpg");
	$(me).attr("onclick", "return remove_input_element(this)");
	return false;
};

function remove_input_element(me) {
	$(me).next().remove(); // Remove the input
	$(me).next().remove(); // Remove </br>
	$(me).remove(); // Remove titself
	return false;
};

function add_imdb_input(me) {
	$(me).parent().append($('<label>URL</label>'));
	$(me).parent().append($('<input></input>').attr({type : "text", size : 50, name : "url"}));
	$(me).parent().append($('</br>'));
	$(me).parent().append($('<label>Username</label>'));
	$(me).parent().append($('<input></input>').attr({type : "text", size : 30, name : "user"}));
	$(me).parent().append($('</br>'));
	$(me).parent().append($('<label>Password</label>'));
	$(me).parent().append($('<input></input>').attr({type : "password", size : 30, name : "pass"}));
	$(me).parent().append($('</br>'));
	$(me).parent().append($('<input></input>').attr({type : "image", height : 20, width : 20, 
		src : "pics/add.png", onclick : "return add_imdb_input(this)"}));
	$(me).attr("src", "pics/remove.jpg");
	$(me).attr("onclick", "return remove_imdb_input(this)");
	return false;
};

function remove_imdb_input(me) {
	while ($(me).next().length && !$(me).next().attr("src")) {
		$(me).next().remove();
	}
	$(me).remove(); // Remove itself
	return false;
};

$('#handler_adder').click(function() {
	var formData = $('#handler_selector, #configuration-file-form').serializeArray();
	$.post($(this).attr('action'), formData, function(response){
		$("#handlers").append(response.div);
	},'json');
	return false;
});

function remove_handler(me) {
	// Remove the entire div directly
	$(me).parent().parent().remove(); // The grandparent should be the handler div..
	return false;
};