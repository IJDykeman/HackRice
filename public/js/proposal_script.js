/**
 * Created by pgirardet on 1/31/2015.
 */
$(document).ready(function(){
    $( "#events" ).accordion();
    $(".btn.btn-success.btn-sm").click(function(){

        $(this).replaceWith("<div align='right'><a href='#' class='btn btn-down btn-sm'>I'm down</a></div>");
    });
});