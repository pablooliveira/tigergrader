function display_data(data) {
    alert('here');
    $("div#grades").append(JSON.stringify(data, null, 2));
}

function wait_for_update() {
    $.ajax({ type: 'GET',
             url: '/grades',
             success:  display_data,        
             complete: wait_for_update,  
             timeout:  1000
           });    
}

$(document).ready(function() {
    $("div#grades").append("awaiting data...\n");
    wait_for_update();
});
        
