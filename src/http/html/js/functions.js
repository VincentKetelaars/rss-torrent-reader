$('#check-all').click(function() {
    $(".checkbox").prop('checked', this.checked);
});
$('.save-button').click(function() {
	var formData = $('#save-form').serializeArray();
  	formData.push({ name: this.name, value: this.value });
	$.post($(this).attr('action'), formData, function(response){
		console.debug(response);
	    alert(response.message);
	},'json');
	return false;
});