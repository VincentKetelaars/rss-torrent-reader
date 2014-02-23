$('#check-all').click(function() {
    $(".checkbox").prop('checked', this.checked);
});
function configuration_form() {
	var formData = $('#configuration-file-form').serializeArray();
  	formData.push({ name: this.name, value: this.value });
	$.post($(this).attr('action'), formData, function(response){
		console.debug(response);
	    alert(response.message);
	},'json');
	return false;
}
$('#configuration-show-button').click(configuration_form);
$('#configuration-file-button').click(configuration_form);
$('.save-button').click(function() {
	var formData = $('#save-form').serializeArray();
  	formData.push({ name: this.name, value: this.value });
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