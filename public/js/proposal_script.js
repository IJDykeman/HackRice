/**
 * Created by pgirardet on 1/31/2015.
 */
$(document).ready(function(){
    $( "#events" ).accordion();
    $('#events.success-button').click(function(){

        (this).replaceWith("<a href='#' class='btn btn-danger'>Danger</a>");

    });
});